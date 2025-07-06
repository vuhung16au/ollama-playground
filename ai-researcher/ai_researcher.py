import re
import os
import time
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse

import streamlit as st
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph
from typing_extensions import TypedDict

import pandas as pd
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

import streamlit as st
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph
from typing_extensions import TypedDict

# Load environment variables from .env file
load_dotenv()

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "log.txt"

# Configure logging to write to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def count_tokens(text: str) -> int:
    """Estimate token count by splitting on whitespace and punctuation."""
    import re
    # Simple token estimation - split on whitespace and punctuation
    tokens = re.findall(r'\b\w+\b', text)
    return len(tokens)

def log_step_performance(step_name: str, start_time: float, input_tokens: int, output_tokens: int):
    """Log performance metrics for a processing step."""
    end_time = time.time()
    duration = end_time - start_time
    total_tokens = input_tokens + output_tokens
    tokens_per_second = total_tokens / duration if duration > 0 else 0
    
    log_message = (
        f"Step: {step_name} | "
        f"Input tokens: {input_tokens} | "
        f"Output tokens: {output_tokens} | "
        f"Total tokens: {total_tokens} | "
        f"Time: {duration:.2f}s | "
        f"Tokens/sec: {tokens_per_second:.2f}"
    )
    
    logger.info(log_message)
    return duration, total_tokens, tokens_per_second

summary_template = """
Summarize the following content into a concise paragraph that directly addresses the query. Ensure the summary 
highlights the key points relevant to the query while maintaining clarity and completeness.
Query: {query}
Content: {content}
"""

generate_response_template = """    
Given the following user query and content, generate a response that directly answers the query using relevant 
information from the content. Ensure that the response is clear, concise, and well-structured. 
Additionally, provide a brief summary of the key points from the response. 
Question: {question} 
Context: {context} 
Answer:
"""

class ResearchState(TypedDict):
    query: str
    sources: list[str]
    web_results: list[str]
    summarized_results: list[str]
    response: str
    # Performance tracking
    step_metrics: dict[str, dict]  # Store timing and token info for each step

class ResearchStateInput(TypedDict):
    query: str

class ResearchStateOutput(TypedDict):
    sources: list[str]
    response: str
    step_metrics: dict[str, dict]

def search_web(state: ResearchState):
    start_time = time.time()
    logger.info("🔍 Starting web search...")
    
    search = TavilySearch(max_results=3)
    search_results = search.invoke(state["query"])
    
    # Count tokens
    query_tokens = count_tokens(state["query"])
    results_content = " ".join([result['content'] for result in search_results['results']])
    output_tokens = count_tokens(results_content)
    
    # Log performance
    duration, total_tokens, tokens_per_second = log_step_performance(
        "Web Search", start_time, query_tokens, output_tokens
    )
    
    # Add a small delay to show progress
    time.sleep(0.5)

    step_metrics = state.get("step_metrics", {})
    step_metrics["search_web"] = {
        "duration": duration,
        "input_tokens": query_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "tokens_per_second": tokens_per_second
    }

    return {
        "sources": [result['url'] for result in search_results['results']],
        "web_results": [result['content'] for result in search_results['results']],
        "step_metrics": step_metrics
    }

