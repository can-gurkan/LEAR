from abc import ABC, abstractmethod
from typing import Tuple, Optional
from pydantic import BaseModel

import logging
import gin

from src.utils.prompts import LEARPrompts
from src.utils.retry import CodeRetryHandler
from src.verification.verify_netlogo import NetLogoVerifier


class NLogoCode(BaseModel):
    new_code: str

@gin.register
class BaseCodeGenerator(ABC):
    def __init__(self, verifier: NetLogoVerifier):
        """Initialize with verifier instance."""
        self.verifier = verifier
        self.retry_handler = CodeRetryHandler(verifier)
        
    def validate_input(self, agent_info: list) -> Tuple[bool, Optional[str]]:
        """Validate the input format and content."""
        if not isinstance(agent_info, list) or len(agent_info) < 2:
            return False, "agent_info must be a list with atleast 2 elements"
        
        if not isinstance(agent_info[0], str):
            return False, "First element must be a string containing NetLogo code"
            
        # Check if this is a tag environment by examining the input
        input_data = agent_info[1]
        is_tag_env = False
        if isinstance(input_data, list) and len(input_data) == 4:
            # Tag environment has 4 inputs: 3 directional views plus tagged state
            if isinstance(input_data[3], bool):  # Last element is the tagged state
                is_tag_env = True
        
        if is_tag_env:
            # Validate tag environment inputs
            if not all(isinstance(x, list) for x in input_data[:3]):
                return False, "First three elements of input must be lists containing sensor readings"
            # Fourth element is already validated as boolean above
        else:
            # Validate food collection environment inputs
            if not isinstance(input_data, list) or len(input_data) != 3:
                return False, "Second element must be a list with exactly 3 food distances"
                
            if not all(isinstance(x, (int, float)) for x in input_data):
                return False, "All food distances must be numbers"
            
        return True, None

    @gin.configurable
    def get_base_prompt(self, agent_info: list, model_type: str, model_prompt=None, is_tag_env=None) -> str:
        """Construct and return base prompt."""
        
        # Considering only rule and food input for now
        rule = agent_info[0]
        input_data = agent_info[1]
        
        prompt_library = LEARPrompts()
        
        # Check if this is a tag environment - use explicit parameter if provided, otherwise detect automatically
        if is_tag_env is None:
            is_tag_env = False
            if isinstance(input_data, list) and len(input_data) == 4:
                # Tag environment has 4 inputs: 3 directional views plus tagged state
                if isinstance(input_data[3], bool):  # Last element is the tagged state
                    is_tag_env = True
        
        # Select appropriate prompt based on environment and model type
        if is_tag_env:
            # Use tag-specific prompt for tag environment
            if model_type.lower() == "groq":
                prompt = prompt_library.tag_groq_prompt
            elif model_type.lower() == "claude":
                prompt = prompt_library.tag_claude_prompt
            else:
                # Default to groq prompt for other models
                prompt = prompt_library.tag_groq_prompt
        else:
            # Use regular food-finding prompt for other environments
            if model_prompt:
                prompt = getattr(prompt_library, model_prompt, None)
            
            # Default prompts if model_prompt not specified or not found
            if not model_prompt or not prompt:
                if model_type.lower() == "groq":
                    prompt = prompt_library.groq_prompt3
                elif model_type.lower() == "claude":
                    prompt = prompt_library.claude_prompt3
                else:
                    prompt = prompt_library.groq_prompt3  # Default
        
        return prompt.format(rule, input_data)
    
    @abstractmethod
    def generate_code(self, agent_info: list, is_tag_env=None) -> str:
        """Generate code based on environment state."""
        pass
