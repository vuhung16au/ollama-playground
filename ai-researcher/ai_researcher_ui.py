import streamlit as st
import time
import pandas as pd
from datetime import datetime

from ai_researcher_config import (
    AVAILABLE_MODELS, SEARCH_SUGGESTIONS, STEP_NAMES, 
    DEFAULT_MODEL, DEFAULT_MAX_RESULTS, DEFAULT_ENABLE_DETAILED_ANALYSIS, 
    DEFAULT_SHOW_DEBUG_INFO, log_file
)
from ai_researcher_analytics import analyze_search_quality, analyze_content_insights, save_research_session
from ai_researcher_export import export_research_data
from ai_researcher_utils import clean_text

def render_control_panel():
    """Render the left control panel."""
    st.header("🎛️ Control Panel")
    
    # Query input section
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
    
    # Model selection
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
    
    # Settings
    with st.container():
        st.subheader("⚙️ Settings")
        max_results = st.slider("Max search results", 1, 10, DEFAULT_MAX_RESULTS)
        enable_detailed_analysis = st.checkbox("Enable detailed content analysis", DEFAULT_ENABLE_DETAILED_ANALYSIS)
        show_debug_info = st.checkbox("Show debug information", DEFAULT_SHOW_DEBUG_INFO)
    
    # Quick Actions
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
    
    # Search suggestions
    with st.expander("💡 Suggested Queries", expanded=True):
        for suggestion in SEARCH_SUGGESTIONS:
            if st.button(f"🔍 {suggestion}", key=f"suggestion_{suggestion[:20]}", use_container_width=True):
                st.session_state['suggested_query'] = suggestion
                st.rerun()
    
    # Research history
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
    
    return query, selected_model, max_results, enable_detailed_analysis, show_debug_info

def render_metrics_dashboard():
    """Render the right metrics dashboard."""
    st.header("📈 Metrics Dashboard")
    
    # Current model info
    with st.container():
        st.subheader("🤖 Current Model")
        current_model = st.session_state.get('selected_model', DEFAULT_MODEL)
        st.info(f"**{current_model}**")
    
    # System info
    with st.container():
        st.subheader("💻 System Info")
        st.metric("Available Models", len(AVAILABLE_MODELS))
        st.metric("Session History", len(st.session_state.get('research_history', [])))
    
    # Performance metrics container
    metrics_container = st.container()
    
    # Additional metrics will be populated during research
    with st.expander("📊 Detailed Metrics", expanded=False):
        st.info("Metrics will appear here after research is completed.")
    
    return metrics_container

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

