from abc import ABC, abstractmethod
from typing import Tuple, Optional
from pydantic import BaseModel
from prompts import LEARPrompts
import logging

class NLogoCode(BaseModel):
    new_code: str

class BaseCodeGenerator(ABC):
    def validate_input(self, agent_info: list) -> Tuple[bool, Optional[str]]:
        """Validate the input format and content."""
        if not isinstance(agent_info, list) or len(agent_info) < 2:
            return False, "agent_info must be a list with atleast 2 elements"
        
        if not isinstance(agent_info[0], str):
            return False, "First element must be a string containing NetLogo code"
            
        if not isinstance(agent_info[1], list) or len(agent_info[1]) != 3:
            return False, "Second element must be a list with exactly 3 food distances"
            
        if not all(isinstance(x, (int, float)) for x in agent_info[1]):
            return False, "All food distances must be numbers"
            
        return True, None

    def get_base_prompt(self, agent_info: list, model_type: str) -> str:
        """Construct and return base prompt."""
        
        # Considering only rule and food input for now
        rule = agent_info[0]
        food_input = agent_info[1]
        
        prompt_library = LEARPrompts()
        
        if model_type == 'groq':
            prompt = prompt_library.groq_prompt2
        elif model_type == 'claude':
            prompt = prompt_library.claude_prompt2
                
        return prompt.format(rule, food_input)
    
    @abstractmethod
    def generate_code(self, agent_info: list) -> str:
        """Generate new NetLogo code based on agent info."""
        pass