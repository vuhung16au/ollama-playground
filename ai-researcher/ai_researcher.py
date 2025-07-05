import re
import os
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
    
    model = ChatOllama(model="deepseek-r1:8b")
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
    
    model = ChatOllama(model="deepseek-r1:8b")
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

st.title("AI Researcher")
query = st.text_input("Enter your research query:")

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
    
    # Handle different response types
    response_content = response_state["response"]
    if hasattr(response_content, 'content'):
        display_content = clean_text(str(response_content.content))
    else:
        display_content = clean_text(str(response_content))
    
    st.subheader("📋 Research Results")
    st.write(display_content)

    st.subheader("🔗 Sources Used")
    for i, source in enumerate(response_state["sources"], 1):
        st.write(f"{i}. {source}")
    
    # Display performance metrics
    st.subheader("📊 Performance Metrics")
    
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