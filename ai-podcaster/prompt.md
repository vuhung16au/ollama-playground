# Add the following metrics

Memory Usage: Peak RAM consumption during inference
GPU Utilization: If using GPU acceleration
CPU Usage: Average CPU utilization percentage
Model Size: Disk space required for each model
Load Time: Time to load model into memory
Response Quality Score: Leave it as "TBC" (hard-coded)
Relevance Score: Leave it as "TBC" (hard-coded)

to the benchmark results:

token_benchmark_report.md
token_benchmark_report.json

# Add timestamp to .md and .json files

token_benchmark_report-{timestamp}.md
token_benchmark_results-{timestamp}.json

# Save the responses of the models to 

`./benchmarks/response-{model name}-{timestamp}.txt`

# Read the content of the file #file:Text-to-be-summarised.txt  and set it to 
`test_prompts` (only one long prompt)
``` 
test_prompts = [
    "Write a haiku about programming.",
    "Explain the difference between machine learning and deep learning in 150 words.",
    "Write a Python function that calculates the Fibonacci sequence up to n terms.",
    "Describe the plot of a science fiction movie in exactly 100 words."
]

``` 

# Print `model-tts` values to file `metrics/runtime.csv`

Current `model-tts` values: blank

New `model-tts` values: 

- if `step` = 1 then fill `model-tts` with the value `model = ChatOllama(model="deepseek-r1:8b")`
- if `step` = 2 then fill `model-tts` with the fixed value "Kokoro 80M"

# Add "model", "model-tts" to the header of `runtime.csv`

current header: 
input_file_name,step,start_time,end_time,duration_seconds

new header: 
input_file_name,step, model-tts, start_time,end_time,duration_seconds

# add model name as the suffixes to output files 

e.g 

when model: `deepseek-r1:8b`
Input file: `Cross-selling and Up-selling.md`

Output summary file: `Cross-selling and Up-selling_deepseek-r1-8b.txt`
Output audio file: `Cross-selling and Up-selling_deepseek-r1-8b.mp3`

# run time metrics 

I want to 

- print the results in a log file `logs/ai_spotify.txt` 
- print run time for each step (1, 2) for each input files 
- save the run time to file `metrics/runtime.csv` 

`metrics/runtime.csv` contains the following columns:

```
file_name, step, start_time, end_time, duration_seconds
```

# add command line options to the script to handle a whole folder of .md files or single .md file

e.g 

--input-file /path/to/file.md
default: .inputs/

--output-folder /path/to/output
default: 
./outputs/summaries
./outputs/audio

# break sccript into 2 steps 

our script has 2 steps 

1. summarize .md and save to .txt 
2. convert .txt to .mp3 

help me refactor to code 

- break it into 2 steps 
- have command line options to handle step 1, 2 at once or separately.

e.g 

## Run only step 1 (summarize markdown to text)
python ai_spotify.py --step 1

## Run only step 2 (convert text to MP3)
python ai_spotify.py --step 2

## Run both steps
python ai_spotify.py --step all

if --step is not specified, run both steps by default.

# Only one attempt to generate summary

we will use only attemp to generate summary 

pls remove `create_summary_prompt_with_length` function and related code 

# Improve prompt

summary_template = """
Shorten the following text. Your shortened text should:

- In less than {word_limit} words.
- Use clear and concise language.
- Avoid jargon and complex terminology.
- Use a friendly and engaging tone.
- Provide a response that is easy to understand for a general audience.
- Please respond in plain text only. Do not use any markdown formatting, bold text, italics, code blocks, or special characters for formatting. Just provide a simple, unformatted text response.
- IMPORTANT: Respond with PLAIN TEXT ONLY. No markdown, no formatting, no bold, no italics, no code blocks, no special characters. Just simple, clean text paragraphs.
- Do not use asterisks (*), underscores (_), backticks (`), hash symbols (#), or any other markdown syntax.
- Only respond with the shortened text, without any additional comments or explanations.
Text: {text}

"""

# strip_markdown 

Pls update `def clean_text(text):` function in `ai_spotify.py` to remove all markdown formats from the text.
Currently, it only removes some basic formats like bold and italic, but we need to remove all markdown formats manually.

