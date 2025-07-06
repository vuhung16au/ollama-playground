import streamlit as st
import time
import pandas as pd

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
        total_research_time = research_start_time  # This is actually the duration, not a timestamp
        st.metric("Research Speed", f"{response_length/total_research_time:.0f} chars/sec" if total_research_time > 0 else "0 chars/sec")

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