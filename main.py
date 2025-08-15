import streamlit as st
from unstructured.query_bot import retrieve, generate_answer
from structured.sql_generator import generate_sql
from structured.query_runner import run_query
from structured.schema_loader import load_schema_yaml, schema_to_description
from structured.demo_query import PG_CONFIG  # Postgres config

# Schema file for structured mode
SCHEMA_FILE = "structured/example_schema.yaml"

# Page Config
st.set_page_config(page_title="RAG Document & SQL Bot", page_icon="📚", layout="wide")

# App title
st.title("📚 RAG Document & SQL Bot")
st.write("Ask questions about uploaded documents **or** query structured databases.")

# Sidebar
st.sidebar.header("Settings")
mode = st.sidebar.selectbox("Mode", ["Unstructured", "Structured"])
st.sidebar.markdown("---")

# ============================
# UNSTRUCTURED MODE
# ============================
if mode == "Unstructured":
    top_k = st.sidebar.slider("Number of Chunks (Top K)", min_value=1, max_value=10, value=3)

    question = st.text_input("❓ Enter your question:")

    if st.button("Get Answer") and question.strip():
        with st.spinner("Retrieving answer..."):
            results = retrieve(question, k=top_k)
            answer = generate_answer(question, results)

            st.subheader("💡 Answer:")
            st.write(answer)

            with st.expander("📚 Retrieved Chunks & Sources"):
                for r in results:
                    st.markdown(f"**Source:** `{r['source']}`  — *Distance:* `{r['distance']:.4f}`")
                    st.write(r["text"])
                    st.markdown("---")

# ============================
# STRUCTURED MODE
# ============================
elif mode == "Structured":
    st.subheader("💾 Structured Query Mode")

    # Load schema from YAML
    schema_dict = load_schema_yaml(SCHEMA_FILE)
    schema_desc = schema_to_description(schema_dict)

    question = st.text_area("📝 Enter your request:")

    if st.button("Run SQL") and question.strip():
        with st.spinner("Generating SQL..."):
            sql, params = generate_sql(schema_desc, question)

        if not sql:
            st.error("No SQL could be generated for your question.")
        else:
            st.code(sql, language="sql")
            st.write("**Params:**", params)

            try:
                with st.spinner("Running query..."):
                    rows = run_query(sql, params, PG_CONFIG)
                st.success(f"Retrieved {len(rows)} rows.")
                st.dataframe(rows)
            except Exception as e:
                st.error(f"Query failed: {e}")
