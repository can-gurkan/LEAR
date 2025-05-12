import gin
import logging

logger = logging.getLogger(__name__)

@gin.configurable
def get_retry_config(max_attempts: int = 2):
    """
    Get the centralized retry configuration.
    This is the single source of truth for retry attempts in the system.
    
    Args:
        max_attempts: Maximum number of retry attempts allowed
        
    Returns:
        dict: Configuration dictionary containing retry settings
    """
    return {
        'max_attempts': max_attempts
    }

def should_retry(retry_count: int, error_message: str = None) -> bool:
    """
    Determine if a retry should be attempted based on the centralized configuration.
    
    Args:
        retry_count: Current number of retry attempts
        error_message: Optional error message that triggered the retry
        
    Returns:
        bool: True if should retry, False otherwise
    """
    config = get_retry_config()
    max_attempts = config['max_attempts']
    
    should_retry_value = retry_count < max_attempts and error_message is not None
    logger.info(f"Retry check - Attempts: {retry_count}/{max_attempts}, Error: {error_message}, Should retry: {should_retry_value}")
    
    return should_retry_value 