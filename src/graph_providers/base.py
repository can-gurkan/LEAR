from abc import abstractmethod
import os
import gin
import re
from typing import Optional, List
from dotenv import load_dotenv

from src.generators.base import BaseCodeGenerator
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils.storeprompts import prompts
from src.utils.logging import get_logger

# Load environment variables
load_dotenv()

@gin.configurable
class GraphProviderBase(BaseCodeGenerator):
    """Base class for graph-based code generators."""
    
    def __init__(self, verifier: NetLogoVerifier, retry_max_attempts: int = 5):
        """Initialize with verifier instance."""
        super().__init__(verifier)
        self.model = None  # To be set by child classes
        self.logger = get_logger()
        self.retry_handler.max_attempts = retry_max_attempts
        
    @abstractmethod
    def initialize_model(self):
        """Initialize and return provider-specific model."""
        pass

    def generate_code_with_model(self, agent_info: List, current_code: str,  evolution_description: Optional[str] = None, error_message: Optional[str] = None) -> str:
        """Generate code using the initialized model.

        Args:
            agent_info: List containing agent state and environment information
            evolution_description: Optional description for text-based evolution
            error_message: Optional error message for retry attempts

        Returns:
            Generated NetLogo code as string
        """
        try:
            if not self.model:
                self.model = self.initialize_model()

            prompt = self._build_prompt(current_code, evolution_description, error_message)
            # print(f"Prompt: {prompt}")
            code_response = self._generate_with_prompt(prompt)
            
            # If response is empty (error case), return original code
            if not code_response:
                self.logger.warning("Empty response from model, returning original code")
                return agent_info[0]
            
            # Extract code block from response
            match = re.search(r'```(.*?)```', code_response, re.DOTALL)
            if match:
                code_response = match.group(1).strip()
                # Replace netlogo with "" if it exists
                code_response = code_response.replace("netlogo", "").strip()
                
                
            return code_response

        except Exception as e:
            self.logger.error(f"Graph generation error: {str(e)}")
            return agent_info[0]

    def _build_prompt(self, current_code: str, evolution_description: Optional[str] = None, error_message: Optional[str] = None) -> str:
        """Build the prompt based on the given information."""
        if error_message:
            
            # self.logger.info(error_message)
            return prompts["retry_prompts"]["generate_code_with_error"].format(current_code, error_message)
        
        elif evolution_description:
            # Use evolution description for text-based evolution
            # return f"This is the evolution description: {evolution_description} Here is the code: {agent_info[0]}. Generate new code based on the above description."
            
            return prompts["text_evolution"]["code_gen_prompt"].format(evolution_description)

        else:
            # Use standard prompt
            base_prompt = self.get_base_prompt(current_code)
            # print(base_prompt)
            return base_prompt

    @abstractmethod
    def _generate_with_prompt(self, prompt: str) -> str:
        """Generate code using the model with the given prompt.

        Args:
            prompt: The prompt to send to the model

        Returns:
            Raw model response as string
        """
        pass
