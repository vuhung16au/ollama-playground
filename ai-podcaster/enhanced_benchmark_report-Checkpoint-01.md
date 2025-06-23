# Enhanced Model Benchmark Report

## Summary

| Model | Tokens/sec | TTFT (s) | Memory (MB) | CPU % | GPU % | Size (GB) | Load Time (s) | Quality | Relevance |
|-------|------------|----------|-------------|-------|-------|-----------|---------------|---------|-----------|
| smollm2:1.7b | 44.49 | 2.471 | 228.4 | 5.8 | 100.0 | 1.8 | 1.86 | 7 | 7 |
| deepseek-r1:1.5b | 67.54 | 2.157 | 273.0 | 7.5 | 100.0 | 1.1 | 1.46 | 7 | 7 |
| phi3:mini | 36.96 | 5.180 | 294.4 | 4.4 | 100.0 | 0.00 | 2.2 | 3 | 3 |
| gemma:2b | 48.68 | 2.510 | 302.0 | 7.5 | 100.0 | 1.7 | 1.77 | 6 | 7 |
| llama3.2 | 32.89 | 4.927 | 303.9 | 5.7 | 100.0 | 2.0 | 2.12 | 7 | 7 |
| qwen2.5:3b | 36.82 | 5.134 | 361.3 | 6.1 | 100.0 | 1.9 | 2.39 | 6 | 6 |

## Detailed Results

### smollm2:1.7b

**prompt_1:**
- Response Tokens/sec: 44.49
- Time to First Token: 2.471s
- Peak Memory Usage: 228.4 MB
- Average CPU Usage: 5.8%
- Average GPU Usage: 100.0%
- Model Size: 0.00 GB
- Load Time: 1.86s
- Parameter Count: 1.7B
- Response Quality: TBC
- Relevance Score: TBC
- Success Rate: 100.0%

- Quality: 7
- Relevance: 7

### deepseek-r1:1.5b

**prompt_1:**
- Response Tokens/sec: 67.54
- Time to First Token: 2.157s
- Peak Memory Usage: 273.0 MB
- Average CPU Usage: 7.5%
- Average GPU Usage: 100.0%
- Model Size: 0.00 GB
- Load Time: 1.46s
- Parameter Count: 1.5B
- Response Quality: TBC
- Relevance Score: TBC
- Success Rate: 100.0%

- Quality: 7
- Relevance: 7

### phi3:mini

**prompt_1:**
- Response Tokens/sec: 36.96
- Time to First Token: 5.180s
- Peak Memory Usage: 294.4 MB
- Average CPU Usage: 4.4%
- Average GPU Usage: 100.0%
- Model Size: 0.00 GB
- Load Time: 3.10s
- Parameter Count: 3.8B
- Response Quality: TBC
- Relevance Score: TBC
- Success Rate: 100.0%

- Quality: 3
- Relevance: 3

### gemma:2b

**prompt_1:**
- Response Tokens/sec: 48.68
- Time to First Token: 2.510s
- Peak Memory Usage: 302.0 MB
- Average CPU Usage: 7.5%
- Average GPU Usage: 100.0%
- Model Size: 0.00 GB
- Load Time: 1.77s
- Parameter Count: 2.0B
- Response Quality: TBC
- Relevance Score: TBC
- Success Rate: 100.0%

- Quality: 6
- Relevance: 7

### llama3.2

**prompt_1:**
- Response Tokens/sec: 32.89
- Time to First Token: 4.927s
- Peak Memory Usage: 303.9 MB
- Average CPU Usage: 5.7%
- Average GPU Usage: 100.0%
- Model Size: 0.00 GB
- Load Time: 2.12s
- Parameter Count: 3.0B
- Response Quality: TBC
- Relevance Score: TBC
- Success Rate: 100.0%

- Quality: 7
- Relevance: 7

### qwen2.5:3b

**prompt_1:**
- Response Tokens/sec: 36.82
- Time to First Token: 5.134s
- Peak Memory Usage: 361.3 MB
- Average CPU Usage: 6.1%
- Average GPU Usage: 100.0%
- Model Size: 0.00 GB
- Load Time: 2.39s
- Parameter Count: 3.0B
- Response Quality: TBC
- Relevance Score: TBC
- Success Rate: 100.0%

- Quality: 6
- Relevance: 6

```
ollama list 
NAME                               ID              SIZE      MODIFIED     
qwen2.5:3b                         357c53fb659c    1.9 GB    3 hours ago     
phi3:mini                          4f2222927938    2.2 GB    3 hours ago     
phi3:latest                        4f2222927938    2.2 GB    4 hours ago     
mistral:7b-instruct-v0.2-q4_K_M    eb14864c7427    4.4 GB    4 hours ago     
gemma:2b                           b50d6c999e59    1.7 GB    4 hours ago     
qwen2.5:7b                         845dbda0ea48    4.7 GB    7 days ago      
smollm2:1.7b                       cef4a1e09247    1.8 GB    7 days ago      
llama3.2:3b                        a80c4f17acd5    2.0 GB    7 days ago      
deepseek-r1:8b                     6995872bfe4c    5.2 GB    7 days ago      
magistral:latest                   5dd7e640d9d9    14 GB     11 days ago     
llama3.1:8b                        46e0c10c039e    4.9 GB    3 months ago    
qwen2.5-coder:1.5b-base            02e0f2817a89    986 MB    3 months ago    
nomic-embed-text:latest            0a109f422b47    274 MB    3 months ago    
deepseek-r1:1.5b                   a42b25d8c10a    1.1 GB    4 months ago    
llama3.2:latest                    a80c4f17acd5    2.0 GB    4 months ago  
```