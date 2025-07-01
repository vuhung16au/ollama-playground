# Chat with Data using Ollama and LangChain

A Python application that allows you to have natural language conversations with your CSV data using Ollama and LangChain. Available in both command-line and web interface versions.

## Features

- 🤖 Chat with your CSV data using natural language
- 🚀 Powered by Ollama for local LLM inference
- 📊 Built with LangChain and Pandas for data analysis
- 💬 Available in two versions:
  - **Command-line interface** (`chat-with-data.py`) - Simple terminal-based interaction
  - **Web interface** (`app-chat-with-data.py`) - Modern Streamlit web app with GUI
- 🔒 Runs completely locally - no data sent to external APIs
- 📁 File upload support (Streamlit version)
- 💡 Smart sample prompts based on your data structure
- 📈 Interactive data preview and exploration

## Prerequisites

Before setting up the project, make sure you have:

1. **Python 3.8+** installed on your system
2. **Ollama** installed and running
   - Install from: <https://ollama.ai/>
   - Pull a model (e.g., `ollama pull mistral`)

## Setup Instructions

### 1. Clone or Download the Project

```bash
# If you have the project in a git repository
git clone <repository-url>
cd chat-with-csv

# Or if you downloaded the files, navigate to the project directory
cd path/to/chat-with-csv
```

### 2. Create Python Virtual Environment

Create a virtual environment named `.venv`:

```bash
# Create virtual environment
python3 -m venv .venv
```

### 3. Activate Virtual Environment

**On macOS/Linux:**

```bash
source .venv/bin/activate
```

**On Windows:**

```bash
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt, indicating the virtual environment is active.

### 4. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 5. Prepare Your CSV File

Place your CSV file in the project directory. By default, the script looks for `OnlineRetail.csv`, but you can modify the `csv_file` variable in `chat-with-data.py` to point to your specific file.

### 6. Start Ollama Server

Make sure Ollama is running and you have pulled the required model:

```bash
# Start Ollama (if not already running)
ollama serve

# In another terminal, pull the mistral model (or your preferred model)
ollama pull mistral
```

## Usage

### Option 1: Command-Line Version (chat-with-data.py)

#### Running the Application

With your virtual environment activated:

```bash
python chat-with-data.py
```

#### Example Interaction

```text
🚀 Starting CSV Chat with Ollama (mistral) 🚀
--------------------------------------------------
Successfully loaded 'OnlineRetail.csv' with 541909 rows and 8 columns.
DataFrame head:
   InvoiceNo StockCode                          Description  Quantity InvoiceDate   UnitPrice  CustomerID         Country
0     536365    85123A   WHITE HANGING HEART T-LIGHT HOLDER         6  2010-12-01        2.55     17850.0  United Kingdom
1     536365     71053                  WHITE METAL LANTERN         6  2010-12-01        3.39     17850.0  United Kingdom
2     536365    84406B       CREAM CUPID HEARTS COAT HANGER         8  2010-12-01        2.75     17850.0  United Kingdom
...

Your question (or 'exit'/'quit'): What are the top 5 best-selling products?
```

### Option 2: Streamlit Web Interface (app-chat-with-data.py)

#### For Developers: Installation

If you're setting up the development environment, follow the setup instructions above, then install Streamlit:

```bash
# Activate your virtual environment first
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Install all dependencies (including Streamlit)
pip install -r requirements.txt
```

#### For Users: Running the Web App

1. **Start Ollama server** (in one terminal):

   ```bash
   ollama serve
   ```

2. **Pull your desired model** (in another terminal):

   ```bash
   ollama pull mistral
   ```

3. **Launch the Streamlit app**:

   ```bash
   streamlit run app-chat-with-data.py
   ```

4. **Open your browser** to the URL shown (typically `http://localhost:8501`)

#### Streamlit App Features

**🎨 Modern Web Interface:**

- Clean, intuitive design with responsive layout
- Sidebar configuration panel
- Real-time status indicators

**📁 Flexible Data Loading:**

- Drag-and-drop CSV file upload
- One-click sample data loading (OnlineRetail.csv)
- Automatic data preview and structure analysis

**💡 Smart Sample Prompts:**

- Automatically generated prompts based on your data columns
- Generic prompts that work with any dataset
- Dataset-specific prompts (e.g., for retail data)
- Click-to-use prompt buttons

