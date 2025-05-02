import json
import re

import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from sqlalchemy import create_engine, inspect

db_url = "sqlite:///testdb.sqlite"

template = """
You are a SQL generator.  When given a schema and a user question, you MUST output only the SQL statement—nothing else.  No explanation is needed.

Schema: {schema}
User question: {query}
Output (SQL only):
"""

model = OllamaLLM(model="deepseek-r1:8b")

def extract_schema(db_url):
    engine = create_engine(db_url)
    inspector = inspect(engine)
    schema = {}

    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)
        schema[table] = [col['name'] for col in columns]

    return json.dumps(schema)

def to_sql_query(query, schema):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    return clean_text(chain.invoke({"query": query, "schema": schema}))

def clean_text(text: str):
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()

schema = extract_schema(db_url)
query = st.text_area("Describe the data you want to retrieve from the database:")

if query:
    sql = to_sql_query(query, schema)
    st.code(sql, wrap_lines=True, language="sql")



