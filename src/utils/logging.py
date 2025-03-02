import logging
import os

# Global logger instance
_logger = None

def setup_logging(log_file_path='../Logs/debug.log', level=logging.DEBUG):
    """Sets up logging configuration and returns the global logger instance.
    
    This function will initialize the global logger if it hasn't been initialized yet.
    Subsequent calls will return the same logger instance.
    
    Args:
        log_file_path: Path to the log file
        level: Logging level
        
    Returns:
        The global logger instance
    """
    global _logger
    
    # If logger is already initialized, return it
    if _logger is not None:
        return _logger
        
    # Create log directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # Create a logger with a fixed name to ensure it's the same across all modules
    _logger = logging.getLogger('lear_app')
    _logger.setLevel(level)
    
    # Remove any existing handlers to avoid duplicates on re-initialization
    if _logger.handlers:
        _logger.handlers.clear()

    # Create file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    return _logger

def get_logger():
    """Returns the global logger instance.
    
    If the logger hasn't been initialized yet, it will be initialized with default settings.
    
    Returns:
        The global logger instance
    """
    global _logger
    
    if _logger is None:
        return setup_logging()
        
    return _logger
