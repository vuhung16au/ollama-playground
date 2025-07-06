import streamlit as st

def render_progress_tracking():
    """Render progress tracking components."""
    progress_container = st.container()
    
    with progress_container:
        # Main progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step indicators
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_status = st.empty()
            search_status.markdown("🔍 **Search**")
        with col2:
            analyze_status = st.empty()
            analyze_status.markdown("📊 **Analyze**")
        with col3:
            summarize_status = st.empty()
            summarize_status.markdown("📝 **Summarize**")
        with col4:
            generate_status = st.empty()
            generate_status.markdown("✨ **Generate**")
    
    return progress_container, progress_bar, status_text, search_status, analyze_status, summarize_status, generate_status 