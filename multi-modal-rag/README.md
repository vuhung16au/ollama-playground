# Chat with PDF
A simple Multimodal RAG (Retrieval-Augmented Generation) system using Gemma 3, LangChain, and Streamlit to chat with PDFs and answer complex questions about your local documents - even about images and tables.

You can watch the video on how it was built on my [YouTube](https://youtu.be/hBDNv47KCKo?si=qBhBVNjVu94Bj63j).

# Pre-requisites
Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the Gemma 3 model:

```bash
ollama pull gemma3:27b
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

# Run
Run the Streamlit app:

```bash
streamlit run multi_modal_rag.py
```