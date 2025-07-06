import logging
import os
from pathlib import Path
from dotenv import load_dotenv

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

# Available AI models
AVAILABLE_MODELS = [
    ("deepseek-r1:8b", "DeepSeek R1 8B (5.2 GB) - Reasoning focused"),
    ("qwen2.5:3b", "Qwen 2.5 3B (1.9 GB) - Fast & efficient"),
    ("gemma:2b", "Gemma 2B (1.7 GB) - Lightweight"),
    ("magistral:latest", "Magistral Latest (14 GB) - High capacity"),
]

# Default settings
DEFAULT_MODEL = "deepseek-r1:8b"
DEFAULT_MAX_RESULTS = 3
DEFAULT_ENABLE_DETAILED_ANALYSIS = True
DEFAULT_SHOW_DEBUG_INFO = False

# Search suggestions
SEARCH_SUGGESTIONS = [
    "Latest developments in AI research",
    "Climate change impact on global economy", 
    "Best practices for remote work productivity",
    "Cryptocurrency market trends 2024",
    "Health benefits of Mediterranean diet",
    "Future of renewable energy technologies",
    "Impact of social media on mental health",
    "Sustainable agriculture practices"
]

# Templates
SUMMARY_TEMPLATE = """
Summarize the following content into a concise paragraph that directly addresses the query. Ensure the summary 
highlights the key points relevant to the query while maintaining clarity and completeness.
Query: {query}
Content: {content}
"""

GENERATE_RESPONSE_TEMPLATE = """    
Given the following user query and content, generate a response that directly answers the query using relevant 
information from the content. Ensure that the response is clear, concise, and well-structured. 
Additionally, provide a brief summary of the key points from the response. 
Question: {question} 
Context: {context} 
Answer:
"""

# Step names for UI display
STEP_NAMES = {
    "search_web": "🔍 Search",
    "summarize_results": "📊 Analyze", 
    "generate_response": "✨ Generate"
}

# Reliable and news domains for source analysis
RELIABLE_DOMAINS = ['.edu', '.gov', '.org', '.ac.', 'wikipedia.org', 'scholar.google']
NEWS_DOMAINS = ['.com', '.net', 'news', 'times', 'post', 'journal', 'reuters', 'bbc', 'cnn']

# Stop words for keyword analysis
STOP_WORDS = {
    'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
    'is', 'are', 'was', 'were', 'a', 'an', 'this', 'that', 'will', 'would', 'could', 'should'
} 