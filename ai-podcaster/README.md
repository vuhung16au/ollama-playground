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
python ai_podcaster_cli.py
```

#### CLI Features

The CLI version automatically:

1. **Reads input text** from `./inputs/input.md`
2. **Summarizes the content** using the Deepseek model (limited to 600 words)
3. **Saves the summary** to `./outputs/summary.txt`
4. **Generates audio files** in supported languages to `./audios/` directory

#### CLI Configuration

The CLI uses the following default settings:

- **Input file**: `./inputs/input.md`
- **Output directory**: `./audios/`
- **Summary directory**: `./outputs/`
- **Summary word limit**: 600 words
- **Supported languages**: 🇺🇸 American English
- **Audio format**: WAV files at 24kHz

#### Using the CLI

1. **Prepare your input**: Place your text content in `./inputs/input.md`

   ```bash
   # Example: Copy your content to the input file
   cp your-content.md ./inputs/input.md
   ```

2. **Run the CLI**:

   ```bash
   python ai_podcaster_cli.py
   ```

3. **Check the outputs**:
   - Summary: `./outputs/summary.txt`
   - Audio: `./audios/audio_a.wav` (American English)

#### CLI Output Example

```text
AI Podcaster CLI
==================================================
Reading input from: ./inputs/input.md
Input text length: 5847 characters
Summarizing text...
Summary length: 542 characters
Summary:
------------------------------
Vietnam's economy has transformed remarkably since 1975...
------------------------------
Summary saved to: ./outputs/summary.txt

Generating audio files in 1 languages...
Generating audio for audio_a.wav...
✓ 🇺🇸 American English: audio_a.wav

Completed! Generated 1 audio files:
  - 🇺🇸 American English: ./audios/audio_a.wav
```

#### Customizing the CLI

To modify the CLI behavior, you can edit the configuration variables at the top of `ai_podcaster_cli.py`:

- `INPUT_FILE`: Change the input file path
- `AUDIOS_DIRECTORY`: Change the audio output directory
- `SUMMARISATION_FOLDER`: Change the summary output directory
- `SUMMARY_WORD_LIMIT`: Adjust the summary length limit
- `supported_languages`: Add or modify language options

## Project Structure

```text
ai-podcaster/
├── ai_podcaster.py          # Streamlit web app
├── ai_podcaster_cli.py      # Command line interface
├── requirements.txt         # Python dependencies
├── inputs/                  # Input text files
│   ├── input.md            # Default CLI input file
│   └── input-vn-eco.md     # Example Vietnamese economy content
├── outputs/                 # Generated summaries
│   └── summary.txt         # CLI output summary
└── audios/                 # Generated audio files
    └── audio.wav           # Generated audio files
```

## Troubleshooting

- **Input file not found**: Ensure `./inputs/input.md` exists when using the CLI
- **Audio generation fails**: Check that you have sufficient disk space and write permissions
- **Model errors**: Verify that Ollama is running and the Deepseek model is installed
- **Dependency issues**: Make sure all requirements are installed in your virtual environment