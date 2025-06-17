import os
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from pydub import AudioSegment
from kokoro import KPipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

# Configuration
INPUT_FILE = './inputs/input.md'
AUDIOS_DIRECTORY = './audios/'
SUMMARISATION_FOLDER = './outputs/'
SUMMARISATION_FILE = 'summary.txt'
SUMMARY_WORD_LIMIT = 1200

supported_languages = {
    # '🇬🇧 British English': 'b',
    '🇺🇸 American English': 'a',
}

summary_template = """
Summarize the following text. Your summary should:
1. Identify the central argument or main topic.
2. List 2-3 supporting key points or pieces of evidence.
3. Conclude with the main takeaway or implication.
4. In less than {word_limit} words.
5. Use clear and concise language.
6. Avoid jargon and complex terminology.
7. Use a friendly and engaging tone.
8. Provide a summary that is easy to understand for a general audience.
9. Use plaintext format without any special formatting or tags, e.g., no HTML or Markdown.
Text: {text}
"""

# Initialize the model
model = ChatOllama(model="deepseek-r1:8b")

def read_input_file(file_path):
    """Read text from input file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: Input file '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

def summarize_text(text):
    """Summarize the input text using the language model."""
    prompt = ChatPromptTemplate.from_template(summary_template)
    chain = prompt | model
    
    print("Summarizing text...")
    summary = chain.invoke({"text": text, "word_limit": SUMMARY_WORD_LIMIT})
    return clean_text(summary.content)

def clean_text(text):
    """Clean the text by removing thinking tags."""
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()

def generate_audio(text, lang_code, output_filename):
    """Generate audio for given text and language."""
    print(f"Generating audio for {output_filename}...")
    
    pipeline = KPipeline(lang_code=lang_code)
    generator = pipeline(text, voice='af_heart')
    chunks = []

    for i, (gs, ps, audio) in enumerate(generator):
        chunks.append(audio)

    # Concatenate all audio chunks
    full_audio = np.concatenate(chunks, axis=0)
    
    # Ensure output directory exists
    os.makedirs(AUDIOS_DIRECTORY, exist_ok=True)
    
    # Create temporary WAV file
    output_path = os.path.join(AUDIOS_DIRECTORY, output_filename)
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

def main():
    """Main function to orchestrate the CLI workflow."""
    print("AI Podcaster CLI")
    print("=" * 50)
    
    # Read input text
    print(f"Reading input from: {INPUT_FILE}")
    text = read_input_file(INPUT_FILE)
    print(f"Input text length: {len(text)} characters")
    
    # Summarize text
    summarized_text = summarize_text(text)
    print(f"Summary length: {len(summarized_text)} characters")
    print("\nSummary:")
    print("-" * 30)
    print(summarized_text)
    print("-" * 30)

    # save summarized text to file
    summary_file_path = os.path.join(SUMMARISATION_FOLDER, SUMMARISATION_FILE)

    with open(summary_file_path, 'w', encoding='utf-8') as file:
        file.write(summarized_text)
    print(f"Summary saved to: {summary_file_path}")

    # Generate audio for each supported language
    print(f"\nGenerating audio files in {len(supported_languages)} languages...")
    
    output_files = []
    for language_name, lang_code in supported_languages.items():
        output_filename = f"audio_{lang_code}.mp3"
        try:
            output_path = generate_audio(summarized_text, lang_code, output_filename)
            output_files.append((language_name, output_path))
            print(f"✓ {language_name}: {output_filename}")
        except Exception as e:
            print(f"✗ Error generating {language_name} audio: {e}")
    
    print(f"\nCompleted! Generated {len(output_files)} audio files:")
    for language_name, output_path in output_files:
        print(f"  - {language_name}: {output_path}")

if __name__ == "__main__":
    main()

