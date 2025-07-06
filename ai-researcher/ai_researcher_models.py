from typing_extensions import TypedDict
from typing import List, Dict, Any

class ResearchState(TypedDict):
    """Main state for the research workflow"""
    query: str
    sources: List[str]
    web_results: List[str]
    summarized_results: List[str]
    response: str
    # Performance tracking
    step_metrics: Dict[str, Dict[str, Any]]  # Store timing and token info for each step

class ResearchStateInput(TypedDict):
    """Input state for the research workflow"""
    query: str

class ResearchStateOutput(TypedDict):
    """Output state for the research workflow"""
    sources: List[str]
    response: str
    step_metrics: Dict[str, Dict[str, Any]]

class SearchQuality(TypedDict):
    """Search quality analysis results"""
    relevance_scores: List[float]
    content_lengths: List[int]
    source_diversity: set
    total_sources: int
    avg_relevance: float
    unique_domains: int

class ContentInsights(TypedDict):
    """Content analysis insights"""
    top_keywords: List[tuple]
    content_stats: Dict[str, Any]
    source_reliability: Dict[str, Any]
    content_types: Dict[str, int]

class ResearchSession(TypedDict):
    """Research session data for history"""
    timestamp: str
    query: str
    model: str
    sources_count: int
    total_tokens: int
    total_time: float
    response_length: int
    avg_tokens_per_second: float 