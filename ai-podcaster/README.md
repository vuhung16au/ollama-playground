# AI Podcaster
An AI-powered podcaster that converts text to speech using Kokoro, LangChain, and Streamlit.

You can watch the video on how it was built on my [YouTube](https://youtu.be/h5D4rDNe8xk).

# Pre-requisites
Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the Deepseek model:

```bash
ollama pull deepseek-r1:8b
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

# Run
Run the Streamlit app:

```bash
streamlit run ai_podcaster.py
```