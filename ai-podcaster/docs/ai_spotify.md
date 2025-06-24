# AI Spotify - Advanced Command Line Interface

The `ai_spotify.py` file provides a powerful command-line interface for batch processing Markdown files into AI-generated summaries and audio content.

## Overview

This is the main CLI tool for the AI Podcaster project, offering:
- **Single file processing**: Process individual Markdown files
- **Batch folder processing**: Process entire directories of Markdown files
- **Step-based workflow**: Run summarization and audio generation separately or together
- **Flexible output organization**: Custom output directories and file organization
- **Comprehensive logging**: Detailed logs and performance metrics
- **Runtime tracking**: CSV-based performance monitoring

## How to Use

### Basic Usage

```bash
# Process a single file (both steps)
python ai_spotify.py --input-file inputs/article.md

# Process all files in a folder (both steps)
python ai_spotify.py --input-folder inputs/articles

# Process with custom output directory
python ai_spotify.py --input-folder inputs/articles --output-folder outputs/my-podcasts
```

### Step-Based Processing

The CLI supports breaking the workflow into two distinct steps:

#### Step 1: Summarization Only
```bash
# Summarize single file
python ai_spotify.py --input-file inputs/article.md --step 1

# Summarize all files in folder
python ai_spotify.py --input-folder inputs/articles --step 1
```

#### Step 2: Audio Generation Only
```bash
# Generate audio from existing summary
python ai_spotify.py --input-file inputs/article.md --step 2

# Generate audio for all existing summaries
python ai_spotify.py --input-folder inputs/articles --step 2
```

#### Both Steps (Default)
```bash
# Run both steps sequentially
python ai_spotify.py --input-file inputs/article.md --step all
# or simply
python ai_spotify.py --input-file inputs/article.md
```

## Command Line Options

### Input Options (Mutually Exclusive)

- `--input-file FILE`: Process a single Markdown file
  ```bash
  python ai_spotify.py --input-file inputs/my-article.md
  ```

- `--input-folder FOLDER`: Process all Markdown files in a folder (default: `./inputs/`)
  ```bash
  python ai_spotify.py --input-folder inputs/data-mining-articles
  ```

### Output Options

- `--output-folder FOLDER`: Set output directory (default: `./outputs/`)
  ```bash
  python ai_spotify.py --input-folder inputs/articles --output-folder outputs/podcasts
  ```

### Processing Control

- `--step {1,2,all}`: Processing step control
  - `1`: Only summarize markdown to text
  - `2`: Only convert text to audio
  - `all`: Run both steps (default)

### Legacy Options (Still Supported)

- `-d FOLDER`, `--folder FOLDER`: Legacy input folder option
- `-o FOLDER`, `--output FOLDER`: Legacy output folder option

## Usage Examples

### Single File Processing

```bash
# Basic single file processing (both steps)
python ai_spotify.py --input-file inputs/article.md

# Single file - Step 1 only (summarize only)
python ai_spotify.py --input-file inputs/article.md --step 1

# Single file - Step 2 only (audio generation only)
python ai_spotify.py --input-file inputs/article.md --step 2

# Single file with custom output folder
python ai_spotify.py --input-file inputs/article.md --output-folder outputs/my-content --step all

# Process specific file from data mining collection
python ai_spotify.py --input-file inputs/data-mining-real-world-applications/fraud-detection.md --step 1
```

### Batch Folder Processing

```bash
# Process all files in default inputs folder (both steps)
python ai_spotify.py --input-folder inputs/

# Batch processing - Step 1 only (summarize all files)
python ai_spotify.py --input-folder inputs/data-mining-real-world-applications --step 1

# Batch processing - Step 2 only (generate audio for all existing summaries)
python ai_spotify.py --input-folder inputs/data-mining-real-world-applications --step 2

# Process specific folder with both steps
python ai_spotify.py --input-folder inputs/data-mining-real-world-applications --step all

# Batch processing with custom output
python ai_spotify.py --input-folder inputs/articles --output-folder outputs/podcasts --step all

# Legacy commands (still supported)
python ai_spotify.py -d inputs/articles -o outputs/podcasts
```

### Advanced Workflow Examples

```bash
# Workflow 1: Summarize all files first, then generate audio later
python ai_spotify.py --input-folder inputs/articles --step 1
# ... review summaries if needed ...
python ai_spotify.py --input-folder inputs/articles --step 2

# Workflow 2: Process different folders separately
python ai_spotify.py --input-folder inputs/tech-articles --output-folder outputs/tech --step 1
python ai_spotify.py --input-folder inputs/business-articles --output-folder outputs/business --step 1
# Then generate audio for both
python ai_spotify.py --input-folder inputs/tech-articles --output-folder outputs/tech --step 2
python ai_spotify.py --input-folder inputs/business-articles --output-folder outputs/business --step 2

# Workflow 3: Quick single file processing
python ai_spotify.py --input-file inputs/urgent-article.md --step all
```

## Output Files

### Output Structure

The CLI organizes outputs differently based on processing mode:

#### Single File Mode Output Structure
```
outputs/
├── summaries/
│   └── filename.txt        # Summary of the processed file
└── audio/
    └── filename.mp3        # Audio version of the summary
```

#### Batch Mode Output Structure
```
outputs/
├── summaries/
│   └── folder-name/        # Named after input folder
│       ├── file1.txt       # Individual summaries
│       ├── file2.txt
│       └── file3.txt
└── audio/
    └── folder-name/        # Named after input folder
        ├── file1.mp3       # Individual audio files
        ├── file2.mp3
        └── file3.mp3
```

### File Formats

- **Input**: `.md`, `.markdown` files
- **Summary Output**: `.txt` files (plain text)
- **Audio Output**: `.mp3` files (24kHz, mono)

### Logging and Metrics

The CLI creates additional output files:

- **Logs**: `logs/ai_spotify.txt` - Detailed processing logs with timestamps
- **Metrics**: `metrics/runtime.csv` - Performance metrics including:
  - Input file name
  - Processing step
  - Start/end times
  - Duration in seconds
  - Model used for TTS

## Supported Languages

Currently supported languages:
- 🇺🇸 American English (`a`)

## Technical Details

### Dependencies
- **Kokoro**: Text-to-speech pipeline
- **LangChain**: AI model integration
- **Ollama**: Local AI model (llama3.2)
- **Pydub**: Audio format conversion
- **SoundFile**: Audio file handling
- **NumPy**: Audio processing

### Configuration
- **Audio Sample Rate**: 24kHz
- **Audio Format**: MP3 (converted from WAV)
- **Voice**: `af_heart` (Kokoro voice)
- **Model**: `llama3.2` (via Ollama)
- **Summary Style**: Conversational, podcast-friendly content

### Summary Template
The AI creates engaging, podcast-style summaries that:
- Start directly with the main topic
- Use natural, storytelling tone
- Focus on key insights and practical applications
- Make complex concepts accessible
- Structure content to flow logically
- Keep audiences engaged throughout
- Limit to single paragraph under 500 words
- Remove links and references

## Example Output

### Running Both Steps (Default)
```
AI Podcaster CLI - Processor
============================================================
Processing mode: Both Steps: Summarize and Generate Audio
Mode: Single file processing
Input file: inputs/data-mining-real-world-applications/fraud-detection.md
Output folder: outputs
Step: all
Languages: 🇺🇸 American English

Processing single file: fraud-detection.md

============================================================
Processing: fraud-detection.md (Step: all)
============================================================
STEP 1: Summarizing fraud-detection.md
============================================================
Input text length: 3847 characters (650 words)
Generating summary...
✅ Summary generated successfully with 284 words
Summary length: 1542 characters (284 words)
Summary preview: Fraud detection represents one of the most critical applications of data mining in financial services...
Summary saved to: outputs/summaries/fraud-detection.txt
✅ Step 1 completed: Summary saved to outputs/summaries/fraud-detection.txt

============================================================
STEP 2: Generating audio for fraud-detection.txt
============================================================
Generating audio files...
Generating audio for fraud-detection.mp3...
Audio saved to: outputs/audio/fraud-detection.mp3
✓ 🇺🇸 American English: fraud-detection.mp3
✅ Step 2 completed: 1 audio files generated

============================================================
PROCESSING COMPLETE
============================================================
Summary saved to: outputs/summaries
Audio files generated: 1
Audio files saved to: outputs/audio

✅ Processing completed successfully!
```

## Troubleshooting

### Common Issues

1. **Input file not found**:
   - Ensure input files exist and paths are correct
   - Check file permissions
   - Verify file extensions (.md, .markdown)

2. **Audio generation fails**:
   - Check disk space availability
   - Ensure write permissions for output directories
   - Verify Kokoro pipeline configuration

3. **Model errors**:
   - Ensure Ollama is running: `ollama serve`
   - Verify llama3.2 model is installed: `ollama pull llama3.2`
   - Check system resources (memory, CPU)

4. **Permission errors**:
   - Ensure write permissions for `logs/`, `metrics/`, and output directories
   - Check if directories exist or can be created

### Performance Optimization

- Use step-based processing for large batches
- Monitor `metrics/runtime.csv` for performance insights
- Consider processing smaller batches for memory management
- Review logs in `logs/ai_spotify.txt` for detailed error information

## File Structure

```
ai-podcaster/
├── ai_spotify.py            # This CLI application
├── inputs/                  # Input Markdown files
│   ├── data-mining-real-world-applications/
│   │   ├── 01 Cross-selling and Up-selling.md
│   │   ├── 02 Data mining applications...md
│   │   └── ...
│   └── input.md            # Default legacy CLI input file
├── outputs/                 # Generated content
│   ├── summaries/          # Text summaries
│   │   └── folder-name/    # Organized by input folder
│   └── audio/              # Generated audio files
│       └── folder-name/    # Organized by input folder
├── logs/                   # Processing logs
│   └── ai_spotify.txt      # Detailed logs with timestamps
└── metrics/                # Performance metrics
    └── runtime.csv         # Runtime statistics
```

## Integration with Other Tools

This CLI is part of the AI Podcaster project alongside:
- `ai_podcaster.py`: Streamlit web interface for interactive use
- `ai_podcaster_cli.py`: Legacy CLI interface for simple processing

The advanced CLI is ideal for:
- Batch processing large collections of articles
- Automated content pipeline workflows
- Performance monitoring and optimization
- Production-scale audio content generation 