def summarize_results(state: ResearchState):
    start_time = time.time()
    logger.info("📊 Starting content analysis and summarization...")
    
    # Get selected model from session state, fallback to default
    selected_model = st.session_state.get('selected_model', 'deepseek-r1:8b')
    logger.info(f"Using model for summarization: {selected_model}")
    model = ChatOllama(model=selected_model)
    prompt = ChatPromptTemplate.from_template(summary_template)
    chain = prompt | model

    summarized_results = []
    total_input_tokens = 0
    total_output_tokens = 0
    
    for content in state["web_results"]:
        input_tokens = count_tokens(content) + count_tokens(state["query"])
        total_input_tokens += input_tokens
        
        summary = chain.invoke({"query": state["query"], "content": content})
        # Handle different response types
        if hasattr(summary, 'content'):
            clean_content = clean_text(str(summary.content))
        else:
            clean_content = clean_text(str(summary))
        
        output_tokens = count_tokens(clean_content)
        total_output_tokens += output_tokens
        
        summarized_results.append(clean_content)
    
    # Log performance
    duration, total_tokens, tokens_per_second = log_step_performance(
        "Summarization", start_time, total_input_tokens, total_output_tokens
    )
    
    # Add a small delay to show progress
    time.sleep(0.5)

    step_metrics = state.get("step_metrics", {})
    step_metrics["summarize_results"] = {
        "duration": duration,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "tokens_per_second": tokens_per_second
    }

    return {
        "summarized_results": summarized_results,
        "step_metrics": step_metrics
    }

def generate_response(state: ResearchState):
    start_time = time.time()
    logger.info("✨ Starting response generation...")
    
    # Get selected model from session state, fallback to default
    selected_model = st.session_state.get('selected_model', 'deepseek-r1:8b')
    logger.info(f"Using model for response generation: {selected_model}")
    model = ChatOllama(model=selected_model)
    prompt = ChatPromptTemplate.from_template(generate_response_template)
    chain = prompt | model

    content = "\n\n".join([summary for summary in state["summarized_results"]])
    input_tokens = count_tokens(state["query"]) + count_tokens(content)
    
    response = chain.invoke({"question": state["query"], "context": content})
    
    # Handle different response types for token counting
    if hasattr(response, 'content'):
        response_content = str(response.content)
    else:
        response_content = str(response)
    
    output_tokens = count_tokens(response_content)
    
    # Log performance
    duration, total_tokens, tokens_per_second = log_step_performance(
        "Response Generation", start_time, input_tokens, output_tokens
    )
    
    # Add a small delay to show progress
    time.sleep(0.5)
    
    step_metrics = state.get("step_metrics", {})
    step_metrics["generate_response"] = {
        "duration": duration,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "tokens_per_second": tokens_per_second
    }
    
    return {
        "response": response,
        "step_metrics": step_metrics
    }

def clean_text(text: str):
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()

builder = StateGraph(
    ResearchState,
    input=ResearchStateInput,
    output=ResearchStateOutput
)

builder.add_node("search_web", search_web)
builder.add_node("summarize_results", summarize_results)
builder.add_node("generate_response", generate_response)

builder.add_edge(START, "search_web")
builder.add_edge("search_web", "summarize_results")
builder.add_edge("summarize_results", "generate_response")
builder.add_edge("generate_response", END)

graph = builder.compile()

# Set page config for wide layout
st.set_page_config(page_title="AI Researcher", layout="wide", initial_sidebar_state="collapsed")

st.title("🔬 AI Researcher")

# Create 3-column layout
left_col, middle_col, right_col = st.columns([25, 50, 25])

# ====== LEFT COLUMN - Control Panel ======
with left_col:
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
        available_models = [
            ("deepseek-r1:8b", "DeepSeek R1 8B (5.2 GB) - Reasoning focused"),
            ("qwen2.5:3b", "Qwen 2.5 3B (1.9 GB) - Fast & efficient"),
            ("gemma:2b", "Gemma 2B (1.7 GB) - Lightweight"),
            ("magistral:latest", "Magistral Latest (14 GB) - High capacity"),
        ]
        
        model_names = [f"{desc}" for model, desc in available_models]
        model_keys = [model for model, desc in available_models]
        
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
        max_results = st.slider("Max search results", 1, 10, 3)
        enable_detailed_analysis = st.checkbox("Enable detailed content analysis", True)
        show_debug_info = st.checkbox("Show debug information", False)
    
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
        suggestions = [
            "Latest developments in AI research",
            "Climate change impact on global economy", 
            "Best practices for remote work productivity",
            "Cryptocurrency market trends 2024",
            "Health benefits of Mediterranean diet",
            "Future of renewable energy technologies",
            "Impact of social media on mental health",
            "Sustainable agriculture practices"
        ]
        
        for suggestion in suggestions:
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

