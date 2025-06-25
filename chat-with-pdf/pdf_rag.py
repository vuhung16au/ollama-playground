import streamlit as st
import logging
from datetime import datetime
import re

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_rag.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Streamlit page configuration
st.set_page_config(
    page_title="Chat with PDF",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False
if "current_pdf" not in st.session_state:
    st.session_state.current_pdf = None
if "documents" not in st.session_state:
    st.session_state.documents = []
if "chunked_documents" not in st.session_state:
    st.session_state.chunked_documents = []

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""

pdfs_directory = 'pdfs/'

model = 'deepseek-r1:8b'

embeddings = OllamaEmbeddings(model=model)
vector_store = InMemoryVectorStore(embeddings)

llm = OllamaLLM(model=model)

def upload_pdf(file):
    logger.info(f"Starting upload_pdf function for file: {file.name}")
    try:
        with open(pdfs_directory + file.name, "wb") as f:
            f.write(file.getbuffer())
        logger.info(f"Successfully uploaded PDF: {file.name}")
    except Exception as e:
        logger.error(f"Error uploading PDF {file.name}: {str(e)}")
        raise
    logger.info(f"Completed upload_pdf function for file: {file.name}")

def load_pdf(file_path):
    logger.info(f"Starting load_pdf function for file: {file_path}")
    try:
        loader = PDFPlumberLoader(file_path)
        documents = loader.load()
        logger.info(f"Successfully loaded PDF with {len(documents)} pages: {file_path}")
        return documents
    except Exception as e:
        logger.error(f"Error loading PDF {file_path}: {str(e)}")
        raise
    finally:
        logger.info(f"Completed load_pdf function for file: {file_path}")

def split_text(documents):
    logger.info(f"Starting split_text function for {len(documents)} documents")
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )
        split_docs = text_splitter.split_documents(documents)
        logger.info(f"Successfully split documents into {len(split_docs)} chunks")
        return split_docs
    except Exception as e:
        logger.error(f"Error splitting documents: {str(e)}")
        raise
    finally:
        logger.info("Completed split_text function")

def index_docs(documents):
    logger.info(f"Starting index_docs function for {len(documents)} documents")
    try:
        vector_store.add_documents(documents)
        logger.info(f"Successfully indexed {len(documents)} documents to vector store")
    except Exception as e:
        logger.error(f"Error indexing documents: {str(e)}")
        raise
    finally:
        logger.info("Completed index_docs function")

def retrieve_docs(query):
    logger.info(f"Starting retrieve_docs function for query: {query[:50]}...")
    try:
        results = vector_store.similarity_search(query)
        logger.info(f"Successfully retrieved {len(results)} documents for query")
        return results
    except Exception as e:
        logger.error(f"Error retrieving documents for query '{query}': {str(e)}")
        raise
    finally:
        logger.info("Completed retrieve_docs function")

def answer_question(question, documents):
    logger.info(f"Starting answer_question function for question: {question[:50]}...")
    try:
        context = "\n\n".join([doc.page_content for doc in documents])
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        
        logger.info(f"Generated context from {len(documents)} documents")
        answer = chain.invoke({"question": question, "context": context})
        
        # Remove <think> tags from reasoning models like DeepSeek
        if isinstance(answer, str):
            # Remove everything between <think> and </think> tags
            answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL)
            # Clean up any extra whitespace left behind
            answer = answer.strip()
        
        # Add source information
        sources = []
        for i, doc in enumerate(documents):
            if hasattr(doc, 'metadata') and 'page' in doc.metadata:
                sources.append(f"Page {doc.metadata['page'] + 1}")
            else:
                sources.append(f"Chunk {i+1}")
        
        logger.info("Successfully generated answer")
        return {
            "answer": answer,
            "sources": sources,
            "context_used": len(documents)
        }
    except Exception as e:
        logger.error(f"Error answering question '{question}': {str(e)}")
        raise
    finally:
        logger.info("Completed answer_question function")

# Main Streamlit App
st.title("📄 Chat with PDF")
st.markdown("Upload a PDF document and ask questions about its content!")

