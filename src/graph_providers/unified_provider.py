import os
import logging
import gin
from typing import Optional, List, Any
from enum import Enum

from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.graph_providers.base import GraphProviderBase
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils.storeprompts import prompts

# Define supported models
class SupportedModels(Enum):
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    OPENAI = "openai"

@gin.configurable
class GraphUnifiedProvider(GraphProviderBase):
    """
    Unified graph-based provider that supports multiple models.
    """
    
    # Model name parameters defined at init level to make them configurable
    def __init__(self, model_name: str, verifier: NetLogoVerifier, 
                 temperature: float = 0.7, max_tokens: int = 1000,
                 claude_model_name: str = "claude-3-5-sonnet-20240229",
                 deepseek_model_name: str = "deepseek-chat",
                 groq_model_name: str = "llama-3.3-70b-versatile",
                 openai_model_name: str = "gpt-4o"):
        """
        Initialize with model name and verifier instance.
        
        Args:
            model_name: Type of model to use
            verifier: NetLogoVerifier instance
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            claude_model_name: Model name for Claude
            deepseek_model_name: Model name for DeepSeek
            groq_model_name: Model name for Groq
            openai_model_name: Model name for OpenAI
        """
        super().__init__(verifier)
        self.model_name = model_name
        self.model = None
        self.api_key = None
        self.logger = logging.getLogger(__name__)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.claude_model_name = claude_model_name
        self.deepseek_model_name = deepseek_model_name
        self.groq_model_name = groq_model_name
        self.openai_model_name = openai_model_name

        # Set API key based on model name
        if self.model_name == SupportedModels.CLAUDE.value:
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        elif self.model_name == SupportedModels.DEEPSEEK.value:
            self.api_key = os.getenv('DEEPSEEK_API_KEY')
            if not self.api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        elif self.model_name == SupportedModels.GROQ.value:
            self.api_key = os.getenv('GROQ_API_KEY')
            if not self.api_key:
                raise ValueError("GROQ_API_KEY environment variable is required")
        elif self.model_name == SupportedModels.OPENAI.value:
            self.api_key = os.getenv('OPENAI_API_KEY')
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
        else:
            raise ValueError(f"Unsupported model name: {self.model_name}")
            
    def initialize_model(self):
        """Initialize and return provider-specific model based on model name."""
        try:
            if self.model_name == SupportedModels.CLAUDE.value:
                model = ChatAnthropic(
                    model=self.claude_model_name,
                    anthropic_api_key=self.api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            elif self.model_name == SupportedModels.DEEPSEEK.value:
                model = ChatDeepSeek(
                    model_name=self.deepseek_model_name,
                    api_key=self.api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            elif self.model_name == SupportedModels.GROQ.value:
                model = ChatGroq(
                    model_name=self.groq_model_name,
                    groq_api_key=self.api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            elif self.model_name == SupportedModels.OPENAI.value:
                model = ChatOpenAI(
                    model=self.openai_model_name,
                    openai_api_key=self.api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            else:
                raise ValueError(f"Unsupported model name: {self.model_name}")
            return model

        except Exception as e:
            self.logger.error(f"Failed to initialize model for {self.model_name}: {str(e)}")
            raise
            
    def _generate_with_prompt(self, prompt: str) -> str:
        """Generate code using the model with the given prompt."""
        try:
            if not self.model:
                self.model = self.initialize_model()
                
            # Create a system message with the chain-of-thought prompt
            messages = [
                ("system", prompts["langchain"]["cot_system"]),
                ("user", prompt)
            ]
            
            # Create a chat prompt template
            chat_prompt = ChatPromptTemplate.from_messages(messages)
            
            # Create a chain with the model and output parser
            chain = chat_prompt | self.model | StrOutputParser()
            
            # Invoke the chain
            response = chain.invoke({})
            
            # print(f"Outputtttt: {response}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating with prompt: {str(e)}")
            # Return empty string on error, the parent method will handle it
            return ""
            
    def generate_code(self, agent_info: List, use_text_evolution: bool = False) -> str:
        """
        Generate code using the model.
        
        Args:
            agent_info: List containing agent state and environment information
            use_text_evolution: Whether to use text-based evolution approach
            
        Returns:
            Generated NetLogo code as string
        """
        try:
            # Extract initial_pseudocode from agent_info if available
            initial_pseudocode = ""
            if len(agent_info) > 7:
                initial_pseudocode = agent_info[7]
                
            # Extract modified_pseudocode from agent_info if available
            modified_pseudocode = None
            if len(agent_info) > 8:
                modified_pseudocode = agent_info[8]
                
            # For text-based evolution, use the modified_pseudocode if available
            evolution_description = None
            if use_text_evolution and modified_pseudocode:
                evolution_description = modified_pseudocode
            elif use_text_evolution and initial_pseudocode:
                evolution_description = initial_pseudocode
                
            return self.generate_code_with_model(agent_info, evolution_description)
            
        except Exception as e:
            self.logger.error(f"Error in generate_code: {str(e)}")
            return agent_info[0]  # Return original code on error


@gin.configurable
def create_graph_provider(model_name: str = "groq", verifier: NetLogoVerifier = None):
    """
    Factory method to create a graph provider based on model name.
    
    Args:
        model_name: Type of model to use ("groq", "claude", "openai", or "deepseek")
        verifier: NetLogoVerifier instance for code validation
        
    Returns:
        Initialized GraphUnifiedProvider instance
        
    Raises:
        ValueError: If unsupported model type provided
    """
    return GraphUnifiedProvider(model_name, verifier)