# ====== MIDDLE COLUMN - Main Content ======
with middle_col:
    st.header("📊 Research Results")
    
    # Show welcome message when idle
    if not query:
        st.info("👋 Welcome to AI Researcher! Enter your query in the left panel to get started.")
        st.markdown("""
        ### Features:
        - 🔍 **Advanced Web Search** - Find relevant information from multiple sources
        - 📊 **Content Analysis** - Intelligent summarization and insights
        - ⚡ **Performance Tracking** - Real-time metrics and optimization
        - 🤖 **Multiple AI Models** - Choose the best model for your needs
        - 📚 **Research History** - Track and revisit your previous searches
        """)
    
    # Main research results area
    research_container = st.container()

# ====== RIGHT COLUMN - Metrics Dashboard ======
with right_col:
    st.header("📈 Metrics Dashboard")
    
    # Current model info
    with st.container():
        st.subheader("🤖 Current Model")
        current_model = st.session_state.get('selected_model', 'deepseek-r1:8b')
        st.info(f"**{current_model}**")
    
    # System info
    with st.container():
        st.subheader("💻 System Info")
        st.metric("Available Models", len(available_models))
        st.metric("Session History", len(st.session_state.get('research_history', [])))
    
    # Performance metrics container
    metrics_container = st.container()
    
    # Additional metrics will be populated during research
    with st.expander("📊 Detailed Metrics", expanded=False):
        st.info("Metrics will appear here after research is completed.")

