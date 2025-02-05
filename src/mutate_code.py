from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_providers.base import LangchainProviderBase
    
from config import load_config
from verify_netlogo_code import NetLogoVerifier
from logging_config import setup_logging
from groq_generator import GroqCodeGenerator
from claude_generator import ClaudeCodeGenerator

from langchain_generator import LangChainCodeGenerator
from langchain_providers.groq_langchain import LangchainGroqGenerator
from langchain_providers.claude_langchain import LangchainClaudeGenerator
# from langchain_providers.openai_langchain import LangchainOpenAIGenerator
# from langchain_providers.deepseek_langchain import LangchainDeepseekGenerator
    

# LOG_FILE = "../Logs/netlogo_evolution.log"
# # Create log file if it doesn't exist
# os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# logging.basicConfig(
#     filename=LOG_FILE,
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )


config = load_config()
verifier = NetLogoVerifier()
logger = setup_logging()


def get_code_generator(model_type: str = "groq") -> Union[GroqCodeGenerator, ClaudeCodeGenerator]:
    
    """Get the appropriate direct code generator based on model type.
    
    Args:
        model_type: Type of model to use ("groq" or "claude")
        
    Returns:
        Initialized code generator instance
        
    Raises:
        ValueError: If unsupported model type provided
    """
    if model_type.lower() == "groq":
        return GroqCodeGenerator(config['GROQ_API_KEY'], verifier)
    elif model_type.lower() == "claude":
        return ClaudeCodeGenerator(config["ANTHROPIC_API_KEY"], verifier)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
def get_langchain_provider(model_type: str):
    """Get the appropriate LangChain provider based on model type.
    
    Args:
        model_type: Type of LangChain provider to use ("groq", "claude", "openai", or "deepseek")
        
    Returns:
        Initialized LangChain provider instance
        
    Raises:
        ValueError: If unsupported provider type provided
        ImportError: If required provider module not found
    """
    
    providers = {
        "groq": LangchainGroqGenerator(config['GROQ_API_KEY']),
        "claude": LangchainClaudeGenerator(config['ANTHROPIC_API_KEY']),
        # "openai": LangchainOpenAIGenerator(config['OPENAI_API_KEY']),
        # "deepseek": LangchainDeepseekGenerator(config['DEEPSEEK_API_KEY'])
    }
    
    if model_type.lower() not in providers:
        raise ValueError(f"Unsupported LangChain provider type: {model_type}")
    
    return providers[model_type.lower()]

def mutate_code(agent_info: list, model_type: str = "groq", use_text_evolution: bool = False) -> str:
    """Generate evolved NetLogo code using either direct or text-based evolution.
    
    Args:
        agent_info: List containing agent state and environment information
        model_type: Type of LLM to use ("groq", "claude", "openai", or "deepseek")
        use_text_evolution: Whether to use text-based evolution approach
        
    Returns:
        Evolved NetLogo code as string
    """
    try:
        logger.info(f"Starting code generation with model type: {model_type}")
        if use_text_evolution:
            provider = get_langchain_provider(model_type)
            langchain_generator = LangChainCodeGenerator(provider, verifier)
            result = langchain_generator.generate_code(agent_info, use_text_evolution=True)
            logger.info(f"Langchain code generation complete. Result: {result}")
            return result
        else:
            generator = get_code_generator(model_type)
            return generator.generate_code(agent_info, use_text_evolution=False)
    except Exception as e:
        logger.error(f"Error in mutate_code: {str(e)}")
        # print(f"Error in mutate_code: {str(e)}")
        return agent_info[0]  # Return original code on error

# def mutate_code(agent_info):
#     """Perform rule mutation proided current rule and environment obseration."""
    
#     try:
#         # print(agent_info)
#         client = instructor.from_groq(Groq(api_key=GROQ_API_KEY), 
#                                       mode=instructor.Mode.JSON)

#         prompt = get_prompt(agent_info=agent_info)

#         new_code = client.chat.completions.create(
#             model="llama-3.3-70b-versatile", # "llama-3.1-70b-versatile", 
#             response_model=NLogoCode,
#             messages=[
#                 {"role": "system", 
#                  "content": """You are an expert in evolving NetLogo agent behaviors.
#                 Focus on creating efficient, survival-optimized netlogo code."""},
#                 {
#                 "role": "user",
#                 "content": prompt
#                 }
#             ],
#             temperature=0.65,
#         )

#         # print(f"New Code : {new_code.new_code}")
    
#         # Check safety
#         is_safe = verifier.is_safe(new_code.new_code)
        
#         if is_safe:
#             return new_code.new_code
#         else:
#             print(f'Unsafe code generated. Returning initial command')
#             return agent_info[0]
        
#     except Exception as e:
#         print(f"Encountered Error: {e}")
#         return agent_info[0]
    
# def get_prompt(agent_info):
#     """Construct and return prompt provided current rule and environment observations"""
#     rule = agent_info[0]
#     food_input = agent_info[1]
    
    # prompt = f"""Modify the given NetLogo movement rule according to the following guidelines:

    #     1. Use only existing variables and data types; do not define new variables.
    #     2. Use only fd, rt, and lt for movement; exclude other NetLogo commands.
    #     3. Consider the distances to the nearest food in the three cone regions given in the observation list. If a distance is 0, no food is present in that region.
    #     4. The modified code should only contain movement commands.
    #     5. Provide a concise (less than 100 characters) NetLogo code with no comments or explanations.

    #     Example: Given rule: lt random 20 fd 1 Food input: [5, 2, 0] Updated rule: rt 20 fd 2

    #     INNOVATION GUIDELINES:

    #     - Do not reuse example codes
    #     - Develop unique movement patterns
    #     - Think about efficient food-finding strategies
    #     - Consider trade-offs between exploration and exploitation
    #     - Design for both immediate and long-term survival

    #     rule: {rule} 
    #     input: {food_input}

    #     Remember, the goal is to create an efficient movement rule that balances exploration and exploitation, aiming to find food in both the short and long term."""

#     prompt = f"""Modify the given NetLogo movement rule according to the following guidelines:

#          1. Use only fd, rt, or lt commands with numbers or 'random N'
#          2. Keep expressions simple - avoid complex arithmetic
#          3. Use positive numbers only
#          4. Format: Each command (fd/rt/lt) must be followed by either:
#             - A single number (e.g., "fd 1")
#             - random N (e.g., "rt random 30")
#             - random-float N (e.g., "lt random-float 45")
            
#          CURRENT STATE:
#          - Current rule: {rule}
#          - Food distances: {food_input}
       
#          EXAMPLES OF VALID CODE:
#          - fd 1 rt random 30
#          - lt 45 fd 2
#          - rt random-float 90 fd 1
       
#          Return ONLY the modified NetLogo code with no explanations."""
    
#     return prompt

if __name__ == "__main__":
    config = load_config()

    # For direct code generation
    result = mutate_code(agent_info, model_type="groq", use_text_evolution=False)

# For text-based evolution with any supported provider
# result = mutate_code(agent_info, model_type="claude", use_text_evolution=True)
