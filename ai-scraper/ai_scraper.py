# Import the Streamlit library - this is what we use to create the web interface
import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from langchain_core.documents import Document
import logging

# Import various tools from LangChain that help us work with AI and documents
from langchain_community.document_loaders import SeleniumURLLoader  # Loads web pages
from langchain_text_splitters import RecursiveCharacterTextSplitter  # Splits text into smaller chunks
from langchain_core.vectorstores import InMemoryVectorStore  # Stores documents for searching
from langchain_ollama import OllamaEmbeddings  # Converts text to numbers (embeddings) for AI to understand
from langchain_core.prompts import ChatPromptTemplate  # Creates templates for asking questions to AI
from langchain_ollama.llms import OllamaLLM  # The actual AI model that answers questions

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# This is a template that tells the AI how to answer questions
# It gives the AI instructions and placeholders for the question and context
template = """
You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. 
Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""

# Create an embeddings model - this converts text into numbers that AI can understand
# Think of it like translating human words into AI language
embeddings = OllamaEmbeddings(model="llama3.2")

# Create a vector store - this is like a smart database that can find similar documents
# It stores the converted text (embeddings) in memory for quick searching
vector_store = InMemoryVectorStore(embeddings)

# Create the AI model that will answer our questions
model = OllamaLLM(model="llama3.2")

def load_page(url):
    logger.info(f"load_page start: {url}")
    """
    This function takes a website URL and loads the content from that webpage.
    It uses Selenium (a web browser automation tool) to visit the page and get all the text.
    Now uses a 120s timeout and a Chrome user agent to avoid bot detection and slow loads.
    """
    # Set up Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Create the driver
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(120)  # Set timeout to 120 seconds

    try:
        driver.get(url)
        time.sleep(2)  # Wait for JS to load, adjust as needed
        content = driver.page_source
        # Return as a list of Document objects for compatibility
        logger.info(f"load_page end: {url}")
        return [Document(page_content=content, metadata={"source": url})]
    except Exception as e:
        st.warning(f"Error loading {url}: {e}")
        logger.info(f"load_page end (error): {url}")
        return []
    finally:
        driver.quit()

def split_text(documents):
    logger.info("split_text start")
    """
    This function takes large documents and splits them into smaller pieces.
    This is important because AI models can only handle a certain amount of text at once.
    """
    # Create a text splitter that breaks documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # Each chunk will be about 1000 characters
        chunk_overlap=200,    # Chunks will overlap by 200 characters to maintain context
        add_start_index=True  # Keep track of where each chunk came from in the original text
    )
    # Split the documents into smaller pieces
    data = text_splitter.split_documents(documents)
    logger.info("split_text end")
    return data

def index_docs(documents):
    logger.info("index_docs start")
    """
    This function takes the split documents and adds them to our vector store.
    The vector store will convert them to embeddings and make them searchable.
    """
    vector_store.add_documents(documents)
    logger.info("index_docs end")

def retrieve_docs(query):
    logger.info("retrieve_docs start")
    """
    This function takes a question and finds the most relevant document chunks.
    It uses similarity search to find text that's most related to the question.
    """
    result = vector_store.similarity_search(query)
    logger.info("retrieve_docs end")
    return result

def answer_question(question, context):
    logger.info("answer_question start")
    """
    This function takes a question and relevant context, then asks the AI to answer.
    It uses our template to format the question properly for the AI.
    """
    # Create a prompt template using our predefined template
    prompt = ChatPromptTemplate.from_template(template)
    # Connect the prompt template to our AI model
    chain = prompt | model
    # Ask the AI the question with the provided context
    result = chain.invoke({"question": question, "context": context})
    logger.info("answer_question end")
    return result

# ===== STREAMLIT WEB INTERFACE =====
# This section creates the user interface that people will see in their browser

# Create a title for our web app
st.title("AI Crawler")

# Option 1: Text area for multiple URLs
urls_input = st.text_area("Enter URLs (one per line):")

# Option 2: CSV upload for URLs
uploaded_file = st.file_uploader("Or upload a CSV file with a column named 'url'", type=["csv"])

url_list = []
if urls_input:
    url_list = [url.strip() for url in urls_input.splitlines() if url.strip()]
elif uploaded_file:
    df = pd.read_csv(uploaded_file)
    if 'url' in df.columns:
        url_list = df['url'].dropna().tolist()
    else:
        st.warning("CSV must have a column named 'url'.")

# Only process if we have at least one URL
if url_list:
    all_documents = []
    with st.spinner(f"Loading and processing {len(url_list)} URLs..."):
        for url in url_list:
            try:
                docs = load_page(url)
                all_documents.extend(docs)
            except Exception as e:
                st.warning(f"Failed to load {url}: {e}")
    chunked_documents = split_text(all_documents)
    index_docs(chunked_documents)
    st.success(f"Processed {len(url_list)} URLs!")

    # Create a chat input box where users can ask questions
    question = st.chat_input()

    # When a question is asked:
    if question:
        # Display the user's question in the chat
        st.chat_message("user").write(question)
        
        # Find the most relevant document chunks for this question
        retrieve_documents = retrieve_docs(question)
        
        # Combine all the relevant chunks into one piece of context
        context = "\n\n".join([doc.page_content for doc in retrieve_documents])
        
        # Ask the AI to answer the question using the found context
        answer = answer_question(question, context)
        
        # Display the AI's answer in the chat
        st.chat_message("assistant").write(answer)
else:
    st.info("Enter at least one URL (or upload a CSV) to get started.")