# Process research in the middle column
with middle_col:
    with research_container:
        if query:
            # Log the start of research
            logger.info(f"🚀 Starting research for query: '{query}'")
            research_start_time = time.time()
            
            # Create progress tracking containers
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
            
            # Step 1: Searching
            status_text.markdown("🏃‍♂️ **Searching the web for information...**")
            search_status.markdown("🔍 **Search** 🏃‍♂️")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            # Execute the graph with progress tracking
            try:
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
            
            # Show results
            st.success("✅ Research completed!")
            
            # Calculate total research time
            total_research_time = time.time() - research_start_time
            model_used = st.session_state.get('selected_model', 'deepseek-r1:8b')
            
            # Update metrics in right column
            with right_col:
                with metrics_container:
                    st.subheader("⚡ Performance")
                    
                    # Real-time metrics cards
                    if "step_metrics" in response_state:
                        metrics = response_state["step_metrics"]
                        total_tokens = sum(step["total_tokens"] for step in metrics.values())
                        total_time = sum(step["duration"] for step in metrics.values())
                        
                        st.metric("Total Tokens", f"{total_tokens:,}")
                        st.metric("Processing Time", f"{total_time:.2f}s")
                        st.metric("Tokens/sec", f"{total_tokens/total_time:.2f}" if total_time > 0 else "0.00")
                        
                        # Step breakdown
                        with st.expander("📊 Step Breakdown"):
                            step_names = {
                                "search_web": "🔍 Search",
                                "summarize_results": "📊 Analyze", 
                                "generate_response": "✨ Generate"
                            }
                            
                            for step_key, step_data in metrics.items():
                                if step_key in step_names:
                                    st.write(f"**{step_names[step_key]}**")
                                    st.write(f"• Time: {step_data['duration']:.2f}s")
                                    st.write(f"• Tokens: {step_data['total_tokens']}")
                                    st.write(f"• Speed: {step_data['tokens_per_second']:.2f} t/s")
                                    st.write("---")
            
            # Analyze search quality and content insights (if functions exist)
            try:
                search_quality = analyze_search_quality(response_state["web_results"], response_state["sources"], query)
                content_insights = analyze_content_insights(response_state["web_results"], response_state["sources"])
                
                # Save research session to history
                save_research_session(query, response_state, model_used, total_research_time)
            except NameError:
                # Functions not defined, skip analysis
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
            
            # Enhanced Metrics Dashboard (if function exists)
            try:
                display_enhanced_metrics(response_state, research_start_time, search_quality)
            except NameError:
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
                except NameError:
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
                
                step_names = {
                    "search_web": "🔍 Search",
                    "summarize_results": "📊 Analyze", 
                    "generate_response": "✨ Generate"
                }
                
                for step_key, step_data in metrics.items():
                    if step_key in step_names:
                        performance_data.append({
                            "Step": step_names[step_key],
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
            
            # Export functionality (if function exists)
            try:
                export_research_data(response_state, query, model_used, total_research_time)
            except NameError:
                # Function not defined, show basic export info
                st.subheader("📤 Export & Share")
                st.info("Advanced export features will be available when all functions are loaded.")
                st.write("Results can be copied from the display above.")
            
            # Research History & Comparison (if function exists)
            try:
                display_research_history()
            except NameError:
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

# New features to add
# 🔍 Search & Content Enhancements
# 📊 Enhanced Metrics Dashboard
# 📈 Research History & Comparison
# 🎨 Content Analysis & Insights

def analyze_search_quality(web_results, sources, query):
    """Analyze the quality and relevance of search results"""
    search_quality = {
        "relevance_scores": [],
        "content_lengths": [],
        "source_diversity": set(),
        "total_sources": len(sources),
        "avg_relevance": 0,
        "unique_domains": 0
    }
    
    query_terms = query.lower().split()
    
    for result in web_results:
        # Simple relevance scoring based on query terms
        content_lower = result.lower()
        relevance = sum(1 for term in query_terms if term in content_lower) / len(query_terms)
        
        search_quality["relevance_scores"].append(relevance)
        search_quality["content_lengths"].append(len(result))
    
    # Calculate domain diversity
    for source in sources:
        try:
            parsed = urlparse(source)
            domain = parsed.netloc.lower()
            search_quality["source_diversity"].add(domain)
        except:
            pass
    
    search_quality["avg_relevance"] = sum(search_quality["relevance_scores"]) / len(search_quality["relevance_scores"]) if search_quality["relevance_scores"] else 0
    search_quality["unique_domains"] = len(search_quality["source_diversity"])
    
    return search_quality

def analyze_content_insights(web_results, sources):
    """Analyze content for additional insights"""
    insights = {
        "top_keywords": [],
        "content_stats": {},
        "source_reliability": {},
        "content_types": Counter()
    }
    
    # Combine all text for analysis
    all_text = " ".join(web_results)
    
    # Extract keywords (simple frequency analysis)
    words = re.findall(r'\b\w+\b', all_text.lower())
    # Filter out common words and short words
    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'a', 'an', 'this', 'that', 'will', 'would', 'could', 'should'}
    filtered_words = [word for word in words if len(word) > 3 and word not in stop_words]
    
    word_freq = Counter(filtered_words)
    insights["top_keywords"] = word_freq.most_common(10)
    
    # Content statistics
    insights["content_stats"] = {
        "total_words": len(words),
        "unique_words": len(set(words)),
        "avg_content_length": sum(len(content) for content in web_results) / len(web_results),
        "total_content_length": sum(len(content) for content in web_results)
    }
    
    # Source reliability analysis
    reliable_domains = ['.edu', '.gov', '.org', '.ac.', 'wikipedia.org', 'scholar.google']
    news_domains = ['.com', '.net', 'news', 'times', 'post', 'journal', 'reuters', 'bbc', 'cnn']
    
    reliable_count = 0
    news_count = 0
    
    for source in sources:
        source_lower = source.lower()
        if any(domain in source_lower for domain in reliable_domains):
            reliable_count += 1
            insights["content_types"]["Academic/Official"] += 1
        elif any(domain in source_lower for domain in news_domains):
            news_count += 1
            insights["content_types"]["News/Media"] += 1
        else:
            insights["content_types"]["Other"] += 1
    
    insights["source_reliability"] = {
        "reliable_sources": reliable_count,
        "news_sources": news_count,
        "other_sources": len(sources) - reliable_count - news_count,
        "reliability_score": reliable_count / len(sources) if sources else 0
    }
    
    return insights

def save_research_session(query, response_state, model_used, total_time):
    """Save research session to history"""
    if 'research_history' not in st.session_state:
        st.session_state['research_history'] = []
    
    session_data = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "model": model_used,
        "sources_count": len(response_state["sources"]),
        "total_tokens": sum(step["total_tokens"] for step in response_state.get("step_metrics", {}).values()),
        "total_time": total_time,
        "response_length": len(str(response_state["response"])),
        "avg_tokens_per_second": sum(step["total_tokens"] for step in response_state.get("step_metrics", {}).values()) / total_time if total_time > 0 else 0
    }
    
    st.session_state['research_history'].append(session_data)
    
    # Keep only last 20 sessions
    if len(st.session_state['research_history']) > 20:
        st.session_state['research_history'] = st.session_state['research_history'][-20:]