Pls Use the `strip_markdown` (https://pypi.org/project/strip-markdown/) lib/function to clean the text by removing all markdown formats.

install it by running:
```
$ pip install strip_markdown
```

sample code:

```python
>>> import strip_markdown
>>>
>>> TXT: str = strip_markdown.strip_markdown(MD: str)
>>> strip_markdown.strip_markdown_file(MD_fn: str, TXT_fn: Optional[str])
```

TXT_fn is optional: default is <MD_fn>.md -> <MD_fn>.txt
If TXT_fn is a directory, <MD_fn>.txt is placed in that directory


# Add a config to disable/enalbe using of SUMMARY_WORD configs

SUMMARY_WORD_LIMIT = 1200
SUMMARY_WORD_MIN = 800

default of of this config is DISABLED.

# Better TTS model 

Currently I am using `kokoro` 80M model for text-to-speech.
suggest me an alternative model having better natural, human-like voice. 

My Top Recommendation:
Coqui XTTS v2 is your best bet because it offers:

Significantly more natural speech than Kokoro 80M
Good inference speed
Voice cloning capabilities
Active development and community support
Easy integration

## List 

1. Coqui TTS (XTTS v2)
2. Bark (Suno AI)
3. Tortoise TTS
4. Microsoft SpeechT5
5. MMS-TTS (Meta)

Recommendations Based on Use Case:

For Best Quality (Natural Human-like Voice):
Bark - Most natural with emotions
Coqui XTTS v2 - Excellent voice cloning
Tortoise TTS - Highest quality but slower

For Good Quality + Speed:
Coqui XTTS v2 - Best balance
SpeechT5 - Faster inference
MMS-TTS - Good for multilingual

For Voice Cloning/Customization:
Coqui XTTS v2 - Easiest to use
Bark - Good character voices
Tortoise TTS - Highest fidelity cloning

# Step 11 Which model? 

Currently I am using `deepseek-r1:8b` to summarise text. 

What I want to do is to reduce the text 

Input: ~5000 words 
shortened text: between 

SUMMARY_WORD_LIMIT = 2000
SUMMARY_WORD_MIN = 1000

what local LLM models (using with ollama) should I use? 

# Download and test these models:
ollama pull deepseek-r1:14b        # Upgrade from your current 8B
ollama pull llama3.2:3b            # Fast and efficient
ollama pull qwen2.5:7b             # Good balance
ollama pull smollm2:1.7b           # Most efficient

Add a CLI option to specify ollam model to use 
-m/--model "name-of-ollama-model"

# Step 10 investigate 


============================================================
Processing: Cross-selling and Up-selling.md
============================================================
Input text length: 37825 characters (4762 words)
Generating summary (attempt 1/1)...
Summary word count: 3052 (target: 1000-2000)
⚠️  Attempt 1: Summary has 3052 words, retrying...
⚠️  Warning: Could not generate summary within word limits after 1 attempts. Final summary has 3052 words.
Summary length: 19689 characters (3052 words)
Summary preview: Took:  
The text material contains some typos (e.g., "IT/ITES" should be “IT” or something else)  

I need you to act as an expert sales professional and data scientist with 20 years of experience, an...


# Step 9

Skip any input files (.md) that has less than `SUMMARY_WORD_MIN` words.

# Step 8 Print the number of words in the input/output text and summary

Current console output

```
[2/20] Processing files...

============================================================
Processing: Data Mining Applications in Insurance.md
============================================================
Input text length: 27673 characters
Summarizing text...
Summary length: 2570 characters
```

Expected New console output 

```
[2/20] Processing files...

============================================================
Processing: Data Mining Applications in Insurance.md
============================================================
Input text length: 27673 characters
Input text length: XXX words
Summarizing text...
Summary length: 2570 characters
Summary length: XXX words

```

# Step 7 

SUMMARY_WORD_LIMIT = 2000
SUMMARY_WORD_MIN = 1000

Make sure that the shortened text is at least 1000 words long, and no more than 2000 words long.

How to implement this code? 

# Step 6 

I want to set the response from ollama to be plaintext, not markdown. 

how to set `format` to plain text ?

``` 
import requests

response = requests.post('http://localhost:11434/api/generate', 
    json={
        'model': 'your-model-name',
        'prompt': 'Your prompt here',
        'format': 'json',  # or omit format entirely for plain text
        'options': {
            'temperature': 0.7
        }
    }
)
``` 

# Step 5 

Improve `def clean_text(text):` 
by removing all markdown formats.

Sample code below 

```

import re

def strip_markdown(text):
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # Inline code
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # Code blocks
    text = re.sub(r'^#{1,6}\s', '', text, flags=re.MULTILINE)  # Headers
    return text.strip()
```

# Step 4 

```
(.venv)  ✘ vuhung@vhM1  ~/Desktop/ollama-playground/ai-podcaster   main ±  /Users/vuhung/Desktop/ollama-playground/ai-podcaster/.venv/bin/python /Users/vuhung/Desktop/ollama-playground/ai-podcaster/ai_spotify.py
AI Podcaster CLI - Batch Processor
============================================================
Input folder: inputs/data-mining-real-world-applications
Output folder: outputs/data-mining-real-world-applications
Folder name: data-mining-real-world-applications
Languages: 🇺🇸 American English

Found 20 Markdown files:
  1. Cross-selling and Up-selling.md
  2. Data Mining Applications in Insurance.md
  3. Data Mining Applications in Media and Entertainment Content Performance Prediction.md
  4. Data Mining Applications in Real Estate - Property Valuation and Market Analysis.md
  5. Data Mining Applications in Smart Cities and the Future of Urban Planning.md
  6. Data Mining Applications in Traffic Management Report.markdown
  7. Data mining applications in Cross-selling and Up-selling.md
  8. Data mining applications in Customer Segmentation.md
  9. Data mining applications in Demand Forecasting.md
  10. Datamiining Applied in Education.md
  11. Disease Prediction in Modern Healthcare.md
  12. Fraud Detection Data Mining Applications.md
  13. Predictive Analytics in Modern Law Enforcement.md
  14. Recommendation Systems -  Data Mining Applications  Export  Create.md
  15. Traffic Analysis and Optimization.md
  16. data mining enhances genomics and bioinformatics.md
  17. data mining enhances retail operations .md
  18. data mining enhances self-driving car functionality.md
  19. fraud detection and churn prediction.md
  20. geological analysis, safety monitoring, and operational efficiency.md

This will process 20 files. Continue? (y/N): y
```

Don't ask for confirmation, just process the files.


# Step 3 

save audio files to `.mp3` format, instead of `.wav` 

# Step 2: bug fixing

1. save the summary in plaintext format, not markdown. 
2. don't include `</think>` in the summary, just the summary itself.

# Step 1 

# Finish `ai_spotify.py`

This is a command-line interface (CLI) script for summarizing and generating audio versions of Markdown files. The script reads Markdown files from a specified input folder, summarizes their content, and generates audio files of the summaries.

## Inputs: 

-d/--folder: The folder where input text files are located
default: inputs/data-mining-real-world-applications

the program will read all Markdown (.md) files in the specified folder

## Outputs: 

### Output folder:
-o/--output: The output file where the summary will be saved

default: outputs/data-mining-real-world-applications

### Structure of the output folder:

./outputs/summaries
./outputs/audio

### Output files:
- Summaries of each Markdown file in the specified folder will be saved as .md files in the output folder
- Audio versions of each summary will be generated and saved as .wav files in the output folder

# Techstack: 
- Similar to the previous script, this one will use the same libraries and methods for summarization and audio generation.
- Refer to sample code at `ai_podcaster_cli.py` 
`
# Sample folder structure for inputs and outputs:

## Inputs: 

folder: `/Users/vuhung/Desktop/ollama-playground/ai-podcaster/inputs/data-mining-real-world-applications`
input files:
```
Cross-selling and Up-selling.md
Data mining applications in Cross-selling and Up-selling.md
Data mining applications in Customer Segmentation.md
Data mining applications in Demand Forecasting.md
Data Mining Applications in Insurance.md
Data Mining Applications in Media and Entertainment Content Performance Prediction.md
Data Mining Applications in Real Estate - Property Valuation and Market Analysis.md
Data Mining Applications in Smart Cities and the Future of Urban Planning.md
Data Mining Applications in Traffic Management Report.markdown
data mining enhances genomics and bioinformatics.md
data mining enhances retail operations .md
data mining enhances self-driving car functionality.md
Datamiining Applied in Education.md
Disease Prediction in Modern Healthcare.md
fraud detection and churn prediction.md
Fraud Detection Data Mining Applications.md
geological analysis, safety monitoring, and operational efficiency.md
Predictive Analytics in Modern Law Enforcement.md
Recommendation Systems -  Data Mining Applications  Export  Create.md
Traffic Analysis and Optimization.md
```

## Output files:

### Summary files:

folder: ./outputs/summaries
files: 
```
 ./outputs/summaries/data-mining-real-world-applications/Cross-selling and Up-selling.md
 ./outputs/summaries/data-mining-real-world-applications/Data mining applications in Cross-selling and Up-selling.md
 ./outputs/summaries/data-mining-real-world-applications/Data mining applications in Customer Segmentation.md
 ./outputs/summaries/data-mining-real-world-applications/Data mining applications in Demand Forecasting.md
 ./outputs/summaries/data-mining-real-world-applications/Data Mining Applications in Insurance.md
 ./outputs/summaries/data-mining-real-world-applications/Data Mining Applications in Media and Entertainment Content Performance Prediction.md
 ./outputs/summaries/data-mining-real-world-applications/Data Mining Applications in Real Estate - Property Valuation and Market Analysis.md
 ./outputs/summaries/data-mining-real-world-applications/Data Mining Applications in Smart Cities and the Future of Urban Planning.md
 ./outputs/summaries/data-mining-real-world-applications/Data Mining Applications in Traffic Management Report.markdown
 ./outputs/summaries/data-mining-real-world-applications/data mining enhances genomics and bioinformatics.md
 ./outputs/summaries/data-mining-real-world-applications/data mining enhances retail operations .md
 ./outputs/summaries/data-mining-real-world-applications/data mining enhances self-driving car functionality.md
 ./outputs/summaries/data-mining-real-world-applications/Datamiining Applied in Education.md
 ./outputs/summaries/data-mining-real-world-applications/Disease Prediction in Modern Healthcare.md
 ./outputs/summaries/data-mining-real-world-applications/fraud detection and churn prediction.md
 ./outputs/summaries/data-mining-real-world-applications/Fraud Detection Data Mining Applications.md
 ./outputs/summaries/data-mining-real-world-applications/geological analysis, safety monitoring, and operational efficiency.md
 ./outputs/summaries/data-mining-real-world-applications/Predictive Analytics in Modern Law Enforcement.md
 ./outputs/summaries/data-mining-real-world-applications/Recommendation Systems -  Data Mining Applications  Export  Create.md
 ./outputs/summaries/data-mining-real-world-applications/Traffic Analysis and Optimization.md
```

### audio files:
folder: ./outputs/audio
files:
```
 ./outputs/audio/data-mining-real-world-applications/Cross-selling and Up-selling.wav
 ./outputs/audio/data-mining-real-world-applications/Data mining applications in Cross-selling and Up-selling.wav
 ./outputs/audio/data-mining-real-world-applications/Data mining applications in Customer Segmentation.wav
 ./outputs/audio/data-mining-real-world-applications/Data mining applications in Demand Forecasting.wav
 ./outputs/audio/data-mining-real-world-applications/Data Mining Applications in Insurance.wav
 ./outputs/audio/data-mining-real-world-applications/Data Mining Applications in Media and Entertainment Content Performance Prediction.wav
 ./outputs/audio/data-mining-real-world-applications/Data Mining Applications in Real Estate - Property Valuation and Market Analysis.wav
 ./outputs/audio/data-mining-real-world-applications/Data Mining Applications in Smart Cities and the Future of Urban Planning.wav
 ./outputs/audio/data-mining-real-world-applications/Data Mining Applications in Traffic Management Report.markdown.wav
 ./outputs/audio/data-mining-real-world-applications/data mining enhances genomics and bioinformatics.wav
 ./outputs/audio/data-mining-real-world-applications/data mining enhances retail operations .wav
 ./outputs/audio/data-mining-real-world-applications/data mining enhances self-driving car functionality.wav
 ./outputs/audio/data-mining-real-world-applications/Datamiining Applied in Education.wav
 ./outputs/audio/data-mining-real-world-applications/Disease Prediction in Modern Healthcare.wav
 ./outputs/audio/data-mining-real-world-applications/fraud detection and churn prediction.wav
 ./outputs/audio/data-mining-real-world-applications/Fraud Detection Data Mining Applications.wav
 ./outputs/audio/data-mining-real-world-applications/geological analysis, safety monitoring, and operational efficiency.wav
 ./outputs/audio/data-mining-real-world-applications/Predictive Analytics in Modern Law Enforcement.wav
 ./outputs/audio/data-mining-real-world-applications/Recommendation Systems -  Data Mining Applications  Export  Create.wav
 ./outputs/audio/data-mining-real-world-applications/Traffic Analysis and Optimization.wav
 ```