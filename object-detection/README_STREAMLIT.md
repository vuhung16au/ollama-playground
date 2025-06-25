# Object Detection Streamlit App

This directory contains both a command-line object detection script and a Streamlit web application for interactive object detection using Ollama's Llama3.2-vision model.

## Files

- `object_detection.py` - Command-line script for batch processing images
- `app_object_detection.py` - Streamlit web application for interactive use
- `requirements.txt` - Python dependencies
- `images/` - Sample images for testing
- `logs/` - Log files from object detection runs

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure Ollama is running and has the Llama3.2-vision model:
```bash
ollama pull llama3.2-vision
```

## Usage

### Command Line
Run the batch processing script:
```bash
python object_detection.py
```

### Streamlit Web App
Launch the interactive web application:
```bash
streamlit run app_object_detection.py
```

Then open your browser to `http://localhost:8501`

## Features

### Web App Features:
- 🖼️ Upload images or use sample images
- 🔍 Real-time object detection
- 📊 Structured results display
- ⏱️ Execution time tracking
- 📱 Responsive web interface
- 🎨 Object color identification
- 🔢 Object counting

### Command Line Features:
- 📁 Batch processing of multiple images
- 📝 Detailed logging
- 🗂️ Automatic file discovery
- ⚡ High-performance processing

## Sample Images

The app includes sample images in the `images/` folder:
- `apple.png`
- `java.png` 
- `tiger.png`

## Model Requirements

This application requires:
- Ollama running locally
- Llama3.2-vision model downloaded
- Sufficient system resources for vision model inference