def display_enhanced_metrics(response_state, research_start_time, search_quality):
    """Display comprehensive metrics dashboard"""
    
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
    """Display content analysis insights"""
    
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
    """Display research history and comparison"""
    
    if 'research_history' not in st.session_state or not st.session_state['research_history']:
        st.info("No research history available yet. Complete some research queries to see history.")
        return
    
    st.subheader("📚 Research History & Comparison")
    
    history = st.session_state['research_history']
    
    # Create DataFrame for analysis
    import pandas as pd
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
                st.write(f"• {model}: {count} times")

def export_research_data(response_state, query, model_used, total_time):
    """Add export functionality"""
    
    st.subheader("📤 Export & Share")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Export JSON"):
            export_data = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "model_used": model_used,
                "response": str(response_state["response"]),
                "sources": response_state["sources"],
                "metrics": response_state.get("step_metrics", {}),
                "total_time": total_time
            }
            
            st.download_button(
                label="💾 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📝 Export Markdown"):
            response_content = str(response_state["response"])
            markdown_content = f"""# Research Report: {query}

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Model:** {model_used}  
**Duration:** {total_time:.2f} seconds

## 🔍 Research Results

{response_content}

## 🔗 Sources

{chr(10).join(f"{i+1}. {source}" for i, source in enumerate(response_state["sources"]))}

## 📊 Performance Metrics

- **Total Processing Time:** {total_time:.2f}s
- **Total Tokens:** {sum(step['total_tokens'] for step in response_state.get('step_metrics', {}).values())}
- **Average Speed:** {sum(step['total_tokens'] for step in response_state.get('step_metrics', {}).values()) / total_time:.2f} tokens/sec

---
*Generated by AI Researcher*
"""
            
            st.download_button(
                label="💾 Download Markdown",
                data=markdown_content,
                file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
    
    with col3:
        if st.button("📊 Export CSV"):
            # Create a summary CSV
            csv_data = {
                "Query": [query],
                "Timestamp": [datetime.now().isoformat()],
                "Model": [model_used],
                "Sources_Count": [len(response_state["sources"])],
                "Response_Length": [len(str(response_state["response"]))],
                "Total_Time": [total_time],
                "Total_Tokens": [sum(step['total_tokens'] for step in response_state.get('step_metrics', {}).values())]
            }
            
            import pandas as pd
            csv_df = pd.DataFrame(csv_data)
            csv_string = csv_df.to_csv(index=False)
            
            st.download_button(
                label="💾 Download CSV",
                data=csv_string,
                file_name=f"research_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )