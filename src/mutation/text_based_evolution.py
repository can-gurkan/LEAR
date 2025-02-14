from typing import List, Dict, Optional
from dataclasses import dataclass
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import logging

from src.utils.prompts import LEARPrompts
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
        self.prompts = LEARPrompts()
        self.provider = provider
    
    def _analyze_performance(self, context: EnvironmentContext) -> str:
        """Generate performance analysis description"""
        efficiency = context.food_collected / max(1, context.lifetime)
        
        return self.prompts.evolution_performance.format(
            energy=context.agent_energy,
            food=context.food_collected,
            lifetime=context.lifetime,
            efficiency=efficiency
        )
    
    def _analyze_movement_pattern(self, rule: str) -> str:
        """Analyze current movement rule pattern using LLM if available, with basic pattern matching as fallback"""
        if not rule:
            return self.prompts.evolution_movement_pattern_none
            
        if self.provider:
            try:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", self.prompts.code_analysis_system_message),
                    ("user", self.prompts.code_analysis_user_message.format(code=rule))
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
                pattern.append(self.prompts.evolution_movement_pattern.format(direction="forward", value=value))
            elif command == "rt":
                pattern.append(self.prompts.evolution_movement_pattern.format(direction="right", value=value))
            elif command == "lt":
                pattern.append(self.prompts.evolution_movement_pattern.format(direction="left", value=value))
                
        return ", ".join(pattern) if pattern else self.prompts.evolution_movement_pattern_none
    
    def _generate_llm_explanation(self, movement_pattern: str, performance_metrics: str, parent_pattern: Optional[str] = None) -> str:
        """Generate explanation using LLM"""
        if not self.provider:
            self.logger.warning("No LLM provider available, using basic description")
            return f"Agent {movement_pattern}. {performance_metrics}"
            
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.prompts.explanation_system_message),
                ("user", self.prompts.explanation_user_message.format(
                    movement_pattern=movement_pattern,
                    performance_metrics=performance_metrics,
                    parent_pattern=parent_pattern if parent_pattern else "None"
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
            description += "\n\n" + self.prompts.evolution_goals_prompt
            
            return description
            
        except Exception as e:
            self.logger.error(f"Error generating evolution description: {str(e)}")
            return f"Basic agent with rule: {agent_info[0]}"
