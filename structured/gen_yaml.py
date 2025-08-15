import psycopg2
import yaml

PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "company_db",
    "user": "postgres",
    "password": "4321"
}

conn = psycopg2.connect(**PG_CONFIG)
cur = conn.cursor()

cur.execute("""
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
""")

schema_data = {}
for table, column, col_type in cur.fetchall():
    if table not in schema_data:
        schema_data[table] = []
    schema_data[table].append({"name": column, "type": col_type})

yaml_schema = {
    "tables": [
        {
            "name": table,
            "description": "",
            "columns": cols
        }
        for table, cols in schema_data.items()
    ]
}

with open("structured/example_schema.yaml", "w") as f:
    yaml.dump(yaml_schema, f, sort_keys=False)

print("YAML schema saved to structured/example_schema.yaml")

cur.close()
conn.close()
