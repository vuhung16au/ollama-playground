# AI Scraper 🤖

A powerful AI-powered web scraper and question-answering system that allows you to chat with any website! This application uses advanced AI technology to extract content from websites and answer your questions about that content in natural language.

## 🎯 What is this Program?

This is a **Retrieval-Augmented Generation (RAG)** system that combines:

- **Web Scraping**: Automatically extracts content from any website URL
- **AI Processing**: Uses Llama 3.2 to understand and process the content
- **Smart Search**: Finds the most relevant information for your questions
- **Natural Q&A**: Answers your questions based on the website's content

### Key Features:
- 🌐 **Universal Web Scraping**: Works with any website URL
- 🧠 **AI-Powered Understanding**: Uses Llama 3.2 for intelligent content processing
- 🔍 **Smart Search**: Finds relevant information quickly using vector similarity
- 💬 **Natural Language Q&A**: Ask questions in plain English
- 🎨 **Beautiful Web Interface**: Clean, chat-like interface built with Streamlit
- ⚡ **Real-time Processing**: Get answers instantly

## 🛠️ Installation Guide

### Prerequisites

- **Python 3.9** (required for compatibility with dependencies)
- **Git** (to clone the repository)
- **Ollama** (for running AI models locally)

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd ai-scraper
```

### Step 2: Set Up Python Virtual Environment

Create and activate a virtual environment named `.venv`:

```bash
# Create virtual environment
python3.9 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

**Important**: Always activate the virtual environment before working on the project:
```bash
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

### Step 3: Install Python Dependencies

With your virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

### Step 4: Install and Set Up Ollama

1. **Install Ollama** from the [official website](https://ollama.com/)

2. **Pull the Llama 3.2 model**:
```bash
ollama pull llama3.2
```

3. **Start Ollama service** (if not already running):
```bash
ollama serve
```

## 🚀 Running the Application

### Local Development

1. **Ensure your virtual environment is activated**:
```bash
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

2. **Start the Streamlit application**:
```bash
streamlit run ai_scraper.py
```

3. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

### How to Use

1. **Enter a website URL** in the input field (e.g., `https://example.com`)
2. **Wait for processing** - the app will scrape and analyze the website content
3. **Ask questions** in the chat interface about the website's content
4. **Get AI-powered answers** based on the website's information

## 🌐 Deployment Options

### Option 1: Streamlit Cloud (Recommended for Beginners)

1. **Push your code to GitHub**:
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository and main file (`ai_scraper.py`)
   - Deploy!

**Note**: Streamlit Cloud has limitations with Ollama. You'll need to use cloud-based AI services instead.

### Option 2: Railway Deployment

1. **Create a Railway account** at [railway.app](https://railway.app)

2. **Connect your GitHub repository**

3. **Add environment variables**:
   - `OLLAMA_HOST`: Your Ollama server URL
   - `OLLAMA_MODEL`: `llama3.2`

4. **Deploy automatically** from your GitHub repository

### Option 3: Heroku Deployment

1. **Create a `Procfile`**:
```
web: streamlit run ai_scraper.py --server.port=$PORT --server.address=0.0.0.0
```

2. **Add `setup.sh`** for Ollama installation:
```bash
#!/bin/bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2
```

3. **Deploy to Heroku**:
```bash
heroku create your-app-name
git push heroku main
```

### Option 4: Docker Deployment

1. **Create a `Dockerfile`**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "ai_scraper.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Build and run**:
```bash
docker build -t ai-scraper .
docker run -p 8501:8501 ai-scraper
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom configuration:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Customizing the AI Model

To use a different Ollama model:

1. **Pull the model**:
```bash
ollama pull <model-name>
```

2. **Update the code** in `ai_scraper.py`:
```python
embeddings = OllamaEmbeddings(model="<model-name>")
model = OllamaLLM(model="<model-name>")
```

## 🚨 Troubleshooting

### Common Issues

1. **"Connection refused" error**:
   - Ensure Ollama is running: `ollama serve`
   - Check if the model is installed: `ollama list`

2. **Python version issues**:
   - Use Python 3.9: `python3.9 --version`
   - Recreate virtual environment with correct Python version

3. **Missing dependencies**:
   - Activate virtual environment: `source .venv/bin/activate`
   - Reinstall requirements: `pip install -r requirements.txt`

4. **Web scraping fails**:
   - Some websites block automated access
   - Try different websites or check website's robots.txt

### Performance Tips

- **Reduce chunk size** for faster processing
- **Use smaller AI models** for quicker responses
- **Limit website size** for better performance

## 📚 Additional Resources

- **Video Tutorial**: [YouTube Guide](https://youtu.be/eLV1R6ORRyU)
- **AI Scraper Logic**: [Complete Guide](AI-SCRAPER-LOGIC.md)
- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io/)
- **Ollama Documentation**: [ollama.ai/docs](https://ollama.ai/docs)
- **LangChain Documentation**: [python.langchain.com](https://python.langchain.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Happy Scraping! 🚀**

*Built with ❤️ using Streamlit, LangChain, and Ollama*