def render_research_results(response_state, query, model_used, total_research_time, enable_detailed_analysis, show_debug_info):
    """Render the research results section."""
    st.success("✅ Research completed!")
    
    # Handle different response types
    response_content = response_state["response"]
    if hasattr(response_content, 'content'):
        display_content = clean_text(str(response_content.content))
    else:
        display_content = clean_text(str(response_content))
    
    st.subheader("📋 Research Results")
    st.write(display_content)

    # Sources section
    with st.expander("🔗 Sources Used", expanded=True):
        for i, source in enumerate(response_state["sources"], 1):
            st.write(f"{i}. {source}")
    
    # Enhanced Metrics Dashboard
    try:
        search_quality = analyze_search_quality(response_state["web_results"], response_state["sources"], query)
        content_insights = analyze_content_insights(response_state["web_results"], response_state["sources"])
        
        # Save research session to history
        save_research_session(query, response_state, model_used, total_research_time)
    except Exception as e:
        # Fallback if analysis functions fail
        search_quality = {"avg_relevance": 0, "unique_domains": 0, "total_sources": len(response_state["sources"])}
        content_insights = {"top_keywords": [], "content_stats": {}}
        
        # Simple session save fallback
        if 'research_history' not in st.session_state:
            st.session_state['research_history'] = []
        st.session_state['research_history'].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "model": model_used,
            "total_time": total_research_time
        })
    
    # Enhanced Metrics Dashboard
    try:
        display_enhanced_metrics(response_state, total_research_time, search_quality)
    except Exception:
        # Function not defined, show basic metrics
        st.subheader("🎯 Basic Quality Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sources Found", len(response_state["sources"]))
        with col2:
            st.metric("Response Length", f"{len(str(response_state['response'])):,} chars")
        with col3:
            st.metric("Processing Time", f"{total_research_time:.2f}s")
    
    # Content Analysis & Insights (if enabled and function exists)
    if enable_detailed_analysis:
        try:
            display_content_analysis(content_insights)
        except Exception:
            # Function not defined, show basic content info
            st.subheader("🔍 Basic Content Analysis")
            st.info("Advanced content analysis features will be available when all functions are loaded.")
            st.write(f"**Sources analyzed:** {len(response_state['sources'])}")
            st.write(f"**Content processed:** {len(response_state.get('web_results', []))} articles")
    
    # Display performance metrics
    st.subheader("📊 Performance Metrics")
    
    # Show model used
    st.info(f"🤖 Model used: **{model_used}**")
    
    if "step_metrics" in response_state:
        metrics = response_state["step_metrics"]
        
        # Create performance summary table
        performance_data = []
        total_tokens = 0
        total_time = 0
        
        for step_key, step_data in metrics.items():
            if step_key in STEP_NAMES:
                performance_data.append({
                    "Step": STEP_NAMES[step_key],
                    "Input Tokens": step_data["input_tokens"],
                    "Output Tokens": step_data["output_tokens"],
                    "Total Tokens": step_data["total_tokens"],
                    "Time (s)": f"{step_data['duration']:.2f}",
                    "Tokens/sec": f"{step_data['tokens_per_second']:.2f}"
                })
                total_tokens += step_data["total_tokens"]
                total_time += step_data["duration"]
        
        # Add total row
        performance_data.append({
            "Step": "**🏁 Total**",
            "Input Tokens": "—",
            "Output Tokens": "—", 
            "Total Tokens": total_tokens,
            "Time (s)": f"{total_time:.2f}",
            "Tokens/sec": f"{total_tokens/total_time:.2f}" if total_time > 0 else "0.00"
        })
        
        st.table(performance_data)
        
        # Log file info
        st.info(f"📄 Detailed logs saved to: `{log_file}`")
        
        # Summary metrics in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tokens", f"{total_tokens:,}")
        with col2:
            st.metric("Total Time", f"{total_time:.2f}s")
        with col3:
            st.metric("Avg Tokens/sec", f"{total_tokens/total_time:.2f}" if total_time > 0 else "0.00")
    else:
        st.warning("No performance metrics available")
    
    # Export functionality
    try:
        export_research_data(response_state, query, model_used, total_research_time)
    except Exception:
        # Function not defined, show basic export info
        st.subheader("📤 Export & Share")
        st.info("Advanced export features will be available when all functions are loaded.")
        st.write("Results can be copied from the display above.")
    
    # Research History & Comparison
    try:
        display_research_history()
    except Exception:
        # Function not defined, show basic history
        st.subheader("📚 Research History")
        if 'research_history' in st.session_state and st.session_state['research_history']:
            st.write(f"**Total searches:** {len(st.session_state['research_history'])}")
            st.write("**Recent queries:**")
            for i, session in enumerate(st.session_state['research_history'][-3:]):
                st.write(f"• {session['query'][:50]}{'...' if len(session['query']) > 50 else ''}")
        else:
            st.info("No search history available yet.")
    
    # Debug information
    if show_debug_info:
        st.subheader("🔧 Debug Information")
        with st.expander("Debug Data"):
            st.json({
                "session_state": dict(st.session_state),
                "response_state": {
                    "sources_count": len(response_state["sources"]),
                    "web_results_count": len(response_state.get("web_results", [])),
                    "step_metrics": response_state.get("step_metrics", {})
                }
            })

