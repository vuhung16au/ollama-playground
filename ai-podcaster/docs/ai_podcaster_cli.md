# AI Podcaster CLI - Legacy Command Line Interface

The `ai_podcaster_cli.py` file provides a simple, legacy command-line interface for basic text-to-speech processing with AI-powered summarization.

## Overview

This is the original CLI tool for the AI Podcaster project, offering:
- **Simple single-file processing**: Process one Markdown file at a time
- **Fixed input/output structure**: Uses predefined directories and filenames
- **Basic workflow**: Read → Summarize → Generate Audio
- **Minimal configuration**: No command-line arguments needed
- **Legacy compatibility**: Maintains original project structure

## How to Use

### Basic Usage

The CLI is designed to be simple and requires no command-line arguments:

```bash
python ai_podcaster_cli.py
```

### Setup Requirements

1. **Prepare input file**: Place your Markdown content in `./inputs/input.md`
2. **Run the script**: Execute the Python script
3. **Check outputs**: Results are automatically saved to predefined locations

### Workflow

The CLI follows a simple 3-step process:

1. **Read Input**: Reads content from `./inputs/input.md`
2. **Summarize**: Creates an AI-generated summary (max 1200 words)
3. **Generate Audio**: Converts summary to audio in supported languages

## Command Line Options

**None** - This CLI tool is designed for simplicity and uses no command-line arguments.

All configuration is handled through:
- Fixed file paths in the code
- Predefined output directories
- Hardcoded settings

## Output Files

### Summary Output
- **Location**: `./outputs/summary.txt`
- **Format**: Plain text (.txt)
- **Content**: AI-generated summary of the input text
- **Word Limit**: Maximum 1200 words

### Audio Output
- **Location**: `./audios/` directory
- **Format**: MP3 files (converted from WAV)
- **Sample Rate**: 24kHz
- **Voice**: `af_heart` (Kokoro voice)
- **Files**: One audio file per supported language
  - `audio_a.mp3` - American English

### Input Requirements
- **Location**: `./inputs/input.md`
- **Format**: Markdown (.md) file
- **Content**: Any text content to be processed

## Example Output

```
AI Podcaster CLI
==================================================
Reading input from: ./inputs/input.md
Input text length: 3847 characters

Summarizing text...
Summary length: 1542 characters

Summary:
------------------------------
Cross-selling and up-selling represent fundamental strategies in modern business...
[Summary content here]
------------------------------
Summary saved to: ./outputs/summary.txt

Generating audio files in 1 languages...

Generating audio for audio_a.mp3...
Audio saved to: ./audios/audio_a.mp3
✓ 🇺🇸 American English: audio_a.mp3

Completed! Generated 1 audio files:
  - 🇺🇸 American English: ./audios/audio_a.mp3
```

## Supported Languages

Currently supported languages:
- 🇺🇸 American English (`a`)

Note: British English is configured but commented out in the code.

## Technical Details

### Dependencies
- **Kokoro**: Text-to-speech pipeline
- **LangChain**: AI model integration
- **Ollama**: Local AI model (Deepseek)
- **Pydub**: Audio format conversion
- **SoundFile**: Audio file handling
- **NumPy**: Audio processing

### Configuration
- **Input File**: `./inputs/input.md` (fixed path)
- **Summary Output**: `./outputs/summary.txt` (fixed path)
- **Audio Output**: `./audios/` directory (fixed path)
- **Summary Word Limit**: 1200 words maximum
- **Audio Sample Rate**: 24kHz
- **Audio Format**: MP3 (converted from WAV)
- **Voice**: `af_heart` (Kokoro voice)
- **Model**: `deepseek-r1:8b` (via Ollama)

### Summary Template
The AI uses a structured prompt to create summaries that:
1. Identify the central argument or main topic
2. List 2-3 supporting key points or pieces of evidence
3. Conclude with the main takeaway or implication
4. Use clear and concise language
5. Avoid jargon and complex terminology
6. Use a friendly and engaging tone
7. Provide a summary that is easy to understand for a general audience
8. Use plaintext format without any special formatting or tags

## File Structure

```
ai-podcaster/
├── ai_podcaster_cli.py      # This legacy CLI application
├── inputs/
│   └── input.md            # Input file (must exist)
├── outputs/
│   └── summary.txt         # Generated summary
└── audios/                 # Generated audio files
    └── audio_a.mp3         # American English audio
```

## Usage Workflow

### Step 1: Prepare Input
1. Create the `inputs/` directory if it doesn't exist
2. Place your Markdown content in `inputs/input.md`
3. Ensure the file contains the text you want to process

### Step 2: Run Processing
```bash
python ai_podcaster_cli.py
```

### Step 3: Check Results
1. **Summary**: Check `outputs/summary.txt` for the AI-generated summary
2. **Audio**: Check `audios/audio_a.mp3` for the generated audio file

## Troubleshooting

### Common Issues

1. **Input file not found**:
   ```
   Error: Input file './inputs/input.md' not found.
   ```
   - **Solution**: Create the `inputs/` directory and add an `input.md` file

2. **Audio generation fails**:
   - Check that you have sufficient disk space
   - Ensure write permissions for the `audios/` directory
   - Verify the Kokoro pipeline is properly configured

3. **Model errors**:
   - Ensure Ollama is running: `ollama serve`
   - Verify the Deepseek model is installed: `ollama pull deepseek-r1:8b`
   - Check system resources (memory, CPU)

4. **Permission errors**:
   - Ensure write permissions for `outputs/` and `audios/` directories
   - Check if directories exist or can be created

### Error Handling

The CLI includes basic error handling:
- **File not found**: Exits with error message and code 1
- **File read errors**: Displays specific error messages
- **Audio generation errors**: Continues processing other languages if one fails

## Advantages and Limitations

### Advantages
- **Simple to use**: No command-line arguments needed
- **Predictable**: Fixed file structure and naming
- **Lightweight**: Minimal dependencies and configuration
- **Legacy support**: Maintains original project structure

### Limitations
- **Single file only**: Cannot process multiple files
- **Fixed paths**: No customization of input/output locations
- **No batch processing**: One file at a time
- **Limited language support**: Only American English by default
- **No logging**: No detailed logs or performance metrics
- **No step control**: Cannot run summarization or audio generation separately

## Migration to Advanced CLI

For more advanced features, consider migrating to `ai_spotify.py`:

### From Legacy CLI to Advanced CLI

**Legacy CLI**:
```bash
# Prepare input file
echo "# My content" > inputs/input.md
# Run processing
python ai_podcaster_cli.py
```

**Advanced CLI equivalent**:
```bash
# Process the same file with more options
python ai_spotify.py --input-file inputs/input.md --step all
```

### Advanced CLI Benefits
- **Multiple files**: Process entire folders
- **Custom paths**: Specify input/output directories
- **Step control**: Run summarization or audio generation separately
- **Better logging**: Detailed logs and performance metrics
- **More languages**: Easier to add language support

## Integration with Other Tools

This legacy CLI is part of the AI Podcaster project alongside:
- `ai_podcaster.py`: Streamlit web interface for interactive use
- `ai_spotify.py`: Advanced CLI with batch processing and step control

The legacy CLI is ideal for:
- Simple, one-off content processing
- Learning the basic workflow
- Legacy system compatibility
- Minimal setup requirements 