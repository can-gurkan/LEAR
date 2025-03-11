import logging
import os

def setup_logging(log_file_path='../../Logs/debug.log', level=logging.DEBUG):
    """Sets up logging configuration."""

    # Create log directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logger = logging.getLogger(__name__)
    logger.setLevel(level)

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
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
