
# Rebrand the app

Old name: ai-researcher
New name: research-gpt

Please change the file names acordingly:

old names: 
research_gpt*.py

new names:
research_gpt*.py

also change the references in the codebase.

Don't change the names of the variables, constants, functions, classes, etc.
Don't change the logic of the codebase.

ONLY change file names and references in the codebase.

# Change the name of the app 

Current name: ResearchGPT
New name: ResearchGPT

Pls change the name, references in 
- all markdown files
- all streamlit UI files 

Note:
- Don't change the codebase, just the name
- Don't change names of the variables, constants, functions, classes, etc.

# Refactor `research_gpt_ui.py`, the file is too big 

- Split the file into smaller files

Create separate files for different UI components:
- Control Panel - Query input, model selection, settings 
- Metrics Dashboard - Performance and quality metrics
- Progress Tracking - Progress bars and status indicators
- Results Display - Research results and analysis
- History & Analytics - Research history and content analysis

# Unit test 

- Unit test the code
- Use the `pytest` framework
- Use the `unittest` framework

```
ai-researcher/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # pytest configuration and fixtures
│   ├── test_utils.py                  # Test utility functions
│   ├── test_models.py                 # Test data models
│   ├── test_graph.py                  # Test LangGraph workflow
│   ├── test_analytics.py              # Test analytics functions
│   ├── test_export.py                 # Test export functionality
│   ├── test_config.py                 # Test configuration
│   └── test_integration.py            # Integration tests
├── test_requirements.txt              # Test dependencies
└── pytest.ini                        # pytest configuration
```

# Compare our code with Grok's deep research & Gemini's deep research

# Refactor the code 

Issue: `research_gpt.py` is too long and needs to be refactored.

```
research-gpt/
├── research_gpt.py              # Main application file
├── research_gpt_config.py       # Configuration and constants
├── research_gpt_utils.py        # Utility functions
├── research_gpt_models.py       # Data models and types
├── research_gpt_graph.py        # LangGraph workflow
├── research_gpt_ui.py          # Streamlit UI components
├── research_gpt_analytics.py    # Analytics and metrics functions
└── research_gpt_export.py       # Export functionality
```

# Try with bigger models 

# Try with bigger window sizes 


# Use pandas to create CSV file

Assume that pandas is available, if not, then quit the app.

```
            if PANDAS_AVAILABLE: -> don't check for pandas, just use it
                import pandas as pd
                csv_df = pd.DataFrame(csv_data)
                csv_string = csv_df.to_csv(index=False)
            else:
                # Fallback CSV creation without pandas
                csv_string = "Query,Timestamp,Model,Sources_Count,Response_Length,Total_Time,Total_Tokens\n"
                csv_string += f'"{query}","{datetime.now().isoformat()}","{model_used}",{len(response_state["sources"])},{len(str(response_state["response"]))},{total_time},{sum(step["total_tokens"] for step in response_state.get("step_metrics", {}).values())}'
```

# Implementation of a 3-Column Layout for the ResearchGPT App

Current UI/UX is basic and needs enhancements:
- Only 1 (or 2) column layout

Key Improvements in this 3-Column Layout:

Left Column (25% width) - Control Panel:
    - Clean input area with better text area
    - Model selection dropdown (addresses your backlog item)
    - Logging controls (console, file, performance)
    - Quick actions (clear results, view logs)
    - Settings and configuration

Middle Column (50% width) - Main Content:
    - Prominent research results display
    - Dynamic progress tracking with visual indicators
    - Collapsible sources section
    - Welcome message when idle
    - Better typography and spacing

Right Column (25% width) - Metrics Dashboard:
    - Real-time performance metrics in cards
    - Detailed expandable metrics section
    - System information
    - Clean, organized layout

# New features to add

🔍 Search & Content Enhancements
📊 Enhanced Metrics Dashboard
📈 Research History & Comparison
🎨 Content Analysis & Insights

# Users can choose the model to use

Currently, the app uses the Deepseek model by default.

Users can select from a dropdown menu to choose different models:

```
.venv vuhung@vhM1  ~/Desktop/ollama-playground/ai-researcher   main ±  ollama list
NAME                               ID              SIZE      MODIFIED     
mistral:latest                     3944fe81ec14    4.1 GB    4 days ago      
gemma3:27b                         a418f5838eaf    17 GB     9 days ago      
qwen2.5:3b                         357c53fb659c    1.9 GB    12 days ago     
phi3:mini                          4f2222927938    2.2 GB    12 days ago     
gemma:2b                           b50d6c999e59    1.7 GB    12 days ago     
qwen2.5:7b                         845dbda0ea48    4.7 GB    2 weeks ago     
deepseek-r1:8b                     6995872bfe4c    5.2 GB    2 weeks ago     
magistral:latest                   5dd7e640d9d9    14 GB     3 weeks ago     
llama3.1:8b                        46e0c10c039e    4.9 GB    3 months ago    
deepseek-r1:1.5b                   a42b25d8c10a    1.1 GB    4 months ago    
```

# Add a flag to turn on/off loggings 

- console logging on/off
- Add a flag to turn on/off file logging
- Add a flag to turn on/off performance logging

# Creat and update `CHANGELOG.md` ✅

- Describe the changes made in the codebase ✅
- Scan for recent edits and summarize them ✅
- Include the date and time of changes ✅
- Based on Claude's local changes ✅

# Show performance in terms of tokens per second 

- in streamlit app UI 
- in the console log

# Python Logging and Profiling

Print to console and log file:
- Number of tokens processed
- Time taken for processing
- Tokens per second
- Show the number of tokens processed
- Show the time taken for processing

for each steps 

```

 Search ✅

📊 Analyze ✅

📝 Summarize ✅

✨ Generate ✅
``` 

Log file saved to `logs/log.txt`

# Show AI research progress status

sample: show a man is running to show it is in progress


# Explain main components of the codebase

- LangGraph for state management
- LangChain for model and prompt management
- Tavily for web search
- Streamlit for the web interface
- dotenv for environment variable management
- Ollama for the Deepseek model
- Python's venv for virtual environment management

Save to `CORE-COMPONENTS.md`

# Update README.md

- mention the use of sample-dot-env for environment variables
- add instructions for setting up the Tavily API key
- how to use `deactivate` command to exit the virtual environment
