import os

import cv2
import streamlit as st
from langchain_ollama.llms import OllamaLLM

videos_directory = 'video-summarization/videos/'
frames_directory = 'video-summarization/frames/'

model = OllamaLLM(model="gemma3:27b")

def upload_video(file):
    with open(videos_directory + file.name, "wb") as f:
        f.write(file.getbuffer())

def extract_frames(video_path, interval_seconds=5):
    for file in os.listdir(frames_directory):
        os.remove(frames_directory + file)

    video = cv2.VideoCapture(video_path)

    fps = int(video.get(cv2.CAP_PROP_FPS))
    frames_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    current_frame = 0
    frame_number = 1

    while current_frame <= frames_count:
        video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        success, frame = video.read()

        if not success:
            continue

        frame_path = frames_directory + f"frame_{frame_number:03d}.jpg"
        cv2.imwrite(frame_path, frame)

        current_frame += fps * interval_seconds
        frame_number += 1

    video.release()

def describe_video():
    images = []

    for file in os.listdir(frames_directory):
        images.append(frames_directory + file)

    model_with_images = model.bind(images=images)
    return model_with_images.invoke("Summarize the video content in a few sentences.")

uploaded_file = st.file_uploader(
    "Upload Video",
    type=["mp4", "avi", "mov", "mkv"],
    accept_multiple_files=False
)

if uploaded_file:
    upload_video(uploaded_file)
    extract_frames(videos_directory + uploaded_file.name)
    summary = describe_video()

    st.markdown(summary)


