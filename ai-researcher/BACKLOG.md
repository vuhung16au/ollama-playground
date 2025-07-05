# Implementation of a 3-Column Layout for the AI Researcher App

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
