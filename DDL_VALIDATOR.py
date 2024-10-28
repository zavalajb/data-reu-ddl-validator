import re
import argparse
import os
from collections import defaultdict

def parse_ddl_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"El archivo {filepath} no existe.")

    with open(filepath, 'r') as file:
        ddl_content = file.read()
    return ddl_content

def extract_table_definitions(ddl_content):
    table_pattern = re.compile(r'CREATE TABLE\s+(\w+)\s*\((.*?)\);', re.S)
    column_pattern = re.compile(r'(\w+)\s+([\w\(\)]+)\s*(.*?)(?:,|$)', re.S)
    primary_key_pattern = re.compile(r'PRIMARY KEY\s*\((.*?)\)')
    foreign_key_pattern = re.compile(r'FOREIGN KEY\s*\((.*?)\)\s*REFERENCES\s+(\w+)\s*\((.*?)\)')

    tables = {}

    for table_match in table_pattern.finditer(ddl_content):
        table_name = table_match.group(1)
        columns_section = table_match.group(2)

        columns = []
        primary_key = None
        foreign_keys = []

        for column_match in column_pattern.finditer(columns_section):
            column_name = column_match.group(1)
            data_type = column_match.group(2)
            constraints = column_match.group(3)

            if "PRIMARY KEY" in constraints:
                primary_key = column_name
            if "FOREIGN KEY" in constraints:
                continue

            columns.append({
                'name': column_name,
                'data_type': data_type,
                'constraints': constraints
            })

        primary_key_match = primary_key_pattern.search(columns_section)
        if primary_key_match:
            primary_key = primary_key_match.group(1).strip()

        for foreign_key_match in foreign_key_pattern.finditer(columns_section):
            fk_column = foreign_key_match.group(1).strip()
            referenced_table = foreign_key_match.group(2).strip()
            referenced_column = foreign_key_match.group(3).strip()
            foreign_keys.append((fk_column, referenced_table, referenced_column))

        tables[table_name] = {
            'columns': columns,
            'primary_key': primary_key,
            'foreign_keys': foreign_keys
        }

    return tables

def analyze_tables(tables):
    report = []

    for table_name, table_info in tables.items():
        primary_key = table_info['primary_key']
        foreign_keys = table_info['foreign_keys']

        if not primary_key:
            report.append((f"Table '{table_name}' does not have a primary key defined.", "error"))

        if not foreign_keys:
            possible_fks = [col['name'] for col in table_info['columns'] if 'id' in col['name'].lower() or 'fk' in col['name'].lower() or 'ref' in col['name'].lower()]
            if not possible_fks:
                report.append((f"Table '{table_name}' has no foreign key relationships detected, explicit or implicit.", "warning"))
            else:
                report.append((f"Table '{table_name}' has possible foreign key columns: {', '.join(possible_fks)} but no explicit foreign key constraint is defined.", "warning"))
        else:
            for fk_column, ref_table, ref_column in foreign_keys:
                if ref_table not in tables:
                    report.append((f"Foreign key column '{fk_column}' in table '{table_name}' references non-existent table '{ref_table}'.", "error"))
                elif ref_column not in [col['name'] for col in tables[ref_table]['columns']]:
                    report.append((f"Foreign key column '{fk_column}' in table '{table_name}' references non-existent column '{ref_column}' in table '{ref_table}'.", "error"))

        for col in table_info['columns']:
            if col['name'] == primary_key or any(fk_col[0] == col['name'] for fk_col in foreign_keys):
                if 'INDEX' not in col['constraints'].upper():
                    report.append((f"Key column '{col['name']}' in table '{table_name}' is not indexed.", "warning"))

        if len(foreign_keys) > 1:
            fk_columns = [fk[0] for fk in foreign_keys]
            if primary_key not in fk_columns and primary_key:
                report.append((f"Table '{table_name}' may have a cardinality issue: it has multiple foreign keys but the primary key is not a composite of these foreign keys. This could be a many-to-many relationship incorrectly modeled as one-to-many.", "warning"))

        if foreign_keys:
            if len(foreign_keys) == 1:
                report.append((f"Table '{table_name}' seems to have a one-to-many relationship with table '{foreign_keys[0][1]}'.", "info"))
            elif len(foreign_keys) > 1:
                report.append((f"Table '{table_name}' may have a many-to-many relationship or an incorrect FK setup.", "warning"))

    return report

def generate_report(report, output_format='text'):
    if output_format == 'html':
        html_report = """
        <html>
            <head>
                <title>DDL Analysis Report</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f9;
                        color: #333;
                        margin: 0;
                        padding: 20px;
                    }
                    h1 {
                        text-align: center;
                        color: #333;
                        margin-bottom: 20px;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                    }
                    .message {
                        border-radius: 5px;
                        padding: 15px;
                        margin-bottom: 10px;
                        border-left: 6px solid;
                    }
                    .error {
                        background-color: #ffe6e6;
                        border-color: #e63946;
                        color: #e63946;
                    }
                    .warning {
                        background-color: #fff4e6;
                        border-color: #ffba08;
                        color: #ffba08;
                    }
                    .info {
                        background-color: #e6f7ff;
                        border-color: #0077b6;
                        color: #0077b6;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>DDL Analysis Report</h1>
                    <div>
        """

        for entry, severity in report:
            css_class = severity
            html_report += f"<div class='message {css_class}'><strong>{severity.capitalize()}:</strong> {entry}</div>"

        html_report += """
                    </div>
                </div>
            </body>
        </html>
        """
        return html_report
    else:
        return "\n".join(f"{entry} ({severity.upper()})" for entry, severity in report)

def main():
    parser = argparse.ArgumentParser(description='Analyze DDL file for table structure and constraints.')
    parser.add_argument('filepath', help='The full path to the DDL file including the filename')
    parser.add_argument('--output', choices=['text', 'html'], default='text', help='Output format for the report (default: text)')

    args = parser.parse_args()

    ddl_content = parse_ddl_file(args.filepath)
    tables = extract_table_definitions(ddl_content)
    report = analyze_tables(tables)

    report_output = generate_report(report, args.output)

    if args.output == 'html':
        with open('ddl_analysis_report.html', 'w') as file:
            file.write(report_output)
        print("Report generated: ddl_analysis_report.html")
    else:
        print(report_output)

if __name__ == '__main__':
    main()
