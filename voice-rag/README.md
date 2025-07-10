# Chat with PDF
A simple Voice RAG (Retrieval-Augmented Generation) system using Deepseek, LangChain, and Streamlit to chat with audio files and answer complex questions about them.

# Pre-requisites
Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the Deepseek model:

```bash
ollama pull deepseek-r1:8b
```

Create and activate a virtual environment named '.venv':

```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
# .venv\Scripts\activate  # On Windows
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

# Run

Run the Streamlit app:

```bash
streamlit run voice_rag.py
```