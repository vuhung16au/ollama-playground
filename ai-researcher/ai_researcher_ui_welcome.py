import streamlit as st

def render_welcome_message():
    """Render the welcome message when no query is entered."""
    st.info("👋 Welcome to AI Researcher! Enter your query in the left panel to get started.")
    st.markdown("""
    ### Features:
    - 🔍 **Advanced Web Search** - Find relevant information from multiple sources
    - 📊 **Content Analysis** - Intelligent summarization and insights
    - ⚡ **Performance Tracking** - Real-time metrics and optimization
    - 🤖 **Multiple AI Models** - Choose the best model for your needs
    - 📚 **Research History** - Track and revisit your previous searches
    """) 