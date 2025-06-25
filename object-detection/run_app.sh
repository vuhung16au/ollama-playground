#!/bin/bash

# Object Detection Streamlit App Runner
# This script sets up and runs the Streamlit object detection app

echo "🔍 Object Detection Streamlit App"
echo "=================================="

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python -c "import streamlit, PIL, ollama, pydantic" 2>/dev/null; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ All dependencies are installed"
fi

# Check if Ollama is running
echo "🤖 Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "❌ Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    exit 1
fi

# Check if llama3.2-vision model is available
echo "🔍 Checking for Llama3.2-vision model..."
if ! ollama list | grep -q "llama3.2-vision"; then
    echo "❌ Llama3.2-vision model not found. Pulling model..."
    ollama pull llama3.2-vision
    if [ $? -ne 0 ]; then
        echo "❌ Failed to pull model"
        exit 1
    fi
    echo "✅ Model downloaded successfully"
else
    echo "✅ Llama3.2-vision model is available"
fi

# Create necessary directories
mkdir -p logs temp

echo "🚀 Starting Streamlit app..."
echo "📱 The app will open in your browser at http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the app"
echo ""

# Run the Streamlit app
streamlit run app_object_detection.py
