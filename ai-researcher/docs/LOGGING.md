# AI Researcher - Logging and Performance Monitoring

## Overview
The AI Researcher application now includes comprehensive logging and performance monitoring features that track token processing, timing, and performance metrics for each step of the research process.

## Features

### 🔍 Step-by-Step Logging
The application logs detailed information for each processing step:

- **🔍 Search** - Web search and content retrieval
- **📊 Analyze** - Content analysis and processing  
- **📝 Summarize** - Content summarization
- **✨ Generate** - Final response generation

### 📊 Performance Metrics
For each step, the system tracks:

- **Input Tokens**: Number of tokens in the input text
- **Output Tokens**: Number of tokens in the generated output
- **Total Tokens**: Combined input and output tokens
- **Processing Time**: Time taken for each step (in seconds)
- **Tokens/Second**: Processing speed (tokens per second)

### 📄 Logging Output
Logs are written to both:
- **Console**: Real-time logging during execution
- **Log File**: Persistent logging saved to `logs/log.txt`

## Log File Location
All logs are saved to: `logs/log.txt`

## Sample Log Output
```
2025-07-05 14:30:15,123 - INFO - 🚀 Starting research for query: 'What are the latest developments in AI?'
2025-07-05 14:30:15,456 - INFO - 🔍 Starting web search...
2025-07-05 14:30:18,789 - INFO - Step: Web Search | Input tokens: 8 | Output tokens: 1,247 | Total tokens: 1,255 | Time: 3.33s | Tokens/sec: 376.88
2025-07-05 14:30:19,012 - INFO - 📊 Starting content analysis and summarization...
2025-07-05 14:30:25,345 - INFO - Step: Summarization | Input tokens: 1,255 | Output tokens: 234 | Total tokens: 1,489 | Time: 6.33s | Tokens/sec: 235.15
2025-07-05 14:30:25,567 - INFO - ✨ Starting response generation...
2025-07-05 14:30:32,890 - INFO - Step: Response Generation | Input tokens: 242 | Output tokens: 456 | Total tokens: 698 | Time: 7.32s | Tokens/sec: 95.36
2025-07-05 14:30:32,912 - INFO - 🏁 Research completed in 17.45 seconds
```

## Performance Metrics Display
The Streamlit interface now includes a "Performance Metrics" section that displays:

### 📊 Step-by-Step Table
| Step | Input Tokens | Output Tokens | Total Tokens | Time (s) | Tokens/sec |
|------|-------------|---------------|--------------|----------|------------|
| 🔍 Search | 8 | 1,247 | 1,255 | 3.33 | 376.88 |
| 📊 Analyze | 1,255 | 234 | 1,489 | 6.33 | 235.15 |
| ✨ Generate | 242 | 456 | 698 | 7.32 | 95.36 |
| **🏁 Total** | — | — | 3,442 | 16.98 | 202.71 |

### 📈 Summary Metrics
- **Total Tokens**: 3,442
- **Total Time**: 16.98s  
- **Avg Tokens/sec**: 202.71

## Testing
Run the test script to see the logging functionality in action:

```bash
python test_logging.py
```

## Implementation Details

### Token Counting
- Uses regex-based token estimation: `re.findall(r'\\b\\w+\\b', text)`
- Counts words separated by whitespace and punctuation
- Provides reasonable approximation for performance monitoring

### Performance Logging Function
```python
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
```

### State Management
The `ResearchState` class now includes:
```python
class ResearchState(TypedDict):
    query: str
    sources: list[str]
    web_results: list[str]
    summarized_results: list[str]
    response: str
    step_metrics: dict[str, dict]  # Performance tracking
```

## Usage
1. Run the application: `streamlit run ai_researcher.py`
2. Enter your research query
3. Monitor the progress indicators: 🔍 Search ✅ → 📊 Analyze ✅ → 📝 Summarize ✅ → ✨ Generate ✅
4. View the performance metrics in the results section
5. Check the log file for detailed timing information

The logging system provides valuable insights into:
- Processing efficiency
- Token usage patterns
- Performance bottlenecks
- Overall system performance