**🤖 Model Configuration:**

- Select from multiple Ollama models (mistral, llama2, codellama, gemma)
- Real-time model switching
- Setup instructions in the sidebar

**💬 Enhanced Chat Experience:**

- Beautiful chat history display
- Copy-paste friendly responses
- Clear chat functionality
- Error handling with helpful suggestions

### Sample Questions You Can Ask

- "What are the top 5 best-selling products?"
- "Show me the total revenue by country"
- "What's the average order value?"
- "How many unique customers do we have?"
- "What are the sales trends over time?"
- "Which products have the highest unit price?"

## Project Structure

```text
chat-with-data/
├── chat-with-data.py       # Command-line version
├── app-chat-with-data.py   # Streamlit web interface version
├── requirements.txt        # Python dependencies (includes Streamlit)
├── README.md              # This file
├── .venv/                 # Virtual environment (created during setup)
├── data/                  # Data directory
│   └── OnlineRetail.csv   # Sample dataset
└── chat-with-data.png     # Screenshot
```

## Configuration

### Changing the Model

**Command-line version:**
To use a different Ollama model, modify the `model_name` parameter in the `chat_with_csv()` function call at the bottom of `chat-with-data.py`:

```python
if __name__ == "__main__":
    csv_file = "your-file.csv"
    chat_with_csv(csv_file, model_name="llama2")  # Change model here
```

**Streamlit version:**
Simply select a different model from the dropdown in the sidebar. The app will reinitialize with the new model automatically.

### Using a Different CSV File

**Command-line version:**
Update the `csv_file` variable in the main section:

```python
if __name__ == "__main__":
    csv_file = "path/to/your/file.csv"  # Update this path
    chat_with_csv(csv_file, model_name="mistral")
```

**Streamlit version:**
Use the file uploader in the web interface to select any CSV file from your computer.

## Troubleshooting

### Common Issues

1. **"Ollama not found" error**
   - Ensure Ollama is installed and running (`ollama serve`)
   - Verify the model is pulled (`ollama pull mistral`)

2. **CSV file not found (Command-line version)**
   - Check the file path in the script
   - Ensure the CSV file is in the correct directory

3. **Module import errors**
   - Ensure virtual environment is activated
   - Re-run `pip install -r requirements.txt`

4. **Permission errors with dangerous code**
   - The script uses `allow_dangerous_code=True` for pandas operations
   - This is necessary for the agent to execute data analysis code

5. **Streamlit app won't start**
   - Check if port 8501 is already in use
   - Try running: `streamlit run app-chat-with-data.py --server.port 8502`

6. **File upload issues in Streamlit**
   - Ensure your CSV file is properly formatted
   - Check that the file size is reasonable (< 200MB recommended)
   - Try refreshing the page if upload seems stuck

### Performance Tips

- **For large datasets**: Consider using a subset of your data for faster processing
- **Model selection**: Smaller models (like mistral) are faster but may be less accurate
- **Streamlit performance**: Clear chat history periodically to maintain responsiveness

### Getting Help

If you encounter issues:

1. Check that all prerequisites are installed
2. Ensure your virtual environment is activated
3. Verify Ollama is running and the model is available
4. Check the error messages for specific guidance
5. For Streamlit issues, check the terminal output for detailed error messages

## Deactivating Virtual Environment

When you're done working with the project:

```bash
deactivate
```

This will return you to your system's default Python environment.

## Security Note

This application executes code generated by the LLM to analyze your data. While it runs locally and doesn't send data externally, be cautious when using it with sensitive data. The `allow_dangerous_code=True` parameter is required for the pandas agent to function but should be used responsibly.

## Quick Start Guide

### For End Users (Recommended: Streamlit Version)

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai/)
2. **Start Ollama**: `ollama serve`
3. **Pull a model**: `ollama pull mistral`
4. **Clone/download this project**
5. **Install dependencies**: `pip install -r requirements.txt`
6. **Run the app**: `streamlit run app-chat-with-data.py`
7. **Open browser**: Go to `http://localhost:8501`
8. **Upload your CSV** and start chatting!

### For Developers (Command-line Version)

1. Follow setup instructions above
2. **Run**: `python chat-with-data.py`
3. **Modify** the script to point to your CSV file

## Screenshots

![chat with data](chat-with-data.png)
