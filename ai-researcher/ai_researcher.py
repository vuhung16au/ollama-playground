import time
import streamlit as st

from ai_researcher_config import logger
from ai_researcher_graph import create_research_graph
from ai_researcher_ui import (
    render_control_panel, render_metrics_dashboard, render_welcome_message,
    render_progress_tracking, render_research_results
)

# Set page config for wide layout
st.set_page_config(page_title="AI Researcher", layout="wide", initial_sidebar_state="collapsed")

st.title("🔬 AI Researcher")

# Create 3-column layout
left_col, middle_col, right_col = st.columns([25, 50, 25])

# ====== LEFT COLUMN - Control Panel ======
with left_col:
    query, selected_model, max_results, enable_detailed_analysis, show_debug_info = render_control_panel()

# ====== MIDDLE COLUMN - Main Content ======
with middle_col:
    st.header("📊 Research Results")
    
    # Show welcome message when idle
    if not query:
        render_welcome_message()
    
    # Main research results area
    research_container = st.container()

# ====== RIGHT COLUMN - Metrics Dashboard ======
with right_col:
    metrics_container = render_metrics_dashboard()

# Process research in the middle column
with middle_col:
    with research_container:
        if query:
            # Log the start of research
            logger.info(f"🚀 Starting research for query: '{query}'")
            research_start_time = time.time()
            
            # Create progress tracking containers
            progress_container, progress_bar, status_text, search_status, analyze_status, summarize_status, generate_status = render_progress_tracking()
            
            # Step 1: Searching
            status_text.markdown("🏃‍♂️ **Searching the web for information...**")
            search_status.markdown("🔍 **Search** 🏃‍♂️")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            # Execute the graph with progress tracking
            try:
                # Create the research graph
                graph = create_research_graph()
                
                # Update for web search completion
                search_status.markdown("🔍 **Search** ✅")
                analyze_status.markdown("📊 **Analyze** 🏃‍♂️")
                status_text.markdown("📊 **Analyzing content from sources...**")
                progress_bar.progress(50)
                time.sleep(0.5)
                
                # Get the response
                response_state = graph.invoke({"query": query, "step_metrics": {}})
                
                # Update for summarization
                analyze_status.markdown("📊 **Analyze** ✅")
                summarize_status.markdown("📝 **Summarize** 🏃‍♂️")
                status_text.markdown("📝 **Summarizing research findings...**")
                progress_bar.progress(75)
                time.sleep(0.5)
                
                # Update for final response
                summarize_status.markdown("📝 **Summarize** ✅")
                generate_status.markdown("✨ **Generate** 🏃‍♂️")
                status_text.markdown("✨ **Generating comprehensive response...**")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                # Complete
                generate_status.markdown("✨ **Generate** ✅")
                status_text.markdown("🎉 **Research completed successfully!**")
                
                # Log total research time
                total_research_time = time.time() - research_start_time
                logger.info(f"🏁 Research completed in {total_research_time:.2f} seconds")
                
                # Small delay to show completion
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Research failed: {str(e)}")
                status_text.markdown(f"❌ **Error during research:** {str(e)}")
                st.error(f"An error occurred: {str(e)}")
                st.stop()
            
            # Clear progress indicators after completion
            progress_container.empty()
            
            # Render research results
            render_research_results(
                response_state, query, selected_model, total_research_time, 
                enable_detailed_analysis, show_debug_info
            ) 