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
            
        #if not isinstance(agent_info[1], list) or len(agent_info[1]) != 3:
         #   return False, "Second element must be a list with exactly 3 food distances"
            
        #if not all(isinstance(x, (list)) for x in agent_info[1]):
         #   return False, "All food distances must be numbers"
            
        return True, None

    @gin.configurable
    def get_base_prompt(self, agent_info: list, model_type: str, model_prompt=None) -> str:
        """Construct and return base prompt."""
        
        # Considering only rule and food input for now
        # TO DO: get rid of food_input
        rule = agent_info[0]
        food_input = agent_info[1]
        
        prompt_library = LEARPrompts()
        prompt = getattr(prompt_library, model_prompt) 
                
        return prompt.format(rule, food_input)
    
    @abstractmethod
    def generate_code(self, agent_info: list) -> str:
        """Generate new NetLogo code based on agent info."""
        pass
