import json
import re

import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from sqlalchemy import create_engine, inspect

# Configuration
db_url = "sqlite:///testdb.sqlite"

template = """
You are a SQL generator.  
When given a schema and a user question, you MUST output only the SQL statement — nothing else. 
No explanation is needed.

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

# Streamlit UI Configuration
st.set_page_config(
    page_title="Text to SQL Generator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e86c1;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .sample-prompt {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 5px 5px 0;
    }
    .database-info {
        background-color: #000000;
        color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #333333;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<div class="main-header">🔍 Text to SQL Generator</div>', unsafe_allow_html=True)

# Sidebar with Database Information
with st.sidebar:
    st.markdown('<div class="section-header">📊 Database Overview</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="database-info">
    <h4>testdb.sqlite Structure</h4>
    
    <b>📁 Tables:</b>
    <ul>
        <li><b>users</b> - Customer information (3 records)</li>
        <li><b>orders</b> - Order records with status (5 records)</li>
        <li><b>items</b> - Individual order items (7 records)</li>
    </ul>
    
    <b>🔗 Relationships:</b><br>
    users → orders → items
    
    <b>📈 Order Statuses:</b>
    <ul>
        <li>pending</li>
        <li>shipped</li>
        <li>delivered</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">💡 Sample Prompts</div>', unsafe_allow_html=True)
    
    sample_prompts = [
        "Find all orders with status 'shipped'",
        "Get all users and their order counts",
        "Show all items in orders with status 'delivered'",
        "Find the total value of all orders for each user",
        "List all orders by user 'Alice' with their items",
        "Get the most expensive items in the database",
        "Show orders that have more than one item",
        "Find users who have placed orders with 'pending' status"
    ]
    
    for i, prompt in enumerate(sample_prompts, 1):
        if st.button(f"📝 {prompt}", key=f"prompt_{i}", use_container_width=True):
            st.session_state.selected_prompt = prompt

# Main content area
st.markdown('<div class="section-header">✍️ Describe Your Query</div>', unsafe_allow_html=True)

# Initialize session state for the query
if 'selected_prompt' not in st.session_state:
    st.session_state.selected_prompt = ""

# Text area for user input
query = st.text_area(
    "What data would you like to retrieve from the database?",
    value=st.session_state.selected_prompt,
    height=100,
    placeholder="Example: Find all orders with status 'shipped' and their items..."
)

# Submit button
submit_button = st.button("🚀 Generate SQL", type="primary", use_container_width=True)

# Clear button
if st.button("🗑️ Clear", use_container_width=True):
    st.session_state.selected_prompt = ""
    st.rerun()

# Generate and display SQL when submit button is clicked or query is provided
if (submit_button and query) or (query and st.session_state.get('auto_generate', False)):
    with st.spinner("🤖 Generating SQL query..."):
        try:
            schema = extract_schema(db_url)
            sql = to_sql_query(query, schema)
            
            st.markdown('<div class="section-header">📝 Generated SQL Query</div>', unsafe_allow_html=True)
            st.code(sql, language="sql", line_numbers=True)
            
            # Option to copy the SQL
            st.download_button(
                label="💾 Download SQL",
                data=sql,
                file_name="generated_query.sql",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"❌ Error generating SQL: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "💡 **Tip:** Use the sample prompts in the sidebar to get started, or describe your data needs in natural language!"
)



