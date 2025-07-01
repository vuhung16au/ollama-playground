import streamlit as st
import pandas as pd
from langchain_ollama import OllamaLLM
from langchain_experimental.agents import create_pandas_dataframe_agent
import io
import os

# Page configuration
st.set_page_config(
    page_title="Chat with Data - Streamlit",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.sample-prompt {
    background-color: #f0f2f6;
    padding: 10px;
    border-radius: 5px;
    border-left: 4px solid #1f77b4;
    margin: 5px 0;
    cursor: pointer;
}
.sample-prompt:hover {
    background-color: #e8eaf6;
}
.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
}
.user-message {
    background-color: #2d3748;
    color: #ffffff;
    border-left: 4px solid #1f77b4;
}
.assistant-message {
    background-color: #4a5568;
    color: #ffffff;
    border-left: 4px solid #4caf50;
}
</style>
""", unsafe_allow_html=True)

def initialize_ollama_llm(model_name="mistral"):
    """Initialize Ollama LLM"""
    try:
        llm = OllamaLLM(model=model_name)
        return llm
    except Exception as e:
        st.error(f"Error initializing Ollama LLM. Make sure Ollama server is running and '{model_name}' model is pulled. Error: {e}")
        return None

def create_dataframe_agent(llm, df):
    """Create pandas dataframe agent"""
    try:
        agent = create_pandas_dataframe_agent(
            llm, 
            df, 
            verbose=True, 
            allow_dangerous_code=True
        )
        return agent
    except Exception as e:
        st.error(f"Error creating Pandas DataFrame Agent: {e}")
        return None

def get_sample_prompts(df):
    """Generate sample prompts based on the dataset columns"""
    columns = df.columns.tolist()
    
    # Generic prompts that work with most datasets
    generic_prompts = [
        "Show me the first 10 rows of the dataset",
        "What are the column names and data types?",
        "How many rows and columns are in this dataset?",
        "Are there any missing values in the dataset?",
        "Show me basic statistics of numerical columns"
    ]
    
    # Specific prompts for Online Retail dataset
    retail_prompts = []
    if 'Country' in columns:
        retail_prompts.extend([
            "What are the top 5 countries by number of transactions?",
            "Which country has the highest total sales value?"
        ])
    
    if 'UnitPrice' in columns and 'Quantity' in columns:
        retail_prompts.extend([
            "Calculate the total revenue (UnitPrice * Quantity) for each country",
            "What is the average order value?"
        ])
    
    if 'Description' in columns:
        retail_prompts.extend([
            "What are the top 10 most popular products?",
            "Show me products that contain the word 'HEART' in their description"
        ])
    
    if 'InvoiceDate' in columns:
        retail_prompts.extend([
            "Show sales trends by month",
            "What day of the week has the highest sales?"
        ])
    
    if 'CustomerID' in columns:
        retail_prompts.extend([
            "How many unique customers are there?",
            "Which customers have made the most purchases?"
        ])
    
    return generic_prompts + retail_prompts

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Chat with Data - Streamlit</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        model_name = st.selectbox(
            "Select Ollama Model",
            options=["mistral", "llama2", "codellama", "gemma"],
            index=0,
            help="Make sure the selected model is pulled in Ollama"
        )
        
        # Reset agent if model changes
        if 'current_model' not in st.session_state:
            st.session_state.current_model = model_name
        elif st.session_state.current_model != model_name:
            st.session_state.current_model = model_name
            st.session_state.agent = None
            st.info(f"Model changed to {model_name}. Agent will be reinitialized.")
        
        st.markdown("---")
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. Upload a CSV file or use the default OnlineRetail.csv
        2. Wait for the data to load and agent to initialize
        3. Try the sample prompts or ask your own questions
        4. Make sure Ollama server is running locally
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Ollama Setup")
        st.code("ollama serve", language="bash")
        st.code(f"ollama pull {model_name}", language="bash")
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    # File upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload your CSV file to start chatting with your data"
        )
    
    with col2:
        st.subheader("📊 Use Sample Data")
        use_sample = st.button(
            "Load OnlineRetail.csv",
            help="Load the default OnlineRetail dataset"
        )
    
    # Load data
    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Uploaded file loaded successfully! Shape: {df.shape}")
        except Exception as e:
            st.error(f"Error loading uploaded file: {e}")
    elif use_sample:
        sample_path = "data/OnlineRetail.csv"
        if os.path.exists(sample_path):
            try:
                df = pd.read_csv(sample_path)
                st.success(f"✅ Sample data loaded successfully! Shape: {df.shape}")
            except Exception as e:
                st.error(f"Error loading sample data: {e}")
        else:
            st.error("Sample data file not found. Please upload your own CSV file.")
    
    # Display data info and initialize agent
    if df is not None:
        st.session_state.df = df
        
        # Display data preview
        with st.expander("📋 Data Preview", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**First 5 rows:**")
                st.dataframe(df.head())
            with col2:
                st.write("**Dataset Info:**")
                buffer = io.StringIO()
                df.info(buf=buffer)
                info_str = buffer.getvalue()
                st.text(info_str)
        
        # Initialize LLM and agent
        if st.session_state.agent is None:
            with st.spinner("🤖 Initializing Ollama LLM and creating agent..."):
                llm = initialize_ollama_llm(model_name)
                if llm is not None:
                    agent = create_dataframe_agent(llm, df)
                    if agent is not None:
                        st.session_state.agent = agent
                        st.success("✅ Agent initialized successfully!")
                    else:
                        st.error("❌ Failed to create agent")
                        st.info("Please check if Ollama is running and the model is available.")
                else:
                    st.error("❌ Failed to initialize LLM")
                    st.info("Please check if Ollama is running and the model is available.")
        
        # Sample prompts section
        if st.session_state.agent is not None:
            st.subheader("💡 Sample Prompts")
            st.write("Click on any prompt below to execute it immediately:")
            
            sample_prompts = get_sample_prompts(df)
            
            # Display prompts in columns
            cols = st.columns(2)
            for i, prompt in enumerate(sample_prompts):
                col = cols[i % 2]
                with col:
                    if st.button(prompt, key=f"prompt_{i}", use_container_width=True):
                        # Execute immediately and add to history
                        try:
                            with st.spinner("🤔 Thinking..."):
                                response = st.session_state.agent.invoke({"input": prompt})
                                
                                # Add to chat history
                                st.session_state.chat_history.append({
                                    "question": prompt,
                                    "answer": response.get('output', 'No output found.')
                                })
                                
                                st.success(f"✅ Executed: {prompt}")
                                
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
                            st.info("Please try rephrasing your question or check the Ollama server status.")
        
        # Chat interface
        if st.session_state.agent is not None:
            st.markdown("---")
            st.subheader("💬 Chat with Your Data")
            
            # Question input
            question = st.text_input(
                "Ask a question about your data:",
                value="",
                placeholder="E.g., What are the top 5 products by sales?",
                key="question_input"
            )
            
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                ask_button = st.button("🚀 Ask", type="primary")
            with col2:
                clear_button = st.button("🗑️ Clear Chat")
            
            if ask_button and question.strip():
                # Execute immediately
                try:
                    with st.spinner("🤔 Thinking..."):
                        response = st.session_state.agent.invoke({"input": question.strip()})
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "question": question.strip(),
                            "answer": response.get('output', 'No output found.')
                        })
                        
                        st.success(f"✅ Executed: {question.strip()}")
                        
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.info("Please try rephrasing your question or check the Ollama server status.")
            
            if clear_button:
                st.session_state.chat_history = []
                st.success("🗑️ Chat history cleared!")
            
            # Display chat history
            if st.session_state.chat_history:
                st.markdown("### 📜 Chat History")
                for i, chat in enumerate(reversed(st.session_state.chat_history)):
                    with st.container():
                        # User message
                        st.markdown(f"""
                        <div class="chat-message user-message">
                            <strong>🧑 You:</strong><br>
                            {chat['question']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Assistant message
                        st.markdown(f"""
                        <div class="chat-message assistant-message">
                            <strong>🤖 Assistant:</strong><br>
                            {chat['answer'].replace('\n', '<br>')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if i < len(st.session_state.chat_history) - 1:
                            st.markdown("---")
    
    else:
        # Welcome message when no data is loaded
        st.info("👆 Please upload a CSV file or click 'Load OnlineRetail.csv' to get started!")
        
        # Show example of what the app can do
        st.subheader("🎯 What can this app do?")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📊 Data Analysis**
            - Explore your dataset
            - Get statistical summaries
            - Find patterns and trends
            """)
        
        with col2:
            st.markdown("""
            **🤖 Natural Language Queries**
            - Ask questions in plain English
            - Get code-generated answers
            - Interactive data exploration
            """)
        
        with col3:
            st.markdown("""
            **🚀 Powered by Ollama**
            - Local LLM processing
            - Privacy-focused
            - Customizable models
            """)

if __name__ == "__main__":
    main()
