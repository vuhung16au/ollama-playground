import re

import streamlit as st
import whisper
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""

audios_directory = 'voice-rag/audios/'

embeddings = OllamaEmbeddings(model="deepseek-r1:8b")
vector_store = InMemoryVectorStore(embeddings)

model = OllamaLLM(model="deepseek-r1:8b")

def upload_audio(file):
    with open(audios_directory + file.name, "wb") as f:
        f.write(file.getbuffer())

def transcribe_audio(file_path):
    whisper_model = whisper.load_model("medium.en")
    result = whisper_model.transcribe(file_path)
    return result["text"]

def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )

    return text_splitter.split_text(text)

def index_docs(texts):
    vector_store.add_texts(texts)

def retrieve_docs(query):
    return vector_store.similarity_search(query)

def answer_question(question, documents):
    context = "\n\n".join([doc.page_content for doc in documents])
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    return clean_text(chain.invoke({"question": question, "context": context}))

def clean_text(text):
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()

uploaded_file = st.file_uploader(
    "Upload Audio",
    type=["mp3", "wav"],
    accept_multiple_files=False
)

if uploaded_file:
    upload_audio(uploaded_file)
    text = transcribe_audio(audios_directory + uploaded_file.name)
    chunked_texts = split_text(text)
    index_docs(chunked_texts)

    question = st.chat_input()

    if question:
        st.chat_message("user").write(question)
        related_docs = retrieve_docs(question)
        answer = answer_question(question, related_docs)
        st.chat_message("assistant").write(answer)