# Required Libraries

This document explains the Python packages required for the video summarization project.

## Dependencies

### streamlit

**Purpose**: Web application framework for creating interactive user interfaces

**Usage**: Provides the web interface for uploading videos and displaying summaries. Streamlit makes it easy to create a clean, user-friendly frontend without extensive web development knowledge.

### langchain_core

**Purpose**: Core components and abstractions for the LangChain framework

**Usage**: Provides the foundational classes and interfaces needed for building applications with large language models. This includes base classes for prompts, chains, and other core LangChain components.

### langchain_community

**Purpose**: Community-contributed integrations and tools for LangChain

**Usage**: Extends LangChain with additional integrations and utilities developed by the community. This package provides access to various third-party services and tools that work with LangChain.

### langchain_ollama

**Purpose**: LangChain integration for Ollama models

**Usage**: Enables seamless integration between LangChain and locally-running Ollama models. This package allows the application to communicate with the Gemma 3 model through LangChain's standardized interface.

### opencv-python

**Purpose**: Computer vision and image processing library

**Usage**: Handles video processing tasks including reading video files, extracting frames at specified intervals, and saving frames as image files. OpenCV provides the core functionality for breaking down videos into individual frames for analysis.

## Installation

Install all dependencies using:

```bash
pip install -r requirements.txt
```

## Version Notes

- These packages are designed to work together for AI-powered video analysis
- The specific versions may need to be updated based on compatibility requirements
- Ensure Ollama is installed separately on your system before running the application
