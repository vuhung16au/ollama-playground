import os
import re

import numpy as np
import soundfile as sf
import streamlit as st
import strip_markdown
from kokoro import KPipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

# Configuration
audios_directory = './audios/'
SUMMARY_WORD_LIMIT = 600

supported_languages = {
    '🇬🇧 British English': 'b',
    # '🇺🇸 American English': 'a',
    # '🇯🇵 Japanese': 'j',
    # '🇨🇳 Mandarin Chinese': 'z'
    # '🇪🇸 Spanish': 'e',
    # '🇫🇷 French': 'f',
    # '🇮🇳 Hindi': 'h',
    # '🇮🇹 Italian': 'i',
    # '🇧🇷 Brazilian Portuguese': 'p'
}

summary_template = """
Summarize the following text. Your summary should:
1. Identify the central argument or main topic.
2. List 2-3 supporting key points or pieces of evidence.
3. Conclude with the main takeaway or implication.
4. In less than {word_limit} words.
Maintain a conversational tone and ensure the summary is accessible to a general audience.
Text: {text}
"""

# summary_template = """
# Summarize the following text by highlighting the key points.
# Maintain a conversational tone and keep the summary easy to follow for a general audience.
# Text: {text}
# """

model = ChatOllama(model="deepseek-r1:8b")

def generate_audio(pipeline, text):
    for file in os.listdir(audios_directory):
        os.remove(audios_directory + file)

    generator = pipeline(text, voice='af_heart')
    chunks = []

    for i, (gs, ps, audio) in enumerate(generator):
        chunks.append(audio)

    file_name = 'audio.wav'
    full_audio = np.concatenate(chunks, axis=0)
    sf.write(audios_directory + file_name, full_audio, 24000)

    return file_name

def summarize_text(text):
    prompt = ChatPromptTemplate.from_template(summary_template)
    chain = prompt | model

    summary = chain.invoke({"text": text, "word_limit": SUMMARY_WORD_LIMIT})
    return clean_text(summary.content)

def clean_text(text):
    # Remove <think>...</think> tags first
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Remove all markdown formatting using strip_markdown
    cleaned_text = strip_markdown.strip_markdown(cleaned_text)
    return cleaned_text.strip()

st.title("AI Podcaster")

language = st.selectbox("Select a language:", list(supported_languages.keys()), index=0)
text = st.text_area("Enter text to generate audio:", height=300)
should_summarize = st.checkbox("Summarize text")
button = st.button("Generate Audio")

if button and text:
    pipeline = KPipeline(lang_code=supported_languages[language])

    if should_summarize:
        text = summarize_text(text)

    file_name = generate_audio(pipeline, text)
    st.audio(audios_directory + file_name)













