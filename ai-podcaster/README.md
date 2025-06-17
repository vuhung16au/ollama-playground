# AI Podcaster

An AI-powered podcaster that converts text to speech using Kokoro, LangChain, and Streamlit.

This project utilizes the Deepseek model to generate audio content from text input, allowing users to create podcasts with AI-generated voices.

## Pre-requisites

Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the Deepseek model:

```bash
ollama pull deepseek-r1:8b
```

## Setup

This project requires Python 3.10. Set up the environment as follows:

1. Create a virtual environment named `.venv`:
   ```bash
   python3.10 -m venv .venv
   ```

1. Activate the virtual environment:
   ```bash
   # On macOS/Linux
   source .venv/bin/activate

   # On Windows
   .venv\Scripts\activate
   ```

1. Install the dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

This project provides two ways to use the AI Podcaster:

### 1. Streamlit Web App (Interactive)

Run the Streamlit app for an interactive web interface:

```bash
streamlit run ai_podcaster.py
```

This will open a web browser where you can:

- Enter text directly or upload files
- Choose from different language options
- Generate and download audio files
- View summaries in real-time

### 2. Command Line Interface (CLI)

For automated processing or batch operations, use the CLI version:

```bash
python ai_spotify.py
```

#### CLI Features

The CLI version supports both single file and batch processing with flexible step control:

1. **Single File Mode**: Process individual Markdown files
2. **Batch Mode**: Process entire folders of Markdown files
3. **Step-based Processing**: Run summarization and audio generation separately or together
4. **Summarizes content** using the Deepseek model
5. **Generates audio files** in supported languages
6. **Flexible output organization**

#### Processing Steps

The CLI now supports breaking the workflow into two distinct steps:

- **Step 1**: Summarize Markdown files and save as text (.txt) files
- **Step 2**: Convert text summaries to audio (.mp3) files
- **Step All**: Run both steps sequentially (default behavior)

#### CLI Configuration

The CLI uses the following default settings:

- **Default input folder**: `./inputs/`
- **Default output folder**: `./outputs/`
- **Supported languages**: 🇺🇸 American English
- **Audio format**: MP3 files at 24kHz
- **Summary format**: Plain text (.txt files)

#### CLI Usage Examples

##### Step-based Processing

The CLI now supports running individual steps or both together:

```bash
# Run only Step 1: Summarize markdown to text
python ai_spotify.py --step 1

# Run only Step 2: Convert text to audio
python ai_spotify.py --step 2

# Run both steps (default behavior)
python ai_spotify.py --step all
# or simply
python ai_spotify.py
```

##### Single File Processing

Process a single Markdown file with step control:

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

##### Batch Folder Processing

Process all Markdown files in a folder with step control:

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

##### Advanced Workflow Examples

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

#### Output Structure

The CLI organizes outputs differently based on processing mode:

##### Single File Mode Output Structure

```text
outputs/
├── summaries/
│   └── filename.txt        # Summary of the processed file
└── audio/
    └── filename.mp3        # Audio version of the summary
```

##### Batch Mode Output Structure

```text
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

#### CLI Output Examples

##### Example 1: Running Both Steps (Default)

```text
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

##### Example 2: Running Step 1 Only (Summarization)

```text
AI Podcaster CLI - Processor
============================================================
Processing mode: Step 1: Summarize Markdown to Text
Mode: Batch folder processing
Input folder: inputs/data-mining-real-world-applications
Output folder: outputs
Folder name: data-mining-real-world-applications
Step: 1
Languages: 🇺🇸 American English

Found 20 Markdown files:
  1. 01 Cross-selling and Up-selling.md
  2. 02 Data mining applications in Cross-selling and Up-selling.md
  ...

Processing 20 files automatically...

[1/20] Processing files...

============================================================
Processing: 01 Cross-selling and Up-selling.md (Step: 1)
============================================================
Input text length: 4256 characters (721 words)
Generating summary...
✅ Summary generated successfully with 312 words
Summary length: 1689 characters (312 words)
Summary preview: Cross-selling and up-selling represent fundamental strategies in modern business...
Summary saved to: outputs/summaries/data-mining-real-world-applications/01 Cross-selling and Up-selling.txt
✅ Step 1 completed: Summary saved to outputs/summaries/data-mining-real-world-applications/01 Cross-selling and Up-selling.txt

============================================================
PROCESSING COMPLETE
============================================================
Total files processed: 20/20
Summary files saved to: outputs/summaries/data-mining-real-world-applications

✅ Processing completed successfully!
```

