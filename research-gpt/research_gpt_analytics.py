import re
import streamlit as st
from collections import Counter
from urllib.parse import urlparse
from datetime import datetime

from research_gpt_models import SearchQuality, ContentInsights, ResearchSession
from research_gpt_config import RELIABLE_DOMAINS, NEWS_DOMAINS, STOP_WORDS

def analyze_search_quality(web_results, sources, query) -> SearchQuality:
    """Analyze the quality and relevance of search results."""
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

def analyze_content_insights(web_results, sources) -> ContentInsights:
    """Analyze content for additional insights."""
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
    filtered_words = [word for word in words if len(word) > 3 and word not in STOP_WORDS]
    
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
    reliable_count = 0
    news_count = 0
    
    for source in sources:
        source_lower = source.lower()
        if any(domain in source_lower for domain in RELIABLE_DOMAINS):
            reliable_count += 1
            insights["content_types"]["Academic/Official"] += 1
        elif any(domain in source_lower for domain in NEWS_DOMAINS):
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

def save_research_session(query, response_state, model_used, total_time) -> None:
    """Save research session to history."""
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