# Chat with PDF
A vide summarization system using Gemma 3, LangChain, and Streamlit. 

You can watch the video on how it was built on my [YouTube](https://youtu.be/gDATAZEi5SE).

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
streamlit run video_summary.py
```