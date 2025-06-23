import os
import re
import sys
import argparse
from pathlib import Path
import glob
import time
import csv
from datetime import datetime

import numpy as np
import soundfile as sf
from pydub import AudioSegment
from kokoro import KPipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
import strip_markdown

# Configuration
DEFAULT_INPUT_FOLDER = 'inputs'
DEFAULT_OUTPUT_FOLDER = 'outputs'

def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs('logs', exist_ok=True)
    os.makedirs('metrics', exist_ok=True)

def log_message(message):
    """Write message to log file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('logs/ai_spotify.txt', 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)  # Also print to console

def save_runtime_metric(input_file_name, step, start_time, end_time, duration_seconds, model_tts):
    """Save runtime metric to CSV file"""
    file_exists = os.path.exists('metrics/runtime.csv')
    
    with open('metrics/runtime.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if file doesn't exist
        if not file_exists:
            writer.writerow(['input_file_name', 'step', 'start_time', 'end_time', 'duration_seconds', 'model-tts'])
        
        writer.writerow([
            input_file_name,
            step,
            start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time.strftime("%Y-%m-%d %H:%M:%S"),
            round(duration_seconds, 3),
            model_tts
        ])

supported_languages = {
    # '🇬🇧 British English': 'b',
    '🇺🇸 American English': 'a',
}

# summary_template = """
# Summarize the following text by highlighting the key points.
# Maintain a conversational tone and keep the summary easy to follow for a general audience.
# Do not include reasoning or thinking tags in the summary, just provide the summary directly.
# Text: {text}
# """


summary_template = """
You are a professional content creator writing engaging executive summaries for a general audience.

Transform the following text into a compelling, conversational podcast that tells the story of the topic. 

Requirements:
- Start directly with the main topic - no meta-commentary about the task
- Write in a natural, storytelling tone as if explaining to a friend
- Focus on the key insights and practical applications
- Make complex concepts accessible without oversimplifying
- Structure the content to flow logically from introduction to conclusion
- Keep the audience engaged throughout
- Your summary is for a podcast
- Your summary must be in a single paragraph
- Your summary must be shorter than 500 words
- Skip all the links (http, https, www) and references in the text

Sample `Executive Summary` responses: 

```
This report details how data mining techniques can be used to significantly improve cross-selling and upselling strategies in a competitive business landscape. By leveraging methods like clustering, classification, and association rule learning, companies can analyze vast amounts of customer data to uncover actionable insights, personalize recommendations, and ultimately drive revenue growth. The report draws on case studies from the IT/ITES, banking, telecommunications, and retail sectors to demonstrate the tangible benefits of this approach. Key successes highlighted include a global bank achieving a 50% increase in conversion rates and a telecom firm doubling its cross-selling performance. The document provides a framework for implementation, outlining best practices and future trends to guide businesses in optimizing their sales and customer engagement strategies through data-driven decision-making.
```

```
Cross-selling and up-selling are revenue optimization strategies that involve offering complementary products (cross-selling) or higher-value alternatives (up-selling) to customers. Data mining serves as the analytical engine for these strategies by uncovering hidden patterns in customer behavior and purchase history. This allows businesses to move beyond intuition-based sales to data-driven recommendations, predicting which customers are most likely to respond to specific offers. Cross-selling algorithms typically analyze purchase patterns to find products bought together, while up-selling models predict a customer's likelihood to upgrade.
```

Text: {text}
"""

# Initialize the model
# smollm2:1.7b 
# model = ChatOllama(model="smollm2:1.7b")
# model = ChatOllama(model="deepseek-r1:1.5b")
model = ChatOllama(model="deepseek-r1:8b")

def count_words(text):
    """Count the number of words in a text string."""
    return len(text.split())


def summarize_text_with_length_control(text, max_attempts=1):
    """Generate a summary with a single attempt."""
    print("Generating summary...")
    prompt_template = summary_template
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | model
    summary = chain.invoke({"text": text})
    
    cleaned_summary = clean_text(summary.content)
    word_count = count_words(cleaned_summary)
    print(f"✅ Summary generated successfully with {word_count} words")
    return cleaned_summary

