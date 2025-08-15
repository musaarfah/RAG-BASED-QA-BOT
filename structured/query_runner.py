# structured/query_runner.py
import json
import re
import psycopg2
import psycopg2.extras

# optional strong parser
try:
    import sqlglot
    SQLGLOT_AVAILABLE = True
except Exception:
    SQLGLOT_AVAILABLE = False

FORBIDDEN = ["insert ", "update ", "delete ", "drop ", "alter ", "create ", ";", "--"]

def simple_validate_select(sql):
    s = sql.strip().lower()
    if not s.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
    for kw in FORBIDDEN:
        if kw in s:
            raise ValueError(f"Forbidden token in SQL: {kw}")
    return True

def validate_sql_ast(sql):
    if SQLGLOT_AVAILABLE:
        try:
            tree = sqlglot.parse_one(sql, read="postgres")
            from sqlglot.expressions import Select
            if tree is None:
                raise ValueError("Could not parse SQL")
            if not isinstance(tree, Select) and not tree.find(Select):
                raise ValueError("Only SELECT queries are allowed.")
            return True
        except Exception as e:
            raise ValueError(f"SQL parse error: {e}")
    else:
        return simple_validate_select(sql)

def run_query(sql, params, db_config, limit=1000):
    """
    Executes a parameterized SELECT safely against PostgreSQL.
    db_config should be a dict: 
        {
            "dbname": "your_db",
            "user": "your_user",
            "password": "your_password",
            "host": "localhost",
            "port": 5432
        }
    """
    # Validate query is safe
    validate_sql_ast(sql)

    # Count placeholders BEFORE replacing
    placeholder_matches = re.findall(r"\$\d+", sql)
    num_placeholders = len(set(placeholder_matches))

    if num_placeholders != len(params or []):
        raise ValueError(
            f"Mismatch: SQL expects {num_placeholders} params but got {len(params or [])}: {params}"
        )

    # Convert $1, $2... style placeholders to psycopg2's %s
    sql = re.sub(r"\$\d+", "%s", sql)

    # Enforce a LIMIT for safety (if not already in query)
    if "limit" not in sql.lower():
        sql = sql.rstrip("; ") + f" LIMIT {limit}"

    # Connect to Postgres
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        print("DEBUG running query:", sql)
        print("DEBUG params:", params, type(params))
        # Count %s placeholders AFTER replacement
        placeholder_count = sql.count("%s")
        if placeholder_count != len(params or []):
            raise ValueError(
                f"SQL expects {placeholder_count} placeholders but got {len(params or [])} params: {params}"
                )

        cur.execute(sql, params or None)


        rows = cur.fetchall()
    finally:
        conn.close()

    return rows