##### Example 3: Running Step 2 Only (Audio Generation)

```text
AI Podcaster CLI - Processor
============================================================
Processing mode: Step 2: Convert Text to Audio
Mode: Batch folder processing
Input folder: inputs/data-mining-real-world-applications
Output folder: outputs
Folder name: data-mining-real-world-applications
Step: 2
Languages: 🇺🇸 American English

Found 20 Markdown files:
  1. 01 Cross-selling and Up-selling.md
  2. 02 Data mining applications in Cross-selling and Up-selling.md
  ...

Processing 20 files automatically...

[1/20] Processing files...

============================================================
Processing: 01 Cross-selling and Up-selling.md (Step: 2)
============================================================
STEP 2: Generating audio for 01 Cross-selling and Up-selling.txt
============================================================
Generating audio files...
Generating audio for 01 Cross-selling and Up-selling.mp3...
Audio saved to: outputs/audio/data-mining-real-world-applications/01 Cross-selling and Up-selling.mp3
✓ 🇺🇸 American English: 01 Cross-selling and Up-selling.mp3
✅ Step 2 completed: 1 audio files generated

============================================================
PROCESSING COMPLETE
============================================================
Total files processed: 20/20
Total audio files generated: 20
Audio files saved to: outputs/audio/data-mining-real-world-applications

✅ Processing completed successfully!
```

#### Command Line Options

- `--input-file FILE`: Process a single Markdown file
- `--input-folder FOLDER`: Process all Markdown files in a folder (default: `./inputs/`)
- `--output-folder FOLDER`: Set output directory (default: `./outputs/`)
- `--step {1,2,all}`: Processing step control:
  - `1`: Only summarize markdown to text
  - `2`: Only convert text to audio
  - `all`: Run both steps (default)
- Legacy options: `-d FOLDER`, `-o FOLDER` (still supported)

#### Supported File Formats

- **Input**: `.md`, `.markdown` files
- **Summary Output**: `.txt` files (plain text)
- **Audio Output**: `.mp3` files (24kHz, mono)

## Project Structure

```text
ai-podcaster/
├── ai_podcaster.py          # Streamlit web app
├── ai_spotify.py            # Command line interface (main CLI)
├── ai_podcaster_cli.py      # Legacy CLI interface
├── requirements.txt         # Python dependencies
├── inputs/                  # Input text files
│   ├── data-mining-real-world-applications/  # Sample data mining articles
│   │   ├── 01 Cross-selling and Up-selling.md
│   │   ├── 02 Data mining applications...md
│   │   └── ...
│   └── input.md            # Default legacy CLI input file
├── outputs/                 # Generated content
│   ├── summaries/          # Text summaries
│   │   └── folder-name/    # Organized by input folder
│   └── audio/              # Generated audio files
│       └── folder-name/    # Organized by input folder
└── audios/                 # Legacy audio output directory
    └── audio.wav           # Legacy generated audio files
```

## Troubleshooting

- **Input file not found**: Ensure input files exist when using the CLI
- **Audio generation fails**: Check that you have sufficient disk space and write permissions
- **Model errors**: Verify that Ollama is running and the Deepseek model is installed
- **Dependency issues**: Make sure all requirements are installed in your virtual environment