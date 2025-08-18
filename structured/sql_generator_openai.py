# structured/sql_generator.py
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

OPENAI_MODEL = "gpt-4o-mini"   # fast + cost-effective; change to "gpt-4o" if you want higher accuracy

PROMPT_TEMPLATE = """
You are a precise SQL generator for PostgreSQL.

Return ONLY a valid JSON object in this exact structure:
{{"sql": "...", "params": [...]}}

Rules:
1. "sql" must be a safe, read-only SELECT query using only numbered placeholders ($1, $2, ...). 
   Never use variable names like $HR.
   Always avoid grouping by unique identifiers when searching for the maximum. 
   When asked for the single record with the maximum value, use ORDER BY ... DESC LIMIT 1.

2. Use only syntactically valid PostgreSQL.
3. If you use a WITH clause, it must define a valid CTE:
   WITH cte_name AS (
       SELECT ...
   )
   SELECT ... FROM cte_name ...
4. Do not include any comments, explanations, or markdown formatting — only the JSON object.
5. If unsure, return exactly: {{"sql": "", "params": []}}

Schema:
{schema_description}

Example:
User: Get total sales per region for 2023.
Output:
{{"sql": "SELECT region, SUM(total) AS total_sales FROM orders WHERE EXTRACT(YEAR FROM order_date) = $1 GROUP BY region", "params": ["2023"]}}

User: {question}
Output:
"""

def generate_sql(schema_description, question, max_tokens=256):
    prompt = PROMPT_TEMPLATE.format(schema_description=schema_description, question=question)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a precise SQL generator for PostgreSQL."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0
    )

    res = response.choices[0].message.content.strip()

    # --- Force JSON extraction ---
    start, end = res.find("{"), res.rfind("}")
    sql, params = "", []
    if start != -1 and end != -1:
        try:
            parsed = json.loads(res[start:end+1])
            sql = parsed.get("sql", "").strip()
            params = parsed.get("params", [])
        except json.JSONDecodeError:
            return "", []

    # --- Fix bad placeholders like $HR or $60000 ---
    literal_param_pattern = r"\$([A-Za-z0-9_]+)"
    bad_matches = re.findall(literal_param_pattern, sql)

    if bad_matches:
        fixed_params = []
        placeholder_count = 1
        for match in bad_matches:
            try:
                val = int(match)  # numeric param
            except ValueError:
                val = match       # string param
            fixed_params.append(val)
            sql = re.sub(rf"\${re.escape(match)}", f"${placeholder_count}", sql, count=1)
            placeholder_count += 1

        if not params:
            params = fixed_params

    return sql, params