def read_input_file(file_path):
    """Read text from input file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: Input file '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading input file '{file_path}': {e}")
        return None

def summarize_text(text):
    """Summarize the input text using the language model with word count control."""
    return summarize_text_with_length_control(text)

def clean_text(text):
    """Clean the text by removing thinking tags and markdown formatting."""
    # Remove both <think>...</think> blocks and standalone </think> tags
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned_text = re.sub(r"</think>", "", cleaned_text)
    
    # Use strip_markdown to remove all markdown formatting
    cleaned_text = strip_markdown.strip_markdown(cleaned_text)
    
    return cleaned_text.strip()

def generate_audio(text, lang_code, output_path):
    """Generate audio for given text and language."""
    print(f"Generating audio for {os.path.basename(output_path)}...")
    
    pipeline = KPipeline(lang_code=lang_code)
    generator = pipeline(text, voice='af_heart')
    chunks = []

    for i, (gs, ps, audio) in enumerate(generator):
        chunks.append(audio)

    # Concatenate all audio chunks
    full_audio = np.concatenate(chunks, axis=0)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create temporary WAV file
    temp_wav_path = output_path.replace('.mp3', '_temp.wav')
    
    # Write audio to temporary WAV file
    sf.write(temp_wav_path, full_audio, 24000)
    
    # Convert WAV to MP3 using pydub
    audio_segment = AudioSegment.from_wav(temp_wav_path)
    audio_segment.export(output_path, format="mp3")
    
    # Clean up temporary WAV file
    os.remove(temp_wav_path)
    
    print(f"Audio saved to: {output_path}")
    return output_path

def find_markdown_files(input_folder):
    """Find all Markdown files in the input folder."""
    patterns = ['*.md', '*.markdown']
    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(input_folder, pattern)))
    return sorted(files)

def save_summary(summary_text, output_path):
    """Save summary text to file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(summary_text)
    print(f"Summary saved to: {output_path}")

def step1_summarize_file(input_file_path, output_folder):
    """Step 1: Summarize a markdown file and save as text."""
    # Ensure directories exist
    ensure_directories()
    
    # Get input file name for logging
    input_file_name = os.path.basename(input_file_path)
    
    # Start timing
    step1_start = datetime.now()
    
    print(f"\n{'='*60}")
    print(f"STEP 1: Summarizing {input_file_name}")
    print(f"{'='*60}")
    
    log_message(f"Step 1 starting for {input_file_name}")
    
    # Read input file
    text = read_input_file(input_file_path)
    if text is None:
        log_message(f"Skipping {input_file_name} due to read error")
        return False
    
    # Check if input file has content
    input_word_count = count_words(text)
    log_message(f"Input text length: {len(text)} characters ({input_word_count} words)")
    
    # Summarize text
    summarized_text = summarize_text(text)
    summary_word_count = count_words(summarized_text)
    log_message(f"Summary length: {len(summarized_text)} characters ({summary_word_count} words)")
    
    # Show a preview of the summary
    preview = summarized_text[:200] + "..." if len(summarized_text) > 200 else summarized_text
    log_message(f"Summary preview: {preview}")
    
    # Get base filename without extension
    base_filename = os.path.basename(input_file_path)
    filename_without_ext = os.path.splitext(base_filename)[0]
    
    # Create output paths
    summary_folder = os.path.join(output_folder, 'summaries')
    
    # Change summary file extension to .txt for plaintext format
    summary_filename = f"{filename_without_ext}.txt"
    summary_path = os.path.join(summary_folder, summary_filename)
    
    # Save summary
    save_summary(summarized_text, summary_path)
    
    # End timing and log
    step1_end = datetime.now()
    step1_duration = (step1_end - step1_start).total_seconds()
    
    log_message(f"Step 1 completed for {input_file_name} in {step1_duration:.3f} seconds")
    log_message(f"✅ Step 1 completed: Summary saved to {summary_path}")
    
    # Save runtime metric
    save_runtime_metric(input_file_name, "step_1", step1_start, step1_end, step1_duration, "deepseek-r1:8b")
    
    return True

