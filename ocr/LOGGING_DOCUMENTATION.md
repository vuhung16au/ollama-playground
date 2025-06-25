# Invoice Text Extractor - Logging Features

## Overview
The Invoice Text Extractor application (`invoice_ocr_processor.py`) includes comprehensive logging and OCR performance profiling capabilities.

## Logging Configuration
- **Log File**: `./logs/invoice_text_extractor.log`
- **Log Level**: INFO
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Handlers**: File logging and console output

## OCR Performance Profiling

### Timing Metrics
The application logs detailed timing information for OCR operations:
- **Processing Time**: Total time taken for OCR extraction
- **Image Source**: Whether the image is uploaded or a sample
- **Model Used**: The Ollama vision model (llama3.2-vision)
- **Response Length**: Size of the extracted data

### Example Log Entry
```
2025-06-25 15:59:16,359 - enhanced_invoice_extractor - INFO - Initialized InvoiceExtractor with model: llama3.2-vision
2025-06-25 15:59:16,360 - enhanced_invoice_extractor - INFO - Starting OCR extraction for: images/invoice-01.png
2025-06-25 15:59:20,549 - enhanced_invoice_extractor - INFO - OCR processing completed in 4.19 seconds for images/invoice-01.png
2025-06-25 15:59:20,550 - enhanced_invoice_extractor - INFO - Successfully extracted data: Invoice #INV-001, Vendor: TechCorp, Total: $750.50
```

## Logged Events

### Application Lifecycle
- Application startup and initialization
- Streamlit configuration
- UI component initialization
- Application completion or crashes

### User Interactions
- File uploads (with file size information)
- Sample image selection
- OCR extraction initiation
- Data display and parsing

### OCR Processing
- Start of OCR process with image details
- Ollama model communication
- Processing completion with timing
- Success/failure status
- Extraction result summary
- Error handling with detailed diagnostics

### Error Handling
- Detailed error logging with context
- Processing time even for failed operations
- Error type and message information
- Stack traces for debugging

## Log File Location

All logs are written to: `./logs/invoice_text_extractor.log`

The logs directory is automatically created if it doesn't exist.

## Usage Example

To run the enhanced invoice extractor:

```bash
python invoice_ocr_processor.py
```

To view recent logs:

```bash
tail -f ./logs/invoice_text_extractor.log
```

## Benefits
1. **Performance Monitoring**: Track OCR processing times for optimization
2. **Debugging**: Detailed error information for troubleshooting
3. **Usage Analytics**: Monitor user interactions and success rates
4. **System Health**: Application startup/shutdown tracking
5. **Audit Trail**: Complete record of all operations

## Log Rotation
For production use, consider implementing log rotation to manage file sizes. You can use Python's `RotatingFileHandler` or external tools like `logrotate`.
