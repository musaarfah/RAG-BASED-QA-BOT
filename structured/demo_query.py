# structured/demo_sql_query.py
from structured.schema_loader import load_schema_yaml, schema_to_description
from structured.sql_generator import generate_sql
from structured.query_runner import run_query
import json

# paths
SCHEMA_FILE = "structured/example_schema.yaml"

# PostgreSQL connection parameters
PG_CONFIG = {
    "host": "localhost",      # or your DB host
    "port": 5432,              # default PostgreSQL port
    "dbname": "company_db", # change this to your DB name
    "user": "postgres",   # change this to your username
    "password": "4321" # change this to your password
}

schema = load_schema_yaml(SCHEMA_FILE)
schema_desc = schema_to_description(schema)

# question = "Employees whose name start with A"


# sql, params = generate_sql(schema_desc, question)
# print("Generated SQL:", sql)
# print("Params:", params)

# if sql:
#     rows = run_query(sql, params, PG_CONFIG)  # pass PG_CONFIG instead of DB_FILE
#     print("Rows:", json.dumps(rows, indent=2))
# else:
#     print("No SQL generated.")
