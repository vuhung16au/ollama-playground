import streamlit as st
import os
from datetime import datetime
import pandas as pd

def show_logs():
    """Display log files in a user-friendly format."""
    
    st.title("📊 Application Logs & Performance")
    
    # Check if log files exist
    main_log_file = "./logs/image-search.log"
    timing_log_file = "./logs/image-search-timing.log"
    
    tab1, tab2, tab3 = st.tabs(["📝 Application Logs", "⏱️ Performance Timing", "📈 Analytics"])
    
    with tab1:
        st.header("Application Logs")
        
        if os.path.exists(main_log_file):
            try:
                with open(main_log_file, 'r', encoding='utf-8') as f:
                    logs = f.readlines()
                
                # Show recent logs first
                logs.reverse()
                
                # Filter options
                log_level = st.selectbox("Filter by log level:", ["ALL", "INFO", "WARNING", "ERROR"])
                max_lines = st.slider("Number of lines to show:", 10, 500, 50)
                
                filtered_logs = []
                for log in logs[:max_lines]:
                    if log_level == "ALL" or log_level in log:
                        filtered_logs.append(log.strip())
                
                if filtered_logs:
                    # Display logs in a text area
                    st.text_area(
                        "Recent Logs (newest first):",
                        value="\\n".join(filtered_logs),
                        height=400,
                        help="These are the most recent application logs. Use the filter to see specific log levels."
                    )
                else:
                    st.info("No logs match the selected filter.")
                    
            except Exception as e:
                st.error(f"Error reading log file: {str(e)}")
        else:
            st.warning("No application logs found. Logs will appear after you start using the application.")
    
    with tab2:
        st.header("Performance Timing")
        
        if os.path.exists(timing_log_file):
            try:
                timing_data = []
                with open(timing_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split(" | ")
                            if len(parts) >= 4:
                                timing_data.append({
                                    "Timestamp": parts[0],
                                    "Function": parts[1],
                                    "Execution Time (s)": float(parts[2].replace('s', '')),
                                    "Status": parts[3],
                                    "Error": parts[4] if len(parts) > 4 else ""
                                })
                
                if timing_data:
                    df = pd.DataFrame(timing_data)
                    
                    # Show summary statistics
                    st.subheader("Performance Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Operations", len(df))
                    
                    with col2:
                        avg_time = df["Execution Time (s)"].mean()
                        st.metric("Average Time", f"{avg_time:.4f}s")
                    
                    with col3:
                        success_rate = (df["Status"] == "SUCCESS").sum() / len(df) * 100
                        st.metric("Success Rate", f"{success_rate:.1f}%")
                    
                    with col4:
                        max_time = df["Execution Time (s)"].max()
                        st.metric("Slowest Operation", f"{max_time:.4f}s")
                    
                    # Show function performance breakdown
                    st.subheader("Performance by Function")
                    
                    function_stats = df.groupby("Function").agg({
                        "Execution Time (s)": ["count", "mean", "min", "max"],
                        "Status": lambda x: (x == "SUCCESS").sum() / len(x) * 100
                    }).round(4)
                    
                    function_stats.columns = ["Count", "Avg Time", "Min Time", "Max Time", "Success Rate %"]
                    st.dataframe(function_stats, use_container_width=True)
                    
                    # Show recent timing data
                    st.subheader("Recent Operations")
                    recent_data = df.tail(20).iloc[::-1]  # Show last 20, newest first
                    st.dataframe(recent_data, use_container_width=True)
                    
                else:
                    st.info("No timing data available yet.")
                    
            except Exception as e:
                st.error(f"Error reading timing file: {str(e)}")
        else:
            st.warning("No timing logs found. Performance data will appear after you use the search functionality.")
    
    with tab3:
        st.header("Usage Analytics")
        
        if os.path.exists(timing_log_file):
            try:
                timing_data = []
                with open(timing_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split(" | ")
                            if len(parts) >= 4:
                                timing_data.append({
                                    "Timestamp": pd.to_datetime(parts[0]),
                                    "Function": parts[1],
                                    "Execution Time (s)": float(parts[2].replace('s', '')),
                                    "Status": parts[3]
                                })
                
                if timing_data:
                    df = pd.DataFrame(timing_data)
                    
                    # Usage over time
                    st.subheader("Operations Over Time")
                    df_hourly = df.set_index("Timestamp").resample("H").size()
                    if len(df_hourly) > 0:
                        st.line_chart(df_hourly)
                    
                    # Function usage distribution
                    st.subheader("Function Usage Distribution")
                    function_counts = df["Function"].value_counts()
                    st.bar_chart(function_counts)
                    
                    # Performance trends
                    st.subheader("Performance Trends")
                    if len(df) > 1:
                        df_performance = df.set_index("Timestamp")["Execution Time (s)"].resample("H").mean()
                        st.line_chart(df_performance)
                    
                else:
                    st.info("No analytics data available yet.")
                    
            except Exception as e:
                st.error(f"Error generating analytics: {str(e)}")
        else:
            st.warning("No data available for analytics.")
    
    # Refresh button
    if st.button("🔄 Refresh Logs"):
        st.rerun()

if __name__ == "__main__":
    show_logs()
