import time
import streamlit as st
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph

from ai_researcher_models import ResearchState
from ai_researcher_config import logger, SUMMARY_TEMPLATE, GENERATE_RESPONSE_TEMPLATE, DEFAULT_MODEL
from ai_researcher_utils import count_tokens, log_step_performance, clean_text, extract_response_content

def search_web(state: ResearchState):
    """Search the web for relevant information."""
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
    """Summarize the web search results."""
    start_time = time.time()
    logger.info("📊 Starting content analysis and summarization...")
    
    # Get selected model from session state, fallback to default
    selected_model = st.session_state.get('selected_model', DEFAULT_MODEL)
    logger.info(f"Using model for summarization: {selected_model}")
    model = ChatOllama(model=selected_model)
    prompt = ChatPromptTemplate.from_template(SUMMARY_TEMPLATE)
    chain = prompt | model

    summarized_results = []
    total_input_tokens = 0
    total_output_tokens = 0
    
    for content in state["web_results"]:
        input_tokens = count_tokens(content) + count_tokens(state["query"])
        total_input_tokens += input_tokens
        
        summary = chain.invoke({"query": state["query"], "content": content})
        clean_content = clean_text(extract_response_content(summary))
        
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
    """Generate the final research response."""
    start_time = time.time()
    logger.info("✨ Starting response generation...")
    
    # Get selected model from session state, fallback to default
    selected_model = st.session_state.get('selected_model', DEFAULT_MODEL)
    logger.info(f"Using model for response generation: {selected_model}")
    model = ChatOllama(model=selected_model)
    prompt = ChatPromptTemplate.from_template(GENERATE_RESPONSE_TEMPLATE)
    chain = prompt | model

    content = "\n\n".join([summary for summary in state["summarized_results"]])
    input_tokens = count_tokens(state["query"]) + count_tokens(content)
    
    response = chain.invoke({"question": state["query"], "context": content})
    response_content = extract_response_content(response)
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

def create_research_graph():
    """Create and return the compiled research workflow graph."""
    from ai_researcher_models import ResearchStateInput, ResearchStateOutput
    
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

    return builder.compile() 