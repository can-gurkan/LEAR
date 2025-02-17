from typing import Union
    
from src.utils.config import load_config
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils.logging import setup_logging
from src.generators.groq import GroqCodeGenerator
from src.generators.claude import ClaudeCodeGenerator

from src.generators.langchain import LangChainCodeGenerator
from src.langchain_providers.groq_langchain import LangchainGroqGenerator
from src.langchain_providers.claude_langchain import LangchainClaudeGenerator
from src.langchain_providers.deepseek_langchain import LangchainDeepseekGenerator

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
        return GroqCodeGenerator(config['GROQ_API_KEY'], verifier, temp=0.65)
    elif model_type.lower() == "claude":
        return ClaudeCodeGenerator(config["ANTHROPIC_API_KEY"], verifier, temp=0.65)
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
        "deepseek": LangchainDeepseekGenerator(config['DEEPSEEK_API_KEY'])
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
        #logger.info(f"Starting code generation with model type: {model_type}")
        if use_text_evolution:
            provider = get_langchain_provider(model_type)
            langchain_generator = LangChainCodeGenerator(provider, verifier)
            result = langchain_generator.generate_code(agent_info, use_text_evolution=True)
            logger.info(f"Langchain code generation complete. Result: {result}")
            return result
        else:
            generator = get_code_generator(model_type)
            return generator.generate_code(agent_info)
    except Exception as e:
        logger.error(f"Error in mutate_code: {str(e)}")
        # print(f"Error in mutate_code: {str(e)}")
        return agent_info[0]  # Return original code on error
