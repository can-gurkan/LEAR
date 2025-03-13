from typing import Union
import os
from pathlib import Path
# Ensure the script is run from the correct directory

# Add parent directory to path
import sys
import os
import sys
from pathlib import Path

# Add project root directory to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

print("Current working directory:", os.getcwd())

from src.utils.config import load_config
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils import logging
from src.netlogo_code_generator.graph import NetLogoCodeGenerator
from src.graph_providers.unified_provider import create_graph_provider

config = load_config()
logger = logging.get_logger()
logger.info("Loading NetLogoVerifier...")
verifier = NetLogoVerifier()
logger.info("NetLogoVerifier loaded.")

def get_graph_provider(model_type: str):
    """Get the appropriate Graph provider based on model type."""
    return create_graph_provider(model_type, verifier)

def mutate_code(agent_info: list, model_type: str = "groq", use_text_evolution: bool = False) -> tuple:
    """
    Generate evolved NetLogo code using graph-based evolution.
    
    Returns:
        tuple: (new_rule, text) containing the new rule and the descriptive text (pseudocode)
    """
    logger.info(f"Starting code generation with model type: {model_type}, use_text_evolution: {use_text_evolution}")

    # print(f"Agent info: {agent_info}")
    
    # Extract current text from agent_info if available (at index 5)
    current_text = ""
    if len(agent_info) > 5:
        current_text = agent_info[5]
    
    provider = get_graph_provider(model_type)
    graph_generator = NetLogoCodeGenerator(provider, verifier)
    result = graph_generator.generate_code(agent_info, current_text, use_text_evolution)
    
    # Check if result is a tuple (new_rule, modified_pseudocode)
    if isinstance(result, tuple) and len(result) == 2:
        new_rule, text = result
    else:
        # For backward compatibility, if result is just a string (the code),
        # then use the current text as the text value
        new_rule = result
        text = current_text
    
    logger.info(f"Graph-based code generation complete. Result code: {new_rule}")
    logger.info(f"Text: {text}")
    
    return (new_rule, text)




#  py:run "from src.mutation.mutate_code import mutate_code"
#   py:set "llm_type" llm-type
#   ;;; {{{TO DO: Change later so that get_base prompt doesn't require agent_info and maybe llm_type}}}
#   py:set "agent_info" [0 0 0 0 0]
#   let base-prompt py:runresult "get_code_generator(llm_type).get_base_prompt(agent_info,llm_type)"
#   py:set "base_prompt" base-prompt



# if __name__ == "__main__":
#     # Example usage
#     agent_info = ['lt random 20 rt random 20 fd 1', [4, 0, 0], 'lt random 20 rt random 20 fd 1', 4, 101, 4, 102, 'Move forward and turn randomly to explore the environment and find food', '']
#     model_type = "claude"
#     use_text_evolution = True
#     mutated_code = mutate_code(agent_info, model_type, use_text_evolution)
#     # print(mutated_code)
