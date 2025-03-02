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
from src.utils.logging import get_logger
from src.netlogo_code_generator.graph import NetLogoCodeGenerator
from src.graph_providers.unified_provider import create_graph_provider

config = load_config()
logger = get_logger()
logger.info("Loading NetLogoVerifier...")
verifier = NetLogoVerifier()
logger.info("NetLogoVerifier loaded.")

def get_graph_provider(model_type: str):
    """Get the appropriate Graph provider based on model type."""
    return create_graph_provider(model_type, verifier)

def mutate_code(agent_info: list, model_type: str = "groq", use_text_evolution: bool = False) -> str:
    """Generate evolved NetLogo code using graph-based evolution."""
    logger.info(f"Starting code generation with model type: {model_type}, use_text_evolution: {use_text_evolution}")

    # print(f"Agent info: {agent_info}")
    
    # Extract initial_pseudocode from agent_info if available
    initial_pseudocode = ""
    if len(agent_info) > 7:
        initial_pseudocode = agent_info[7]
    
    provider = get_graph_provider(model_type)
    graph_generator = NetLogoCodeGenerator(provider, verifier)
    result = graph_generator.generate_code(agent_info, initial_pseudocode, use_text_evolution)
    logger.info(f"Graph-based code generation complete. Result: {result}")
    return result




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
