# AI Podcaster - Streamlit Web Application

The `ai_podcaster.py` file provides an interactive web interface for converting text to speech using AI-powered summarization and audio generation.

## Overview

This is a Streamlit-based web application that allows users to:
- Enter text directly or upload files
- Choose from different language options
- Generate AI-powered summaries
- Convert text to high-quality audio files
- Download generated audio content

## How to Use

### Starting the Application

1. **Activate your virtual environment** (if using one):
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

2. **Run the Streamlit app**:
   ```bash
   streamlit run ai_podcaster.py
   ```

3. **Access the web interface**: The application will automatically open in your default web browser, typically at `http://localhost:8501`

### Using the Web Interface

1. **Select Language**: Choose from the available language options in the dropdown menu
   - 🇬🇧 British English (currently supported)

2. **Enter Text**: Use the text area to input the content you want to process
   - You can paste text directly
   - The text area supports large amounts of content

3. **Optional Summarization**: Check the "Summarize text" checkbox if you want the AI to create a summary before generating audio
   - When enabled, the AI will create a concise summary (under 600 words)
   - The summary maintains a conversational tone and is accessible to general audiences

4. **Generate Audio**: Click the "Generate Audio" button to start the process
   - The application will process your text (with optional summarization)
   - Audio generation will begin using the Kokoro pipeline
   - Progress will be displayed in the interface

5. **Download Audio**: Once generation is complete, an audio player will appear
   - You can preview the audio directly in the browser
   - The audio file is automatically saved to the `./audios/` directory as `audio.wav`

## Supported Languages

Currently supported languages:
- 🇬🇧 British English (`b`)

Note: Additional languages are configured but commented out in the code:
- 🇺🇸 American English
- 🇯🇵 Japanese
- 🇨🇳 Mandarin Chinese
- 🇪🇸 Spanish
- 🇫🇷 French
- 🇮🇳 Hindi
- 🇮🇹 Italian
- 🇧🇷 Brazilian Portuguese

## Output Files

### Audio Output
- **Location**: `./audios/` directory
- **Format**: WAV file (24kHz sample rate)
- **Filename**: `audio.wav`
- **Voice**: Uses the `af_heart` voice from the Kokoro pipeline

### Summary Processing
When summarization is enabled:
- The AI creates a summary under 600 words
- Maintains conversational tone
- Focuses on key points and main takeaways
- Removes markdown formatting and thinking tags
- The summarized text is used for audio generation

## Technical Details

### Dependencies
- **Streamlit**: Web interface framework
- **Kokoro**: Text-to-speech pipeline
- **LangChain**: AI model integration
- **Ollama**: Local AI model (Deepseek)
- **SoundFile**: Audio file handling
- **NumPy**: Audio processing

### Configuration
- **Summary Word Limit**: 600 words maximum
- **Audio Sample Rate**: 24kHz
- **Voice**: `af_heart` (Kokoro voice)
- **Model**: `deepseek-r1:8b` (via Ollama)

### Summary Template
The AI uses a structured prompt to create summaries that:
1. Identify the central argument or main topic
2. List 2-3 supporting key points or pieces of evidence
3. Conclude with the main takeaway or implication
4. Maintain conversational tone for general audiences

## Troubleshooting

### Common Issues

1. **Application won't start**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check that Ollama is running and the Deepseek model is available
   - Verify your virtual environment is activated

2. **Audio generation fails**:
   - Check that you have sufficient disk space
   - Ensure write permissions for the `./audios/` directory
   - Verify the Kokoro pipeline is properly configured

3. **Model errors**:
   - Ensure Ollama is running: `ollama serve`
   - Verify the Deepseek model is installed: `ollama pull deepseek-r1:8b`
   - Check system resources (memory, CPU)

4. **Browser issues**:
   - Try refreshing the page
   - Check browser console for JavaScript errors
   - Ensure you're using a modern browser (Chrome, Firefox, Safari, Edge)

### Performance Tips

- For large text inputs, consider enabling summarization to reduce processing time
- The application processes audio in chunks for better memory management
- Audio files are generated in WAV format for quality, then converted to MP3 if needed

## File Structure

```
ai-podcaster/
├── ai_podcaster.py          # This Streamlit application
├── audios/                  # Generated audio files
│   └── audio.wav           # Current audio output
├── requirements.txt         # Python dependencies
└── README.md               # Main project documentation
```

## Integration with Other Tools

This Streamlit app is part of a larger AI Podcaster project that includes:
- `ai_spotify.py`: Command-line interface for batch processing
- `ai_podcaster_cli.py`: Legacy CLI interface
- Various input/output directories for file management

The web interface is ideal for:
- Interactive content creation
- Quick audio generation
- Testing and experimentation
- User-friendly content processing 