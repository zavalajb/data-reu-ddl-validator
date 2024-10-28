import re
import argparse
import os
from collections import defaultdict

# Función que obtiene el archivo DDL desde una ruta específica incluyendo el nombre del archivo
def parse_ddl_file(filepath):
    # Verifica si el archivo existe
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"El archivo {filepath} no existe.")

    with open(filepath, 'r') as file:
        ddl_content = file.read()
    return ddl_content

def extract_table_definitions(ddl_content):
    # Regex patterns to capture CREATE TABLE definitions and constraints
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

        # Extract column definitions
        for column_match in column_pattern.finditer(columns_section):
            column_name = column_match.group(1)
            data_type = column_match.group(2)
            constraints = column_match.group(3)

            if "PRIMARY KEY" in constraints:
                primary_key = column_name
            if "FOREIGN KEY" in constraints:
                # Ignore inline foreign keys for now, we'll handle explicit ones later
                continue

            columns.append({
                'name': column_name,
                'data_type': data_type,
                'constraints': constraints
            })

        # Extract constraints like PRIMARY KEY and FOREIGN KEY
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
    indexes = defaultdict(list)

    for table_name, table_info in tables.items():
        primary_key = table_info['primary_key']
        foreign_keys = table_info['foreign_keys']

        # Check for primary key
        if not primary_key:
            report.append(f"Table '{table_name}' does not have a primary key defined.")

        # Analyze foreign key relationships
        if not foreign_keys:
            # Try to infer relationships based on column names
            possible_fks = [col['name'] for col in table_info['columns'] if 'id' in col['name'].lower() or 'fk' in col['name'].lower() or 'ref' in col['name'].lower()]
            if not possible_fks:
                report.append(f"Table '{table_name}' has no foreign key relationships detected, explicit or implicit.")
            else:
                report.append(f"Table '{table_name}' has possible foreign key columns: {', '.join(possible_fks)} but no explicit foreign key constraint is defined.")
        else:
            for fk_column, ref_table, ref_column in foreign_keys:
                if ref_column not in [col['name'] for col in tables[ref_table]['columns']]:
                    report.append(f"Foreign key column '{fk_column}' in table '{table_name}' references non-existent column '{ref_column}' in table '{ref_table}'.")

        # Check if primary and foreign key columns are indexed
        for col in table_info['columns']:
            if col['name'] == primary_key or any(fk_col[0] == col['name'] for fk_col in foreign_keys):
                if 'INDEX' not in col['constraints'].upper():
                    report.append(f"Key column '{col['name']}' in table '{table_name}' is not indexed.")

        # Detect many-to-many relationships (table with composite PK of FKs)
        if len(foreign_keys) > 1:
            fk_columns = [fk[0] for fk in foreign_keys]
            # Check if the primary key is composed of both foreign keys
            if primary_key not in fk_columns and primary_key:
                report.append(f"Table '{table_name}' may have a cardinality issue: it has multiple foreign keys but the primary key is not a composite of these foreign keys. This could be a many-to-many relationship incorrectly modeled as one-to-many.")

        # Detect one-to-one or one-to-many relationships based on FK definitions
        if foreign_keys:
            if len(foreign_keys) == 1:
                report.append(f"Table '{table_name}' seems to have a one-to-many relationship with table '{foreign_keys[0][1]}'.")
            elif len(foreign_keys) > 1:
                report.append(f"Table '{table_name}' may have a many-to-many relationship or an incorrect FK setup.")

    return report

def generate_report(report, output_format='text'):
    if output_format == 'html':
        html_report = "<html><head><title>DDL Analysis Report</title></head><body><h1>DDL Analysis Report</h1><ul>"
        for entry in report:
            html_report += f"<li>{entry}</li>"
        html_report += "</ul></body></html>"
        return html_report
    else:
        return "\n".join(report)

def main():
    # Argument parser for command line inputs
    parser = argparse.ArgumentParser(description='Analyze DDL file for table structure and constraints.')
    parser.add_argument('filepath', help='The full path to the DDL file including the filename')
    parser.add_argument('--output', choices=['text', 'html'], default='text', help='Output format for the report (default: text)')

    args = parser.parse_args()

    # Parse and analyze the DDL file
    ddl_content = parse_ddl_file(args.filepath)
    tables = extract_table_definitions(ddl_content)
    report = analyze_tables(tables)

    # Generate the report
    report_output = generate_report(report, args.output)

    # Output the report
    if args.output == 'html':
        with open('ddl_analysis_report.html', 'w') as file:
            file.write(report_output)
        print("Report generated: ddl_analysis_report.html")
    else:
        print(report_output)

if __name__ == '__main__':
    main()
