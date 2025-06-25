import logging
import time
import functools
from datetime import datetime
import os
from typing import Any, Callable, Optional

class ImageSearchLogger:
    """
    Centralized logging and profiling utility for the image search application.
    """
    
    def __init__(self, log_file: str = "./logs/image-search.log"):
        self.log_file = log_file
        self.setup_logger()
    
    def setup_logger(self):
        """Set up the logger with proper formatting and file handling."""
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        self.logger = logging.getLogger('ImageSearchApp')
        self.logger.info("Image Search Application started")
    
    def log_info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log an error message with optional exception details."""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def log_warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def profile_function(self, func_name: Optional[str] = None):
        """
        Decorator to profile function execution time.
        
        Args:
            func_name: Optional custom name for the function being profiled
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                name = func_name or f"{func.__module__}.{func.__name__}"
                start_time = time.time()
                
                self.logger.info(f"Started: {name}")
                
                try:
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    self.logger.info(f"Completed: {name} - Execution time: {execution_time:.4f} seconds")
                    
                    # Also write timing to specific log format for profiling
                    self._log_timing(name, execution_time, "SUCCESS")
                    
                    return result
                    
                except Exception as e:
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    self.logger.error(f"Failed: {name} - Execution time: {execution_time:.4f} seconds - Error: {str(e)}")
                    self._log_timing(name, execution_time, "FAILED", str(e))
                    
                    raise e
            
            return wrapper
        return decorator
    
    def _log_timing(self, function_name: str, execution_time: float, status: str, error: Optional[str] = None):
        """Log timing information in a structured format."""
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | {function_name} | {execution_time:.4f}s | {status}"
        
        if error:
            log_entry += f" | Error: {error}"
        
        # Write to timing log file
        timing_log_file = "./logs/image-search-timing.log"
        os.makedirs(os.path.dirname(timing_log_file), exist_ok=True)
        
        with open(timing_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def log_search_operation(self, query: str, num_results: int, execution_time: float, results_found: int):
        """Log specific image search operation details."""
        log_message = (
            f"Image Search - Query: '{query}' | "
            f"Requested: {num_results} | "
            f"Found: {results_found} | "
            f"Time: {execution_time:.4f}s"
        )
        self.logger.info(log_message)
        
        # Also log to timing file
        self._log_timing(f"image_search_query", execution_time, "SUCCESS")
    
    def log_upload_operation(self, filename: str, execution_time: float, success: bool = True):
        """Log image upload operation details."""
        status = "SUCCESS" if success else "FAILED"
        log_message = f"Image Upload - File: '{filename}' | Time: {execution_time:.4f}s | Status: {status}"
        
        if success:
            self.logger.info(log_message)
        else:
            self.logger.error(log_message)
        
        self._log_timing(f"image_upload", execution_time, status)
    
    def log_reverse_search_operation(self, filename: str, execution_time: float, results_found: int):
        """Log reverse image search operation details."""
        log_message = (
            f"Reverse Search - Image: '{filename}' | "
            f"Found: {results_found} | "
            f"Time: {execution_time:.4f}s"
        )
        self.logger.info(log_message)
        self._log_timing(f"reverse_image_search", execution_time, "SUCCESS")

# Global logger instance
app_logger = ImageSearchLogger()
