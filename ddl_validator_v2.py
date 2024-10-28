import re
from dataclasses import dataclass
from typing import List, Dict, Set, Optional
import sqlparse

@dataclass
class Column:
    name: str
    data_type: str
    constraints: List[str]
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references_table: Optional[str] = None
    references_column: Optional[str] = None

@dataclass
class Table:
    name: str
    columns: Dict[str, Column]
    primary_keys: List[str]

class SQLSchemaAnalyzer:
    def __init__(self):
        self.tables: Dict[str, Table] = {}
        self.errors: List[str] = []

    def parse_schema(self, sql_schema: str) -> None:
        # Parse and normalize the SQL schema
        statements = sqlparse.split(sql_schema)
        print(statements)
        for statement in statements:
            parsed = sqlparse.parse(statement)[0]
            if parsed.get_type() == 'CREATE':
                self._parse_create_table(statement)

    def _parse_create_table(self, create_statement: str) -> None:
        # Extract table name
        table_name_match = re.search(r'SELECT (\w+)', create_statement, re.IGNORECASE)
        if not table_name_match:
            return
        
        table_name = table_name_match.group(1).lower()
        columns: Dict[str, Column] = {}
        primary_keys: List[str] = []

        # Extract column definitions
        column_defs = re.findall(r'(\w+)\s+([\w()]+)([^,]+)?', create_statement)
        
        for col_name, data_type, constraints in column_defs:
            col_name = col_name.lower()
            constraints_list = self._parse_constraints(constraints)
            
            is_primary_key = any('PRIMARY KEY' in c.upper() for c in constraints_list)
            is_foreign_key = any('FOREIGN KEY' in c.upper() for c in constraints_list)
            
            references = None
            references_column = None
            
            if is_foreign_key:
                ref_match = re.search(r'REFERENCES\s+(\w+)\s*\((\w+)\)', constraints, re.IGNORECASE)
                if ref_match:
                    references = ref_match.group(1).lower()
                    references_column = ref_match.group(2).lower()

            columns[col_name] = Column(
                name=col_name,
                data_type=data_type,
                constraints=constraints_list,
                is_primary_key=is_primary_key,
                is_foreign_key=is_foreign_key,
                references_table=references,
                references_column=references_column
            )
            
            if is_primary_key:
                primary_keys.append(col_name)

        # Check for table-level PRIMARY KEY constraint
        pk_match = re.search(r'PRIMARY KEY\s*\(([^)]+)\)', create_statement, re.IGNORECASE)
        if pk_match:
            pk_columns = [col.strip().lower() for col in pk_match.group(1).split(',')]
            primary_keys.extend(pk_columns)

        self.tables[table_name] = Table(name=table_name, columns=columns, primary_keys=primary_keys)

    def _parse_constraints(self, constraints: str) -> List[str]:
        if not constraints:
            return []
        return [c.strip() for c in constraints.split() if c.strip()]

    def analyze(self) -> List[str]:
        self.errors = []
        
        for table_name, table in self.tables.items():
            self._check_primary_key(table)
            self._check_foreign_keys(table)
            self._check_naming_consistency(table)

        return self.errors

    def _check_primary_key(self, table: Table) -> None:
        if not table.primary_keys:
            self.errors.append(f"Table '{table.name}' has no PRIMARY KEY defined")

    def _check_foreign_keys(self, table: Table) -> None:
        for col_name, column in table.columns.items():
            if column.is_foreign_key:
                if not column.references_table or not column.references_column:
                    self.errors.append(f"Foreign key '{col_name}' in table '{table.name}' does not properly specify referenced table and column")
                elif column.references_table not in self.tables:
                    self.errors.append(f"Foreign key '{col_name}' in table '{table.name}' references non-existent table '{column.references_table}'")
                elif column.references_table in self.tables:
                    referenced_table = self.tables[column.references_table]
                    if column.references_column not in referenced_table.columns:
                        self.errors.append(f"Foreign key '{col_name}' in table '{table.name}' references non-existent column '{column.references_column}' in table '{column.references_table}'")
                    elif column.references_column not in referenced_table.primary_keys:
                        self.errors.append(f"Foreign key '{col_name}' in table '{table.name}' references non-primary key column '{column.references_column}' in table '{column.references_table}'")

    def _check_naming_consistency(self, table: Table) -> None:
        for col_name, column in table.columns.items():
            if column.is_foreign_key and not col_name.endswith('_id'):
                referenced_table = column.references_table
                self.errors.append(f"Inconsistent foreign key naming: '{col_name}' in table '{table.name}' should be named '{referenced_table}_id'")

def analyze_sql_schema(sql_schema: str) -> List[str]:
    analyzer = SQLSchemaAnalyzer()
    analyzer.parse_schema(sql_schema)
    return analyzer.analyze()

# Example usage
def main():
    # Example schema or read from file
    filepath = "DDL_Muestra.sql"
    with open(filepath, 'r') as file:
        ddl_content = file.read()
    #sample_schema = """
    #CREATE TABLE users (
    #    user_id INT NOT NULL,
    #    username VARCHAR(50) NOT NULL UNIQUE,
    #    PRIMARY KEY (user_id)
    #);

    #CREATE TABLE orders (
    #    order_id INT NOT NULL,
    #    user INT NOT NULL,
    #    PRIMARY KEY (order_id)
    #);
    #"""
   #print(ddl_content)
    errors = analyze_sql_schema(ddl_content)
    for error in errors:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()