def step2_generate_audio_from_text(text_file_path, output_folder):
    """Step 2: Generate audio from a text file."""
    # Ensure directories exist
    ensure_directories()
    
    # Get input file name for logging
    input_file_name = os.path.basename(text_file_path)
    
    # Start timing
    step2_start = datetime.now()
    
    print(f"\n{'='*60}")
    print(f"STEP 2: Generating audio for {input_file_name}")
    print(f"{'='*60}")
    
    log_message(f"Step 2 starting for {input_file_name}")
    
    # Read text file
    try:
        with open(text_file_path, 'r', encoding='utf-8') as file:
            text_content = file.read().strip()
    except FileNotFoundError:
        log_message(f"Error: Text file '{text_file_path}' not found.")
        return 0
    except Exception as e:
        log_message(f"Error reading text file '{text_file_path}': {e}")
        return 0
    
    if not text_content:
        log_message(f"Warning: Text file '{text_file_path}' is empty.")
        return 0
    
    # Get base filename without extension
    base_filename = os.path.basename(text_file_path)
    filename_without_ext = os.path.splitext(base_filename)[0]
    
    # Create output paths
    audio_folder = os.path.join(output_folder, 'audio')
    
    # Generate audio files
    log_message(f"Generating audio files...")
    
    output_files = []
    for language_name, lang_code in supported_languages.items():
        audio_filename = f"{filename_without_ext}.mp3"
        audio_path = os.path.join(audio_folder, audio_filename)
        
        try:
            output_path = generate_audio(text_content, lang_code, audio_path)
            output_files.append((language_name, output_path))
            log_message(f"✓ {language_name}: {audio_filename}")
        except Exception as e:
            log_message(f"✗ Error generating {language_name} audio: {e}")
    
    # End timing and log
    step2_end = datetime.now()
    step2_duration = (step2_end - step2_start).total_seconds()
    
    log_message(f"Step 2 completed for {input_file_name} in {step2_duration:.3f} seconds")
    log_message(f"✅ Step 2 completed: {len(output_files)} audio files generated")
    
    # Save runtime metric
    save_runtime_metric(input_file_name, "step_2", step2_start, step2_end, step2_duration, "Kokoro 80M")
    
    return len(output_files)

def process_single_file(input_file_path, output_folder, step='all'):
    """Process a single markdown file with specified step(s)."""
    # Ensure directories exist
    ensure_directories()
    
    # Get input file name for logging
    input_file_name = os.path.basename(input_file_path)
    
    print(f"\n{'='*60}")
    print(f"Processing: {input_file_name} (Step: {step})")
    print(f"{'='*60}")
    
    log_message(f"Starting processing for file: {input_file_name}")
    
    # Get base filename without extension
    base_filename = os.path.basename(input_file_path)
    filename_without_ext = os.path.splitext(base_filename)[0]
    
    # Create output paths
    summary_folder = os.path.join(output_folder, 'summaries')
    summary_filename = f"{filename_without_ext}.txt"
    summary_path = os.path.join(summary_folder, summary_filename)
    
    audio_count = 0
    
    if step in ['1', 'all']:
        # Step 1: Summarize markdown to text
        success = step1_summarize_file(input_file_path, output_folder)
        if not success:
            log_message(f"Failed to process step 1 for {input_file_name}")
            return None
    
    if step in ['2', 'all']:
        # Step 2: Generate audio from text
        if step == '2':
            # If only running step 2, check if summary file exists
            if not os.path.exists(summary_path):
                log_message(f"Error: Summary file '{summary_path}' not found. Run step 1 first.")
                return None
        
        audio_count = step2_generate_audio_from_text(summary_path, output_folder)
    
    log_message(f"Successfully completed processing for {input_file_name}")
    return audio_count

def process_file(input_file_path, output_folder, folder_name, step='all'):
    """Process a single markdown file with specified step(s)."""
    # Ensure directories exist
    ensure_directories()
    
    # Get input file name for logging
    input_file_name = os.path.basename(input_file_path)
    
    print(f"\n{'='*60}")
    print(f"Processing: {input_file_name} (Step: {step})")
    print(f"{'='*60}")
    
    log_message(f"Starting processing for file: {input_file_name}")
    
    # Get base filename without extension
    base_filename = os.path.basename(input_file_path)
    filename_without_ext = os.path.splitext(base_filename)[0]
    
    # Create output paths
    summary_folder = os.path.join(output_folder, 'summaries')
    summary_filename = f"{filename_without_ext}.txt"
    summary_path = os.path.join(summary_folder, summary_filename)
    
    audio_count = 0
    
    if step in ['1', 'all']:
        # Step 1: Summarize markdown to text
        success = step1_summarize_file(input_file_path, output_folder)
        if not success:
            log_message(f"Failed to process step 1 for {input_file_name}")
            return None
    
    if step in ['2', 'all']:
        # Step 2: Generate audio from text
        if step == '2':
            # If only running step 2, check if summary file exists
            if not os.path.exists(summary_path):
                log_message(f"Error: Summary file '{summary_path}' not found. Run step 1 first.")
                return None
        
        audio_count = step2_generate_audio_from_text(summary_path, output_folder)
    
    log_message(f"Successfully completed processing for {input_file_name}")
    return audio_count