# Sidebar for PDF Information and Controls
with st.sidebar:
    st.header("📋 Document Information")
    
    # File upload with validation
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type="pdf",
        accept_multiple_files=False,
        help="Upload a PDF file (max 10MB)"
    )
    
    # File validation
    if uploaded_file:
        if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
            st.error("🚫 File too large! Please upload a PDF smaller than 10MB.")
            st.stop()
        
        if not uploaded_file.name.lower().endswith('.pdf'):
            st.error("🚫 Please upload a valid PDF file.")
            st.stop()
        
        # Check if it's a new file
        if st.session_state.current_pdf != uploaded_file.name:
            st.session_state.current_pdf = uploaded_file.name
            st.session_state.pdf_processed = False
            st.session_state.messages = []  # Clear chat history for new PDF
            st.session_state.documents = []
            st.session_state.chunked_documents = []
        
        # Display file information
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
        
        # Process PDF if not already processed
        if not st.session_state.pdf_processed:
            with st.spinner("Processing PDF..."):
                try:
                    # Upload and process the PDF
                    upload_pdf(uploaded_file)
                    st.session_state.documents = load_pdf(pdfs_directory + uploaded_file.name)
                    st.session_state.chunked_documents = split_text(st.session_state.documents)
                    index_docs(st.session_state.chunked_documents)
                    st.session_state.pdf_processed = True
                    st.success("✅ PDF processed successfully!")
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")
                    st.stop()
        
        # Show processing status
        if st.session_state.pdf_processed:
            st.success("✅ PDF ready for questions")
            st.write(f"**Pages:** {len(st.session_state.documents)}")
            st.write(f"**Text Chunks:** {len(st.session_state.chunked_documents)}")
    
    # Chat controls
    st.header("💬 Chat Controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.session_state.messages:
            # Export chat functionality
            chat_export = "\n\n".join([
                f"**{msg['role'].title()}:** {msg['content']}" 
                for msg in st.session_state.messages
            ])
            
            st.download_button(
                label="📥 Export",
                data=chat_export,
                file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

# Main chat interface
if uploaded_file and st.session_state.pdf_processed:
    # Sample questions section
    if not st.session_state.messages:
        st.info("💡 **Get started with these sample questions:**")
        sample_questions = [
            "What is the main topic of this document?",
            "Can you summarize the key points?",
            "What are the main conclusions?",
            "Are there any specific recommendations?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(sample_questions):
            if cols[i % 2].button(f"❓ {question}", key=f"sample_{i}", use_container_width=True):
                # Process the sample question automatically
                st.session_state.messages.append({"role": "user", "content": question})
                
                try:
                    related_documents = retrieve_docs(question)
                    result = answer_question(question, related_documents)
                    
                    # Create assistant response with sources
                    assistant_content = result["answer"]
                    if result["sources"]:
                        assistant_content += f"\n\n**Sources:** {', '.join(result['sources'])}"
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": assistant_content,
                        "sources": result["sources"],
                        "context_used": result["context_used"]
                    })
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"❌ Error processing question: {str(e)}"
                    })
                
                st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 View Sources"):
                    st.write(f"**Answer based on {message.get('context_used', 0)} document chunks:**")
                    for source in message["sources"]:
                        st.write(f"• {source}")
    
    # Chat input
    if question := st.chat_input("Ask a question about the PDF..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Display user message
        with st.chat_message("user"):
            st.write(question)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    related_documents = retrieve_docs(question)
                    result = answer_question(question, related_documents)
                
                # Display answer
                st.write(result["answer"])
                
                # Display sources
                with st.expander("📚 View Sources"):
                    st.write(f"**Answer based on {result['context_used']} document chunks:**")
                    for source in result["sources"]:
                        st.write(f"• {source}")
                
                # Save to session state
                assistant_content = result["answer"]
                if result["sources"]:
                    assistant_content += f"\n\n**Sources:** {', '.join(result['sources'])}"
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": assistant_content,
                    "sources": result["sources"],
                    "context_used": result["context_used"]
                })
                
            except Exception as e:
                error_msg = f"❌ Error processing your question: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg
                })

else:
    # Welcome message when no PDF is uploaded
    st.markdown("""
    ## Welcome to Chat with PDF! 📄
    
    **Get started by:**
    1. 📤 Upload a PDF file using the sidebar
    2. ⏳ Wait for processing to complete
    3. 💬 Start asking questions about your document
    
    **Features:**
    - 🤖 AI-powered question answering
    - 📚 Source citations showing which parts of the document were used
    - 💾 Export chat history
    - 🔄 Sample questions to get you started
    """)

uploaded_file = st.file_uploader(
    "Upload PDF",
    type="pdf",
    accept_multiple_files=False
)

if uploaded_file:
    upload_pdf(uploaded_file)
    documents = load_pdf(pdfs_directory + uploaded_file.name)
    chunked_documents = split_text(documents)
    index_docs(chunked_documents)

    question = st.chat_input()

    if question:
        st.chat_message("user").write(question)
        related_documents = retrieve_docs(question)
        answer = answer_question(question, related_documents)
        st.chat_message("assistant").write(answer)


