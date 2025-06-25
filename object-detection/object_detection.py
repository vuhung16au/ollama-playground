from typing import List
import time
import logging
import os
import glob

import ollama
from pydantic import BaseModel

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/object_detection.log'),
        logging.StreamHandler()  # Also log to console
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
            model="llama3.2-vision",
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
        
        return res
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        logger.error(f"Object detection failed after {execution_time:.2f} seconds")
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    # Get all image files from the images folder
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.tiff']
    image_files = []
    
    for extension in image_extensions:
        image_files.extend(glob.glob(f'images/{extension}'))
    
    # Filter out .gitkeep and other non-image files
    image_files = [f for f in image_files if not f.endswith('.gitkeep')]
    
    if not image_files:
        print("No image files found in the images folder.")
    else:
        print(f"Found {len(image_files)} image file(s): {image_files}")
        
        for image_path in image_files:
            print(f"\n{'='*50}")
            print(f"Processing: {image_path}")
            print(f"{'='*50}")
            
            try:
                result = perform_object_detection(image_path)
                print(result['message']['content'])
            except Exception as e:
                print(f"Failed to process {image_path}: {str(e)}")
                continue