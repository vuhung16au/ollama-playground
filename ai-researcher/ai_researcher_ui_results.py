import streamlit as st
import time
from datetime import datetime

from ai_researcher_config import STEP_NAMES, log_file
from ai_researcher_analytics import analyze_search_quality, analyze_content_insights, save_research_session
from ai_researcher_export import export_research_data
from ai_researcher_utils import clean_text

def render_basic_results(response_state):
    """Render basic research results."""
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

def render_performance_metrics(response_state, model_used):
    """Render performance metrics."""
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

def render_export_section(response_state, query, model_used, total_research_time):
    """Render export functionality."""
    try:
        export_research_data(response_state, query, model_used, total_research_time)
    except Exception:
        # Function not defined, show basic export info
        st.subheader("📤 Export & Share")
        st.info("Advanced export features will be available when all functions are loaded.")
        st.write("Results can be copied from the display above.")

def render_debug_info(response_state, show_debug_info):
    """Render debug information."""
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

def render_research_results(response_state, query, model_used, total_research_time, enable_detailed_analysis, show_debug_info):
    """Render the complete research results section."""
    render_basic_results(response_state)
    
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
        from ai_researcher_ui_analytics import display_enhanced_metrics
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
            from ai_researcher_ui_analytics import display_content_analysis
            display_content_analysis(content_insights)
        except Exception:
            # Function not defined, show basic content info
            st.subheader("🔍 Basic Content Analysis")
            st.info("Advanced content analysis features will be available when all functions are loaded.")
            st.write(f"**Sources analyzed:** {len(response_state['sources'])}")
            st.write(f"**Content processed:** {len(response_state.get('web_results', []))} articles")
    
    render_performance_metrics(response_state, model_used)
    render_export_section(response_state, query, model_used, total_research_time)
    render_debug_info(response_state, show_debug_info) 