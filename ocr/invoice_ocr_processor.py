from typing import List, Optional
import time
import logging
import os
import json
from pathlib import Path

import ollama
from pydantic import BaseModel

# Configure logging
log_dir = './logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/invoice_text_extractor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class Item(BaseModel):
    name: str
    quantity: int
    price: float

class Invoice(BaseModel):
    invoice_number: str
    date: str
    vendor_name: str
    items: List[Item]
    total: float

class InvoiceExtractor:
    """Enhanced invoice text extractor with logging and profiling capabilities."""
    
    def __init__(self, model_name: str = "llama3.2-vision"):
        self.model_name = model_name
        logger.info(f"Initialized InvoiceExtractor with model: {model_name}")
    
    def extract_from_image(self, image_path: str) -> Optional[dict]:
        """
        Extract invoice data from a single image file.
        
        Args:
            image_path: Path to the invoice image file
            
        Returns:
            Dictionary containing extracted invoice data or None if failed
        """
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None
        
        logger.info(f"Starting OCR extraction for: {image_path}")
        start_time = time.time()
        
        try:
            result = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': """Given an invoice image, Your task is to use OCR to detect and extract text, categorize it into predefined fields.
                        Invoice/Receipt Number: The unique identifier of the document.
                        Date: The issue or transaction date.
                        Vendor Name: The business or entity issuing the document.
                        Items: A list of purchased products or services with Name, Quantity and price.
                        Total: The total amount of the invoice.""",
                        'images': [image_path]
                    }
                ],
                format=Invoice.model_json_schema(),
                options={'temperature': 0}
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            logger.info(f"OCR processing completed in {processing_time:.2f} seconds for {image_path}")
            
            # Parse the JSON response
            extracted_data = json.loads(result['message']['content'])
            logger.info(f"Successfully extracted data: Invoice #{extracted_data.get('invoice_number', 'N/A')}, "
                       f"Vendor: {extracted_data.get('vendor_name', 'N/A')}, "
                       f"Total: ${extracted_data.get('total', 0):.2f}")
            
            return {
                'data': extracted_data,
                'processing_time': processing_time,
                'image_path': image_path
            }
            
        except json.JSONDecodeError as e:
            end_time = time.time()
            processing_time = end_time - start_time
            logger.error(f"Failed to parse JSON response for {image_path} after {processing_time:.2f} seconds: {e}")
            return None
            
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            logger.error(f"Error processing {image_path} after {processing_time:.2f} seconds: {e}")
            return None
    
    def extract_from_directory(self, directory_path: str, extensions: Optional[List[str]] = None) -> List[dict]:
        """
        Extract invoice data from all images in a directory.
        
        Args:
            directory_path: Path to directory containing invoice images
            extensions: List of file extensions to process (default: ['.png', '.jpg', '.jpeg'])
            
        Returns:
            List of dictionaries containing extraction results
        """
        if extensions is None:
            extensions = ['.png', '.jpg', '.jpeg']
        
        directory = Path(directory_path)
        if not directory.exists():
            logger.error(f"Directory not found: {directory_path}")
            return []
        
        # Find all image files
        image_files = []
        for ext in extensions:
            image_files.extend(directory.glob(f"*{ext}"))
            image_files.extend(directory.glob(f"*{ext.upper()}"))
        
        logger.info(f"Found {len(image_files)} image files in {directory_path}")
        
        results = []
        total_start_time = time.time()
        
        for image_file in image_files:
            result = self.extract_from_image(str(image_file))
            if result:
                results.append(result)
        
        total_end_time = time.time()
        total_processing_time = total_end_time - total_start_time
        
        logger.info(f"Batch processing completed: {len(results)}/{len(image_files)} successful extractions "
                   f"in {total_processing_time:.2f} seconds")
        
        return results
    
    def save_results_to_json(self, results: List[dict], output_file: str) -> None:
        """Save extraction results to a JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save results to {output_file}: {e}")

def main():
    """Example usage of the InvoiceExtractor class."""
    extractor = InvoiceExtractor()
    
    # Process a single image
    single_result = extractor.extract_from_image('images/invoice-01.png')
    if single_result:
        print(f"Single image processing time: {single_result['processing_time']:.2f} seconds")
        print(f"Extracted data: {json.dumps(single_result['data'], indent=2)}")
    
    # Process all images in the images directory
    batch_results = extractor.extract_from_directory('images')
    
    if batch_results:
        # Save results to file
        extractor.save_results_to_json(batch_results, 'extraction_results.json')
        
        # Print summary statistics
        total_time = sum(result['processing_time'] for result in batch_results)
        avg_time = total_time / len(batch_results)
        
        print(f"\nBatch Processing Summary:")
        print(f"- Total images processed: {len(batch_results)}")
        print(f"- Total processing time: {total_time:.2f} seconds")
        print(f"- Average time per image: {avg_time:.2f} seconds")
        
        for result in batch_results:
            data = result['data']
            print(f"- {os.path.basename(result['image_path'])}: "
                  f"{data.get('vendor_name', 'N/A')} - ${data.get('total', 0):.2f} "
                  f"({result['processing_time']:.2f}s)")

if __name__ == "__main__":
    main()
