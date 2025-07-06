import re
import time
from typing import Tuple
from ai_researcher_config import logger

def count_tokens(text: str) -> int:
    """Estimate token count by splitting on whitespace and punctuation."""
    # Simple token estimation - split on whitespace and punctuation
    tokens = re.findall(r'\b\w+\b', text)
    return len(tokens)

def log_step_performance(step_name: str, start_time: float, input_tokens: int, output_tokens: int) -> Tuple[float, int, float]:
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

def clean_text(text: str) -> str:
    """Clean text by removing think tags and extra whitespace."""
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()

def extract_response_content(response) -> str:
    """Extract content from different response types."""
    if hasattr(response, 'content'):
        return str(response.content)
    else:
        return str(response) 