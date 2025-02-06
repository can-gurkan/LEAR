# config.py
from dotenv import load_dotenv
import os
import gin

def load_config():
    """Load environment variables from .env file"""
    load_dotenv()
    
    # Required environment variables
    required_vars = {
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
    }
    
    # Check for missing variables
    missing = [key for key, value in required_vars.items() if not value]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    # Load configurations from gin file
    gin.parse_config_file("config/default.gin")
        
    return required_vars

# Example usage
if __name__ == "__main__":
    try:
        config = load_config()
        print("Environment variables loaded successfully!")
    except ValueError as e:
        print(f"Error: {e}")