# ...existing code...

# ...existing code...

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='AI Podcaster CLI - Process Markdown files to summaries and audio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file (both steps)
  python ai_spotify.py --input-file inputs/article.md
  
  # Process single file - step 1 only (summarize)
  python ai_spotify.py --input-file inputs/article.md --step 1
  
  # Process single file - step 2 only (audio generation)
  python ai_spotify.py --input-file inputs/article.md --step 2
  
  # Process all files in a folder
  python ai_spotify.py --input-folder inputs/data-mining-real-world-applications
  
  # Process folder - step 1 only
  python ai_spotify.py --input-folder inputs/articles --step 1
  
  # Process folder - step 2 only
  python ai_spotify.py --input-folder inputs/articles --step 2
  
  # Process with custom output folder
  python ai_spotify.py --input-folder inputs/articles --output-folder outputs/my-articles --step all
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        '--input-file',
        type=str,
        help='Input Markdown file to process'
    )
    
    input_group.add_argument(
        '--input-folder',
        type=str,
        default=DEFAULT_INPUT_FOLDER,
        help=f'Input folder containing Markdown files (default: {DEFAULT_INPUT_FOLDER})'
    )
    
    # Legacy arguments for backward compatibility
    input_group.add_argument(
        '-d', '--folder',
        type=str,
        dest='input_folder',
        help='Input folder containing Markdown files (legacy option, use --input-folder)'
    )
    
    parser.add_argument(
        '--output-folder',
        type=str,
        default=DEFAULT_OUTPUT_FOLDER,
        help=f'Output folder for summaries and audio files (default: {DEFAULT_OUTPUT_FOLDER})'
    )
    
    # Legacy argument for backward compatibility
    parser.add_argument(
        '-o', '--output',
        type=str,
        dest='output_folder',
        help='Output folder for summaries and audio files (legacy option, use --output-folder)'
    )
    
    # Step argument
    parser.add_argument(
        '--step',
        type=str,
        choices=['1', '2', 'all'],
        default='all',
        help='Processing step: 1 (summarize only), 2 (audio only), all (both steps) (default: all)'
    )
    
    return parser.parse_args()

