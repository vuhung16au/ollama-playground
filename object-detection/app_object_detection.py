import streamlit as st
from typing import List
import time
import logging
import os
import json
from PIL import Image
import io

import ollama
from pydantic import BaseModel

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/object_detection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class Object(BaseModel):
    name: str
    color: List[str]
    count: int

class ObjectDetectionResponse(BaseModel):
    objects: list[Object]

def perform_object_detection(image_path: str):
    """
    Perform object detection on an image and return the response.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        Object detection response from the model
    """
    logger.info(f"Starting object detection for image: {image_path}")
    start_time = time.time()
    
    try:
        res = ollama.chat(
            model="llama3.2-vision:latest",
            messages=[
                {
                    'role': 'user',
                    'content': """Your task is to perform object detection on the image and return a structured output in JSON format. For each detected object, include the following attributes:
                    Name: The name of the detected object (e.g., 'cat', 'car', 'person').
                    Count: The total number of detected instances of this object type in the image.
                    Color: The dominant color or primary colors of the object.
                    """,
                    'images': [image_path]
                }
            ],
            format=ObjectDetectionResponse.model_json_schema(),
            options={'temperature': 0}
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.info(f"Object detection completed successfully")
        logger.info(f"Execution time: {execution_time:.2f} seconds")
        logger.info(f"Response: {res['message']['content']}")
        
        return res, execution_time
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        logger.error(f"Object detection failed after {execution_time:.2f} seconds")
        logger.error(f"Error: {str(e)}")
        raise e

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary location and return path"""
    if uploaded_file is not None:
        # Create temp directory if it doesn't exist
        os.makedirs('temp', exist_ok=True)
        
        # Save file
        file_path = f"temp/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

def format_detection_results(response_content):
    """Format the detection results for display"""
    try:
        # Parse the JSON response
        detection_data = json.loads(response_content)
        objects = detection_data.get('objects', [])
        
        if not objects:
            return "No objects detected in the image."
        
        formatted_results = []
        for obj in objects:
            name = obj.get('name', 'Unknown')
            count = obj.get('count', 0)
            colors = obj.get('color', [])
            color_str = ', '.join(colors) if colors else 'Unknown'
            
            formatted_results.append({
                'name': name,
                'count': count,
                'colors': color_str
            })
        
        return formatted_results
    except json.JSONDecodeError:
        return "Error parsing detection results."

# Streamlit app
def main():
    st.set_page_config(
        page_title="Object Detection App",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Object Detection with Ollama")
    st.write("Upload an image to detect objects using the Llama3.2-vision model")
    
    # Sidebar for information
    st.sidebar.header("About")
    st.sidebar.write("""
    This app uses the Llama3.2-vision model to detect objects in images.
    
    **Features:**
    - Object detection with names
    - Object counting
    - Color identification
    - Execution time tracking
    """)
    
    # Model status check
    st.sidebar.header("Model Status")
    try:
        # Check if ollama is available
        models_response = ollama.list()
        
        # Extract model names from the response
        model_names = []
        if hasattr(models_response, 'models'):
            # models_response.models is a list of Model objects
            for model in models_response.models:
                if hasattr(model, 'model'):
                    model_names.append(model.model)
        elif isinstance(models_response, dict) and 'models' in models_response:
            # Fallback for dictionary structure
            for model in models_response['models']:
                if isinstance(model, dict):
                    name = model.get('name') or model.get('model') or model.get('id')
                    if name:
                        model_names.append(name)
                elif isinstance(model, str):
                    model_names.append(model)
        
        # Check if llama3.2-vision model is available (with or without tag)
        vision_model_available = any(
            'llama3.2-vision' in name.lower() for name in model_names
        )
        
        if vision_model_available:
            st.sidebar.success("✅ Llama3.2-vision model available")
        else:
            st.sidebar.error("❌ Llama3.2-vision model not found")
            st.sidebar.write("Please run: `ollama pull llama3.2-vision`")
            # Show available models for debugging
            if model_names:
                st.sidebar.write("Available models:", model_names[:5])  # Show first 5 models
    except Exception as e:
        st.sidebar.error(f"❌ Ollama connection failed: {str(e)}")
        # Add more detailed error information for debugging
        st.sidebar.write("Make sure Ollama is running and accessible.")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Upload Image")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'],
            help="Upload an image file for object detection"
        )
        
        # Sample images option
        st.subheader("Or use sample images")
        sample_images = ['apple.png', 'java.png', 'tiger.png']
        sample_options = ['None'] + sample_images
        selected_sample = st.selectbox("Select a sample image:", sample_options)
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Process button
            if st.button("🔍 Detect Objects", type="primary"):
                with st.spinner("Processing image..."):
                    # Save uploaded file
                    image_path = save_uploaded_file(uploaded_file)
                    
                    if image_path:
                        try:
                            # Perform object detection
                            result, execution_time = perform_object_detection(image_path)
                            
                            # Store results in session state
                            st.session_state.detection_results = result['message']['content']
                            st.session_state.execution_time = execution_time
                            st.session_state.processed_image = image
                            
                            # Clean up temp file
                            if os.path.exists(image_path):
                                os.remove(image_path)
                                
                        except Exception as e:
                            st.error(f"Error during object detection: {str(e)}")
                    else:
                        st.error("Error saving uploaded file")
        
        elif selected_sample != 'None':
            # Display sample image
            sample_path = f"images/{selected_sample}"
            if os.path.exists(sample_path):
                image = Image.open(sample_path)
                st.image(image, caption=f"Sample Image: {selected_sample}", use_container_width=True)
                
                # Process button for sample
                if st.button("🔍 Detect Objects", type="primary"):
                    with st.spinner("Processing image..."):
                        try:
                            # Perform object detection
                            result, execution_time = perform_object_detection(sample_path)
                            
                            # Store results in session state
                            st.session_state.detection_results = result['message']['content']
                            st.session_state.execution_time = execution_time
                            st.session_state.processed_image = image
                            
                        except Exception as e:
                            st.error(f"Error during object detection: {str(e)}")
            else:
                st.error(f"Sample image {selected_sample} not found")
    
    with col2:
        st.header("Detection Results")
        
        # Display results if available
        if hasattr(st.session_state, 'detection_results'):
            st.success(f"✅ Detection completed in {st.session_state.execution_time:.2f} seconds")
            
            # Format and display results
            formatted_results = format_detection_results(st.session_state.detection_results)
            
            if isinstance(formatted_results, list):
                st.subheader("Detected Objects:")
                
                # Create a nice table view
                for i, obj in enumerate(formatted_results, 1):
                    with st.container():
                        st.write(f"**Object {i}:**")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Name", obj['name'])
                        with col_b:
                            st.metric("Count", obj['count'])
                        with col_c:
                            st.write(f"**Colors:** {obj['colors']}")
                        st.divider()
                
                # Raw JSON output (expandable)
                with st.expander("View Raw JSON Response"):
                    st.json(st.session_state.detection_results)
                    
            else:
                st.warning(formatted_results)
        else:
            st.info("👆 Upload an image or select a sample to start object detection")
            
            # Show sample results placeholder
            st.subheader("Sample Detection Output:")
            st.write("After processing, you'll see:")
            st.write("- 📝 Object names")
            st.write("- 🔢 Object counts") 
            st.write("- 🎨 Dominant colors")
            st.write("- ⏱️ Processing time")

if __name__ == "__main__":
    main()
