import streamlit as st
import ollama
import json
import base64
import time
import logging
import os
from typing import List
from pydantic import BaseModel
from PIL import Image
import io

# Configure logging for the Streamlit app
log_dir = './logs'
os.makedirs(log_dir, exist_ok=True)

# Configure detailed logging with OCR profiling
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('./logs/app_invoice_text_extractor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log application startup
logger.info("="*60)
logger.info("Invoice Text Extractor Application Starting")
logger.info("="*60)

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

def encode_image_to_base64(image_file):
    """Convert uploaded image to base64 string"""
    return base64.b64encode(image_file.read()).decode('utf-8')

def extract_invoice_data(image_data, image_source="uploaded"):
    """Extract invoice data using Ollama's vision model with detailed profiling"""
    logger.info(f"Starting invoice OCR extraction for {image_source} image")
    logger.info(f"Image data size: {len(image_data)} characters (base64)")
    
    # Start timing the OCR process
    start_time = time.time()
    
    try:
        logger.info("Sending request to Ollama vision model (llama3.2-vision)")
        
        res = ollama.chat(
            model="llama3.2-vision",
            messages=[
                {
                    'role': 'user',
                    'content': """Given an invoice image, Your task is to use OCR to detect and extract text, categorize it into predefined fields.
                    Invoice/Receipt Number: The unique identifier of the document.
                    Date: The issue or transaction date.
                    Vendor Name: The business or entity issuing the document.
                    Items: A list of purchased products or services with Name, Quantity and price.
                    Total: The total amount of the invoice.""",
                    'images': [image_data]
                }
            ],
            format=Invoice.model_json_schema(),
            options={'temperature': 0}
        )
        
        # End timing and calculate duration
        end_time = time.time()
        ocr_duration = end_time - start_time
        
        logger.info(f"OCR processing completed successfully in {ocr_duration:.2f} seconds for {image_source} image")
        logger.info(f"OCR Performance Metrics:")
        logger.info(f"  - Processing Time: {ocr_duration:.2f}s")
        logger.info(f"  - Image Source: {image_source}")
        logger.info(f"  - Model Used: llama3.2-vision")
        logger.info(f"  - Response Length: {len(res['message']['content'])} characters")
        
        # Log successful extraction with data preview
        try:
            parsed_data = json.loads(res['message']['content'])
            items_count = len(parsed_data.get('items', []))
            total_amount = parsed_data.get('total', 0)
            logger.info(f"Extraction Summary: {items_count} items found, total: ${total_amount}")
        except:
            logger.warning("Could not parse response as JSON for summary")
        
        return res['message']['content']
        
    except Exception as e:
        end_time = time.time()
        ocr_duration = end_time - start_time
        
        logger.error(f"Error processing {image_source} image after {ocr_duration:.2f} seconds: {str(e)}")
        logger.error(f"Error Details:")
        logger.error(f"  - Processing Time: {ocr_duration:.2f}s")
        logger.error(f"  - Image Source: {image_source}")
        logger.error(f"  - Error Type: {type(e).__name__}")
        logger.error(f"  - Error Message: {str(e)}")
        
        return f"Error processing image: {str(e)}"

def main():
    logger.info("Starting Invoice Text Extractor Streamlit app")
    logger.info("Initializing Streamlit page configuration")
    
    st.set_page_config(
        page_title="Invoice Text Extractor",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Invoice Text Extractor")
    st.markdown("Upload an invoice image to extract structured data using OCR and AI")
    
    logger.info("Streamlit UI components initialized successfully")
    
    # Sidebar for instructions
    with st.sidebar:
        st.header("Instructions")
        st.markdown("""
        1. Upload an invoice image (PNG, JPG, JPEG)
        2. Click 'Extract Data' to process
        3. View the extracted structured data
        
        **Supported formats:**
        - PNG
        - JPG/JPEG
        """)
        
        # Show sample images from the images directory
        st.header("Sample Images")
        sample_images_dir = "images"
        if os.path.exists(sample_images_dir):
            sample_files = [f for f in os.listdir(sample_images_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            logger.info(f"Found {len(sample_files)} sample images in {sample_images_dir}")
            
            for sample_file in sample_files:
                if st.button(f"Use {sample_file}"):
                    st.session_state.sample_image = os.path.join(sample_images_dir, sample_file)
                    logger.info(f"User selected sample image: {sample_file}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Upload Invoice")
        
        # Check if using sample image
        if 'sample_image' in st.session_state:
            st.info(f"Using sample image: {os.path.basename(st.session_state.sample_image)}")
            uploaded_file = st.session_state.sample_image
            
            # Display the sample image
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Sample: {os.path.basename(uploaded_file)}", use_column_width=True)
            
            logger.info(f"Displaying sample image: {os.path.basename(uploaded_file)}")
            
            if st.button("Clear Sample"):
                logger.info("User cleared sample image selection")
                del st.session_state.sample_image
                st.rerun()
        else:
            uploaded_file = st.file_uploader(
                "Choose an invoice image...",
                type=['png', 'jpg', 'jpeg'],
                help="Upload a clear image of your invoice"
            )
            
            if uploaded_file is not None:
                # Display the uploaded image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Invoice", use_column_width=True)
                
                logger.info(f"User uploaded file: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Extract button
        if uploaded_file is not None:
            if st.button("🔍 Extract Data", type="primary"):
                logger.info("User initiated OCR extraction process")
                
                with st.spinner("Processing invoice... This may take a few moments."):
                    try:
                        # Handle both uploaded files and sample images
                        if isinstance(uploaded_file, str):  # Sample image path
                            with open(uploaded_file, 'rb') as f:
                                image_data = base64.b64encode(f.read()).decode('utf-8')
                            image_source = f"sample ({os.path.basename(uploaded_file)})"
                            logger.info(f"Processing sample image: {os.path.basename(uploaded_file)}")
                        else:  # Uploaded file
                            uploaded_file.seek(0)  # Reset file pointer
                            image_data = encode_image_to_base64(uploaded_file)
                            image_source = f"uploaded ({uploaded_file.name})"
                            logger.info(f"Processing uploaded file: {uploaded_file.name}")
                        
                        # Extract invoice data
                        result = extract_invoice_data(image_data, image_source)
                        st.session_state.extraction_result = result
                        
                        logger.info("OCR extraction process completed, result stored in session state")
                        
                    except Exception as e:
                        logger.error(f"Error in main OCR process: {str(e)}")
                        st.error(f"Error processing image: {str(e)}")
    
    with col2:
        st.header("Extracted Data")
        
        if 'extraction_result' in st.session_state:
            result = st.session_state.extraction_result
            
            logger.info("Displaying extraction results to user")
            
            try:
                # Try to parse as JSON
                invoice_data = json.loads(result)
                
                logger.info("Successfully parsed extraction result as JSON")
                logger.info(f"Extracted invoice data: Invoice #{invoice_data.get('invoice_number', 'N/A')}, "
                           f"Vendor: {invoice_data.get('vendor_name', 'N/A')}, "
                           f"Total: ${invoice_data.get('total', 0):.2f}")
                
                # Display extracted information in a nice format
                st.success("✅ Data extracted successfully!")
                
                # Invoice details
                st.subheader("Invoice Details")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric("Invoice Number", invoice_data.get('invoice_number', 'N/A'))
                    st.metric("Date", invoice_data.get('date', 'N/A'))
                
                with col_b:
                    st.metric("Vendor", invoice_data.get('vendor_name', 'N/A'))
                    st.metric("Total", f"${invoice_data.get('total', 0):.2f}")
                
                # Items table
                st.subheader("Items")
                if 'items' in invoice_data and invoice_data['items']:
                    items_data = []
                    for item in invoice_data['items']:
                        items_data.append({
                            'Name': item.get('name', ''),
                            'Quantity': item.get('quantity', 0),
                            'Price': f"${item.get('price', 0):.2f}"
                        })
                    
                    st.dataframe(items_data, use_container_width=True)
                else:
                    st.info("No items found in the invoice")
                
                # Raw JSON data (expandable)
                with st.expander("View Raw JSON Data"):
                    st.json(invoice_data)
                
                # Download button for JSON
                json_str = json.dumps(invoice_data, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name="invoice_data.json",
                    mime="application/json"
                )
                
                logger.info("User interface updated with extracted data successfully")
                
            except json.JSONDecodeError:
                # If not valid JSON, show raw text
                logger.warning("Failed to parse extraction result as JSON, displaying raw response")
                st.warning("Could not parse as structured data. Showing raw response:")
                st.text_area("Raw Response", result, height=300)
                
        else:
            st.info("👆 Upload an invoice image and click 'Extract Data' to see results here")
            
            # Show example of expected output
            st.subheader("Expected Output Format")
            example_data = {
                "invoice_number": "INV-2024-001",
                "date": "2024-01-15",
                "vendor_name": "Tech Solutions Inc.",
                "items": [
                    {"name": "Software License", "quantity": 2, "price": 500.00},
                    {"name": "Support Package", "quantity": 1, "price": 200.00}
                ],
                "total": 700.00
            }
            st.json(example_data)

if __name__ == "__main__":
    logger.info("Application entry point reached")
    try:
        main()
        logger.info("Application completed successfully")
    except Exception as e:
        logger.error(f"Application crashed with error: {str(e)}")
        raise
