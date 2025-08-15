# structured/sql_generator.py
import json
import os
os.environ["HF_HOME"] = "D:/huggingface"


# from transformers import pipeline

# HF_MODEL = "HuggingFaceH4/zephyr-7b-beta"
# generator = pipeline("text-generation", model=HF_MODEL, device=-1)

import subprocess
import json

OLLAMA_MODEL = "sqlcoder:7b"

def ollama_generate(prompt):
    """Run a local Ollama model and return its text output."""
    result = subprocess.run(
        ["ollama", "run", OLLAMA_MODEL],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        raise RuntimeError(f"Ollama error: {result.stderr.decode()}")
    return result.stdout.decode("utf-8")



PROMPT_TEMPLATE = """
You are a precise SQL generator for PostgreSQL.

Return ONLY a valid JSON object in this exact structure:
{{"sql": "...", "params": [...]}}

Rules:
1. "sql" must be a safe, read-only SELECT query using only numbered placeholders ($1, $2, ...). Never use variable names like $HR.
 "sql": must use numbered placeholders ($1, $2, ...) for ANY dynamic value — never insert raw values directly.
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






# def generate_sql(schema_description, question, max_new_tokens=256):
#     prompt = PROMPT_TEMPLATE.format(schema_description=schema_description, question=question)

#     res = generator(
#         prompt,
#         max_new_tokens=max_new_tokens,
#         truncation=True,
#         do_sample=False  # Deterministic
#     )[0]["generated_text"].strip()

#     # Force JSON extraction
#     start, end = res.find("{"), res.rfind("}")
#     if start != -1 and end != -1:
#         try:
#             parsed = json.loads(res[start:end+1])
#             return parsed.get("sql", "").strip(), parsed.get("params", [])
#         except json.JSONDecodeError:
#             pass

#     return "", []
import json
import re

def generate_sql(schema_description, question, max_new_tokens=256):
    prompt = PROMPT_TEMPLATE.format(schema_description=schema_description, question=question)
    res = ollama_generate(prompt).strip()

    # Force JSON extraction
    start, end = res.find("{"), res.rfind("}")
    sql, params = "", []
    if start != -1 and end != -1:
        try:
            parsed = json.loads(res[start:end+1])
            sql = parsed.get("sql", "").strip()
            params = parsed.get("params", [])
        except json.JSONDecodeError:
            return "", []

    # --- FIX 1: Replace literal values with $ placeholders if needed ---
    # Match cases like $60000, $HR etc.
    literal_param_pattern = r"\$([A-Za-z0-9_]+)"
    bad_matches = re.findall(literal_param_pattern, sql)

    if bad_matches:
        fixed_params = []
        placeholder_count = 1
        for match in bad_matches:
            # Try converting to int if numeric, else keep as string
            try:
                val = int(match)
            except ValueError:
                val = match
            fixed_params.append(val)
            # Replace each bad placeholder with proper $n
            sql = re.sub(rf"\${re.escape(match)}", f"${placeholder_count}", sql, count=1)
            placeholder_count += 1

        # If original params are empty, use our fixed ones
        if not params:
            params = fixed_params

    return sql, params

