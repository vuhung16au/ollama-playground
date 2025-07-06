import streamlit as st
from research_gpt_config import AVAILABLE_MODELS, DEFAULT_MODEL

def render_current_model_info():
    """Render current model information."""
    with st.container():
        st.subheader("🤖 Current Model")
        current_model = st.session_state.get('selected_model', DEFAULT_MODEL)
        st.info(f"**{current_model}**")

def render_system_info():
    """Render system information."""
    with st.container():
        st.subheader("💻 System Info")
        st.metric("Available Models", len(AVAILABLE_MODELS))
        st.metric("Session History", len(st.session_state.get('research_history', [])))

def render_metrics_dashboard():
    """Render the complete metrics dashboard."""
    st.header("📈 Metrics Dashboard")
    
    render_current_model_info()
    render_system_info()
    
    # Performance metrics container
    metrics_container = st.container()
    
    # Additional metrics will be populated during research
    with st.expander("📊 Detailed Metrics", expanded=False):
        st.info("Metrics will appear here after research is completed.")
    
    return metrics_container 