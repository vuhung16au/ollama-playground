# Image Search Application - Logging & Profiling

This document describes the logging and profiling implementation for the image search application.

## Overview

The application now includes comprehensive logging and performance profiling to track:
- Image upload operations
- Search operations (text-based and reverse image search)
- Image description generation
- Error tracking and debugging information
- Performance metrics and timing data

## Logging Files

The application creates two main log files in the `./logs/` directory:

### 1. `image-search.log`
Contains general application logs including:
- Application startup/shutdown events
- User operations (uploads, searches)
- Success and error messages
- Detailed error information with stack traces

### 2. `image-search-timing.log`
Contains structured performance timing data:
- Function execution times
- Operation success/failure status
- Timestamp information for analytics

## Features Implemented

### 1. Automatic Profiling
All major operations are automatically profiled using the `@app_logger.profile_function()` decorator:
- `image_upload`: Time to upload and process images
- `image_search_by_query`: Time to search images by text query
- `reverse_image_search`: Time to search similar images by uploaded image
- `image_description_generation`: Time to generate AI descriptions

### 2. Structured Logging
- **INFO level**: Normal operations and user actions
- **WARNING level**: Non-critical issues (e.g., no search results found)
- **ERROR level**: Errors with full exception details and stack traces

### 3. Performance Metrics
The application logs detailed timing information for:
- Individual search operations
- Batch upload operations
- Image processing time
- AI model inference time

### 4. Log Viewer Interface
A built-in web interface (`Logs & Performance` page) provides:
- Real-time log viewing with filtering options
- Performance analytics and statistics
- Usage trends and patterns
- Function performance breakdown

## Usage Examples

### Viewing Logs
1. Navigate to the "Logs & Performance" page in the application
2. Use the tabs to view:
   - **Application Logs**: Recent log entries with filtering
   - **Performance Timing**: Execution time statistics
   - **Analytics**: Usage patterns and trends

### Log File Format

**Main Log Format:**
```
2024-06-25 10:30:45,123 - ImageSearchApp - INFO - User initiated search with query: 'red apple'
2024-06-25 10:30:45,567 - ImageSearchApp - INFO - Search completed. Found 2 results for query: 'red apple'
```

**Timing Log Format:**
```
2024-06-25T10:30:45.123456 | image_search_query | 0.4440s | SUCCESS
2024-06-25T10:30:50.789012 | image_upload | 2.1234s | SUCCESS
```

### Manual Log Access

You can also view logs directly from the command line:

```bash
# View recent application logs
tail -f ./logs/image-search.log

# View performance timing
tail -f ./logs/image-search-timing.log

# Search for specific operations
grep "image_search" ./logs/image-search-timing.log
```

## Performance Monitoring

The application tracks several key performance metrics:

### Search Operations
- **Query processing time**: Time to embed and search the query
- **Result retrieval time**: Time to fetch matching documents
- **Total search time**: End-to-end search operation time

### Upload Operations
- **File processing time**: Time to save and process uploaded files
- **AI description time**: Time for AI to analyze and describe images
- **Vector embedding time**: Time to create and store embeddings

### Reverse Search Operations
- **Image analysis time**: Time to analyze uploaded reference image
- **Similarity search time**: Time to find similar images
- **Total operation time**: End-to-end reverse search time

## Error Tracking

All errors are logged with:
- Full exception details
- Stack traces for debugging
- Context information (what operation was being performed)
- Timing information (how long before failure occurred)

## Log Rotation and Maintenance

Currently, logs are appended to files without automatic rotation. For production use, consider:
- Implementing log rotation based on file size or time
- Archiving old log files
- Setting up log monitoring and alerting

## Configuration

The logging system is configured in `logger.py` with:
- Log file paths (default: `./logs/`)
- Log levels and formatting
- Console output (for development)
- Structured timing format

To modify logging behavior, edit the `ImageSearchLogger` class in `logger.py`.

## Troubleshooting

### No Logs Appearing
1. Check if the `./logs/` directory exists and is writable
2. Verify the application has started correctly
3. Ensure you've performed operations that generate logs

### Performance Issues
1. Check the timing logs for slow operations
2. Use the analytics page to identify bottlenecks
3. Monitor the success rates for failing operations

### Log File Size
Monitor log file sizes in production and implement rotation as needed:
```bash
# Check log file sizes
ls -lah ./logs/

# Clear logs if needed (use with caution)
> ./logs/image-search.log
> ./logs/image-search-timing.log
```