def display_enhanced_metrics(response_state, research_start_time, search_quality):
    """Display comprehensive metrics dashboard."""
    
    # Research Quality Metrics
    st.subheader("🎯 Research Quality Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sources Found", search_quality["total_sources"])
    with col2:
        st.metric("Avg Relevance", f"{search_quality['avg_relevance']:.2f}")
    with col3:
        response_length = len(str(response_state["response"]))
        st.metric("Response Length", f"{response_length:,} chars")
    with col4:
        st.metric("Unique Domains", search_quality["unique_domains"])
    
    # Additional quality metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_content_length = sum(len(content) for content in response_state.get("web_results", [])) / len(response_state.get("web_results", [1]))
        st.metric("Avg Content Length", f"{avg_content_length:.0f} chars")
    with col2:
        compression_ratio = response_length / avg_content_length if avg_content_length > 0 else 0
        st.metric("Compression Ratio", f"{compression_ratio:.2f}x")
    with col3:
        total_research_time = time.time() - research_start_time
        st.metric("Research Speed", f"{response_length/total_research_time:.0f} chars/sec")

def display_content_analysis(content_insights):
    """Display content analysis insights."""
    
    st.subheader("🔍 Content Analysis & Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📊 Top Keywords:**")
        for word, count in content_insights["top_keywords"]:
            st.write(f"• {word}: {count} occurrences")
        
        st.write("**📈 Content Statistics:**")
        stats = content_insights["content_stats"]
        st.write(f"• Total words: {stats['total_words']:,}")
        st.write(f"• Unique words: {stats['unique_words']:,}")
        st.write(f"• Vocabulary richness: {stats['unique_words']/stats['total_words']:.2f}")
    
    with col2:
        st.write("**🏛️ Source Reliability:**")
        reliability = content_insights["source_reliability"]
        st.write(f"• Academic/Official: {reliability['reliable_sources']}")
        st.write(f"• News/Media: {reliability['news_sources']}")
        st.write(f"• Other sources: {reliability['other_sources']}")
        st.write(f"• Reliability score: {reliability['reliability_score']:.2f}")
        
        st.write("**📚 Content Types:**")
        for content_type, count in content_insights["content_types"].items():
            st.write(f"• {content_type}: {count}")

def display_research_history():
    """Display research history and comparison."""
    
    if 'research_history' not in st.session_state or not st.session_state['research_history']:
        st.info("No research history available yet. Complete some research queries to see history.")
        return
    
    st.subheader("📚 Research History & Comparison")
    
    history = st.session_state['research_history']
    
    # Create DataFrame for analysis
    df = pd.DataFrame(history)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Display recent searches
    with st.expander("📋 Recent Searches", expanded=False):
        for i, session in enumerate(reversed(history[-10:])):  # Show last 10
            st.write(f"**{i+1}.** {session['query'][:50]}{'...' if len(session['query']) > 50 else ''}")
            st.write(f"   ⏱️ {session['timestamp'][:16]} | 🤖 {session['model']} | ⚡ {session['total_time']:.1f}s")
            st.write("---")
    
    # Performance trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**⚡ Performance Trends:**")
        if len(df) > 1:
            st.line_chart(df.set_index('timestamp')[['total_time', 'avg_tokens_per_second']])
        else:
            st.info("Need more research sessions to show trends")
    
    with col2:
        st.write("**📊 Usage Statistics:**")
        st.metric("Total Searches", len(history))
        st.metric("Avg Response Time", f"{df['total_time'].mean():.2f}s")
        st.metric("Most Used Model", df['model'].mode().iloc[0] if not df.empty else "N/A")
        
        # Model usage distribution
        if not df.empty:
            model_counts = df['model'].value_counts()
            st.write("**🤖 Model Usage:**")
            for model, count in model_counts.items():
                st.write(f"• {model}: {count}") 