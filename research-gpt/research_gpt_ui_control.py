import streamlit as st
from research_gpt_config import (
    AVAILABLE_MODELS, SEARCH_SUGGESTIONS, 
    DEFAULT_MAX_RESULTS, DEFAULT_ENABLE_DETAILED_ANALYSIS, 
    DEFAULT_SHOW_DEBUG_INFO, log_file
)

def render_query_input():
    """Render the query input section."""
    with st.container():
        st.subheader("💭 Research Query")
        default_query = st.session_state.get('suggested_query', '')
        query = st.text_area(
            "Enter your research query:",
            value=default_query,
            height=100,
            placeholder="What would you like to research today?"
        )
        
        # Clear suggestion after use
        if 'suggested_query' in st.session_state:
            del st.session_state['suggested_query']
    
    return query

def render_model_selection():
    """Render the model selection section."""
    with st.container():
        st.subheader("🤖 AI Model")
        model_names = [f"{desc}" for model, desc in AVAILABLE_MODELS]
        model_keys = [model for model, desc in AVAILABLE_MODELS]
        
        selected_index = st.selectbox(
            "Select Model:",
            range(len(model_names)),
            format_func=lambda x: model_names[x],
            index=0,
            help="Choose the AI model to use for research and analysis."
        )
        
        selected_model = model_keys[selected_index]
        st.session_state['selected_model'] = selected_model
    
    return selected_model

def render_settings():
    """Render the settings section."""
    with st.container():
        st.subheader("⚙️ Settings")
        max_results = st.slider("Max search results", 1, 10, DEFAULT_MAX_RESULTS)
        enable_detailed_analysis = st.checkbox("Enable detailed content analysis", DEFAULT_ENABLE_DETAILED_ANALYSIS)
        show_debug_info = st.checkbox("Show debug information", DEFAULT_SHOW_DEBUG_INFO)
    
    return max_results, enable_detailed_analysis, show_debug_info

def render_quick_actions():
    """Render the quick actions section."""
    with st.container():
        st.subheader("⚡ Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Results", use_container_width=True):
                if 'research_history' in st.session_state:
                    st.session_state['research_history'] = []
                st.rerun()
        with col2:
            if st.button("📄 View Logs", use_container_width=True):
                st.info(f"Logs: `{log_file}`")

def render_search_suggestions():
    """Render the search suggestions section."""
    with st.expander("💡 Suggested Queries", expanded=True):
        for suggestion in SEARCH_SUGGESTIONS:
            if st.button(f"🔍 {suggestion}", key=f"suggestion_{suggestion[:20]}", use_container_width=True):
                st.session_state['suggested_query'] = suggestion
                st.rerun()

def render_research_history():
    """Render the research history section."""
    with st.expander("📚 Quick History", expanded=False):
        if 'research_history' in st.session_state and st.session_state['research_history']:
            recent_searches = st.session_state['research_history'][-5:]  # Last 5 searches
            for i, search in enumerate(reversed(recent_searches)):
                short_query = search['query'][:30] + "..." if len(search['query']) > 30 else search['query']
                if st.button(f"🔄 {short_query}", key=f"history_{i}", use_container_width=True):
                    st.session_state['suggested_query'] = search['query']
                    st.rerun()
        else:
            st.info("No search history yet")

def render_control_panel():
    """Render the complete control panel."""
    st.header("🎛️ Control Panel")
    
    query = render_query_input()
    selected_model = render_model_selection()
    max_results, enable_detailed_analysis, show_debug_info = render_settings()
    render_quick_actions()
    render_search_suggestions()
    render_research_history()
    
    return query, selected_model, max_results, enable_detailed_analysis, show_debug_info 