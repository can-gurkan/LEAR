from typing import Union
import logging
from config import load_config
from verify_netlogo_code import NetLogoVerifier
from groq_generator import GroqCodeGenerator
from claude_generator import ClaudeCodeGenerator
import os

LOG_FILE = "../Logs/netlogo_evolution.log"
# Create log file if it doesn't exist
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


config = load_config()
verifier = NetLogoVerifier()


def get_code_generator(model_type: str = "groq") -> Union[GroqCodeGenerator, ClaudeCodeGenerator]:
    if model_type.lower() == "groq":
        return GroqCodeGenerator(config['GROQ_API_KEY'], verifier, temp=0.65)
    elif model_type.lower() == "claude":
        return ClaudeCodeGenerator(config["ANTHROPIC_API_KEY"], verifier, temp=0.65)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
def mutate_code(agent_info: list, model_type: str = "groq") -> str:
    try:
        generator = get_code_generator(model_type)
        return generator.generate_code(agent_info)
    except Exception as e:
        logging.error(f"Error in mutate_code: {str(e)}")
        # print(f"Error in mutate_code: {str(e)}")
        return 
