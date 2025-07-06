import streamlit as st
import time
import pandas as pd
from datetime import datetime

from research_gpt_config import (
    AVAILABLE_MODELS, SEARCH_SUGGESTIONS, STEP_NAMES, 
    DEFAULT_MODEL, DEFAULT_MAX_RESULTS, DEFAULT_ENABLE_DETAILED_ANALYSIS, 
    DEFAULT_SHOW_DEBUG_INFO, log_file
)
from research_gpt_analytics import analyze_search_quality, analyze_content_insights, save_research_session
from research_gpt_export import export_research_data
from research_gpt_utils import clean_text

# Import UI components
from research_gpt_ui_control import render_control_panel as render_control_panel_component
from research_gpt_ui_metrics import render_metrics_dashboard as render_metrics_dashboard_component
from research_gpt_ui_progress import render_progress_tracking as render_progress_tracking_component
from research_gpt_ui_results import render_research_results as render_research_results_component
from research_gpt_ui_welcome import render_welcome_message as render_welcome_message_component

def render_control_panel():
    """Render the left control panel."""
    return render_control_panel_component()

def render_metrics_dashboard():
    """Render the right metrics dashboard."""
    return render_metrics_dashboard_component()

def render_welcome_message():
    """Render the welcome message when no query is entered."""
    return render_welcome_message_component()

def render_progress_tracking():
    """Render progress tracking components."""
    return render_progress_tracking_component()

def render_research_results(response_state, query, model_used, total_research_time, enable_detailed_analysis, show_debug_info):
    """Render the research results section."""
    return render_research_results_component(response_state, query, model_used, total_research_time, enable_detailed_analysis, show_debug_info)

# Legacy functions for backward compatibility
def display_enhanced_metrics(response_state, research_start_time, search_quality):
    """Display comprehensive metrics dashboard."""
    from research_gpt_ui_analytics import display_enhanced_metrics as display_enhanced_metrics_component
    return display_enhanced_metrics_component(response_state, research_start_time, search_quality)

def display_content_analysis(content_insights):
    """Display content analysis insights."""
    from research_gpt_ui_analytics import display_content_analysis as display_content_analysis_component
    return display_content_analysis_component(content_insights)

def display_research_history():
    """Display research history and comparison."""
    from research_gpt_ui_analytics import display_research_history as display_research_history_component
    return display_research_history_component() 