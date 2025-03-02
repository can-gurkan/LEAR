from typing import List, Dict, Optional
from dataclasses import dataclass
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import logging
import re

from src.utils.storeprompts import prompts
from src.langchain_providers.base import LangchainProviderBase

@dataclass
class EnvironmentContext:
    """Represents the current state of the NetLogo environment"""
    food_distances: List[float]  # List of food distances
    agent_energy: float
    food_collected: int
    lifetime: int
    current_rule: str
    parent_rule: Optional[str]
    ticks: int

class TextBasedEvolution:
    """Handles text-based description generation for NetLogo code evolution"""
    
    def __init__(self, provider: Optional[LangchainProviderBase] = None):
        self.logger = logging.getLogger(__name__)
        self.provider = provider
    
    def _analyze_performance(self, context: EnvironmentContext) -> str:
        """Generate performance analysis description"""
        efficiency = context.food_collected / max(1, context.lifetime)
        
        return prompts["evolution_goals"].format(
            energy=context.agent_energy,
            food=context.food_collected,
            lifetime=context.lifetime,
            efficiency=efficiency
        )
    
    def _analyze_movement_pattern(self, rule: str) -> str:
        """Analyze current movement rule pattern using LLM if available, with basic pattern matching as fallback"""
        if not rule:
            return "No movement pattern"
            
        if self.provider:
            try:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", prompts["langchain"]["cot_system"]),
                    ("user", prompts["langchain"]["cot_template"].format(code=rule, base_prompt="", inputs=""))
                ])
                
                chain = prompt | self.provider.initialize_llm() | StrOutputParser()
                return chain.invoke({"input": ""})
                
            except Exception as e:
                self.logger.error(f"Error analyzing movement pattern with LLM: {str(e)}")
                # Fall through to basic pattern matching on error
        
        # Basic pattern matching (used when no LLM available or on LLM error)
        self.logger.warning("Using basic pattern matching for movement analysis")
        components = rule.split()
        pattern = []
        
        for i in range(0, len(components), 2):
            command = components[i]
            value = components[i + 1] if i + 1 < len(components) else ""
            
            if command == "fd":
                pattern.append("Moving forward with value {value}".format(direction="forward", value=value))
            elif command == "rt":
                pattern.append("Turning right with value {value}".format(direction="right", value=value))
            elif command == "lt":
                pattern.append("Turning left with value {value}".format(direction="left", value=value))
                
        return ", ".join(pattern) if pattern else "No movement pattern"
    
    def _generate_llm_explanation(self, movement_pattern: str, performance_metrics: str, parent_pattern: Optional[str] = None) -> str:
        """Generate explanation using LLM"""
        if not self.provider:
            self.logger.warning("No LLM provider available, using basic description")
            return f"Agent {movement_pattern}. {performance_metrics}"
            
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", prompts["langchain"]["cot_system"]),
                ("user", prompts["langchain"]["cot_template"].format(
                    movement_pattern=movement_pattern,
                    performance_metrics=performance_metrics,
                    parent_pattern=parent_pattern if parent_pattern else "None", base_prompt="", code="", inputs=""
                ))
            ])
            
            chain = prompt | self.provider.initialize_llm() | StrOutputParser()
            return chain.invoke({"input": ""})
            
        except Exception as e:
            self.logger.error(f"Error generating LLM explanation: {str(e)}")
            return f"Agent {movement_pattern}. {performance_metrics}"
    
    def generate_evolution_description(self, agent_info: list) -> str:
        """Generate a natural language description of the desired evolution"""
        try:
            # Parse agent info into context
            context = EnvironmentContext(
                food_distances=agent_info[1],
                current_rule=agent_info[0],
                parent_rule=agent_info[2] if len(agent_info) > 2 else None,
                agent_energy=agent_info[3] if len(agent_info) > 3 else 0,
                ticks=agent_info[4] if len(agent_info) > 4 else 0,
                food_collected=0,  # These would need to be added to agent_info
                lifetime=0
            )
            
            # Analyze movement patterns
            current_movement = self._analyze_movement_pattern(context.current_rule)
            parent_movement = self._analyze_movement_pattern(context.parent_rule) if context.parent_rule else None
            performance = self._analyze_performance(context)
            
            # Generate LLM-based explanation
            description = self._generate_llm_explanation(
                movement_pattern=current_movement,
                performance_metrics=performance,
                parent_pattern=parent_movement
            )
            
            # Add evolution guidance
            description += "\n\n" + prompts["evolution_goals"]
            
            return description
            
        except Exception as e:
            self.logger.error(f"Error generating evolution description: {str(e)}")
            return f"Basic agent with rule: {agent_info[0]}"
            
    def generate_pseudocode(self, agent_info: list, initial_pseudocode: str, original_code: str) -> str:
        """
        Generate pseudocode for NetLogo code evolution using prompts from the prompt dictionary.
        
        Args:
            agent_info: List containing agent state and environment information
            initial_pseudocode: The initial pseudocode to guide evolution
            original_code: The original NetLogo code
            
        Returns:
            Modified pseudocode
        """
        if not self.provider:
            self.logger.warning("No LLM provider available, using initial pseudocode")
            return initial_pseudocode
            
        try:
            # Use appropriate prompt from the prompts dictionary
            # Choose a appropriate prompt for pseudocode generation
            system_prompt = prompts["langchain"]["cot_system"]
            user_prompt = prompts["text_evolution"]["pseudo_gen_prompt"].format(initial_pseudocode)
        
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", user_prompt)
            ])
            
            chain = prompt | self.provider.initialize_model() | StrOutputParser()
            pseudocode_response = chain.invoke({"input": ""})
            
            if pseudocode_response:
                # Parse the response to extract the pseudocode - re to extract content within triple backticks
                
                match = re.search(r'```(.*?)```', pseudocode_response, re.DOTALL)
                if match:
                    pseudocode_response = match.group(1).strip()
                else:
                    self.logger.warning("No pseudocode found in response, using initial pseudocode.")
                    return initial_pseudocode
                
                        
            return pseudocode_response
            
        except Exception as e:
            self.logger.error(f"Error generating pseudocode: {str(e)}")
            return initial_pseudocode