def main():
    """Main function to orchestrate the CLI workflow."""
    # Ensure directories exist
    ensure_directories()
    
    print("AI Podcaster CLI - Processor")
    print("=" * 60)
    
    log_message("AI Podcaster CLI - Processor started")
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Display step information
    step_descriptions = {
        '1': 'Step 1: Summarize Markdown to Text',
        '2': 'Step 2: Convert Text to Audio',
        'all': 'Both Steps: Summarize and Generate Audio'
    }
    
    print(f"Processing mode: {step_descriptions[args.step]}")
    log_message(f"Processing mode: {step_descriptions[args.step]}")
    
    # Determine input mode
    if args.input_file:
        # Single file mode
        input_file = args.input_file
        output_folder = args.output_folder
        
        print(f"Mode: Single file processing")
        print(f"Input file: {input_file}")
        print(f"Output folder: {output_folder}")
        print(f"Step: {args.step}")
        print(f"Languages: {', '.join(supported_languages.keys())}")
        
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' does not exist.")
            sys.exit(1)
        
        # Check if it's a markdown file
        if not input_file.lower().endswith(('.md', '.markdown')):
            print(f"Error: Input file '{input_file}' is not a Markdown file.")
            sys.exit(1)
        
        print(f"\nProcessing single file: {os.path.basename(input_file)}")
        
        try:
            # Log start time
            start_time = datetime.now()
            log_message(f"Processing started for {os.path.basename(input_file)} (Step: {args.step})")
            
            audio_count = process_single_file(input_file, output_folder, args.step)
            if audio_count is not None:
                # Log end time
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                log_message(f"Processing completed for {os.path.basename(input_file)}. Duration: {duration:.3f} seconds")
                
                print(f"\n{'='*60}")
                print("PROCESSING COMPLETE")
                print(f"{'='*60}")
                
                if args.step in ['1', 'all']:
                    print(f"Summary saved to: {os.path.join(output_folder, 'summaries')}")
                    log_message(f"Summary saved to: {os.path.join(output_folder, 'summaries')}")
                if args.step in ['2', 'all']:
                    print(f"Audio files generated: {audio_count}")
                    print(f"Audio files saved to: {os.path.join(output_folder, 'audio')}")
                    log_message(f"Audio files generated: {audio_count}")
                    log_message(f"Audio files saved to: {os.path.join(output_folder, 'audio')}")
                
                print(f"\n✅ Processing completed successfully!")
                log_message("AI Podcaster CLI - Single file processing completed successfully!")
            else:
                print("❌ Failed to process the file.")
                log_message("❌ Failed to process the file.")
                sys.exit(1)
        except Exception as e:
            print(f"Error processing {input_file}: {e}")
            log_message(f"Error processing {input_file}: {e}")
            sys.exit(1)
    
    else:
        # Folder mode (batch processing)
        input_folder = args.input_folder
        output_folder = args.output_folder
        
        # Get folder name for organizing outputs
        folder_name = os.path.basename(os.path.normpath(input_folder))
        
        print(f"Mode: Batch folder processing")
        print(f"Input folder: {input_folder}")
        print(f"Output folder: {output_folder}")
        print(f"Folder name: {folder_name}")
        print(f"Step: {args.step}")
        print(f"Languages: {', '.join(supported_languages.keys())}")
        
        # Check if input folder exists
        if not os.path.exists(input_folder):
            print(f"Error: Input folder '{input_folder}' does not exist.")
            sys.exit(1)
        
        # Find all Markdown files
        markdown_files = find_markdown_files(input_folder)
        
        if not markdown_files:
            print(f"No Markdown files found in '{input_folder}'")
            sys.exit(1)
        
        print(f"\nFound {len(markdown_files)} Markdown files:")
        for i, file_path in enumerate(markdown_files, 1):
            print(f"  {i}. {os.path.basename(file_path)}")
        
        # Auto-process all files without confirmation
        print(f"\nProcessing {len(markdown_files)} files automatically...")
        
        # Process each file
        total_files = len(markdown_files)
        successful_files = 0
        total_audio_files = 0
        
        for i, file_path in enumerate(markdown_files, 1):
            print(f"\n[{i}/{total_files}] Processing files...")
            try:
                # Log start time for each file
                start_time = datetime.now()
                log_message(f"Processing started for {os.path.basename(file_path)} (Step: {args.step})")
                
                audio_count = process_file(file_path, output_folder, folder_name, args.step)
                
                if audio_count is not None:
                    successful_files += 1
                    if args.step in ['2', 'all']:
                        total_audio_files += audio_count
                    
                    # Log end time for each file
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    log_message(f"Processing completed for {os.path.basename(file_path)}. Duration: {duration} seconds")
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user.")
                log_message("Operation cancelled by user.")
                break
            except Exception as e:
                error_message = f"Error processing {file_path}: {e}"
                print(error_message)
                log_message(error_message)
        
        # Summary
        print(f"\n{'='*60}")
        print("PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"Total files processed: {successful_files}/{total_files}")
        
        log_message(f"Batch processing complete: {successful_files}/{total_files} files processed successfully")
        
        if args.step in ['1', 'all']:
            print(f"Summary files saved to: {os.path.join(output_folder, 'summaries')}")
            log_message(f"Summary files saved to: {os.path.join(output_folder, 'summaries')}")
        if args.step in ['2', 'all']:
            print(f"Total audio files generated: {total_audio_files}")
            print(f"Audio files saved to: {os.path.join(output_folder, 'audio')}")
            log_message(f"Total audio files generated: {total_audio_files}")
            log_message(f"Audio files saved to: {os.path.join(output_folder, 'audio')}")
        
        if successful_files == 0:
            print("No files were successfully processed.")
            log_message("No files were successfully processed.")
            sys.exit(1)
        
        print("\n✅ Processing completed successfully!")
        log_message("AI Podcaster CLI - Processing completed successfully!")

