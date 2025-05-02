# Text to SQL
A simple Text to SQL converter using Deepseek that connects to your database, reads the schema, and generates SQL queries based on the user's input.

You can watch the video on how it was built on my [YouTube](https://youtu.be/kem-v9MXuG4).

# Pre-requisites
Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the Deepseek model:

```bash
ollama pull deepseek-r1:8b
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```
To use your own database instead of the test SQLite one, just replace your own connection URL into the `db_url` variable in the code.
```python
db_url = "sqlite:///testdb.sqlite"
```

# Run
Run the Streamlit app:

```bash
streamlit run pdf_rag.py
```