from typing import List, Dict, Optional
from dataclasses import dataclass
from .prompts import LEARPrompts
import logging

@dataclass
class EnvironmentContext:
    """Represents the current state of the NetLogo environment"""
    food_distances: List[float]  # Distances in left, center, right cones
    agent_energy: float
    food_collected: int
    lifetime: int
    current_rule: str
    parent_rule: Optional[str]
    ticks: int

class TextBasedEvolution:
    """Handles text-based description generation for NetLogo code evolution"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def _analyze_food_distribution(self, distances: List[float]) -> str:
        """Analyze food distribution pattern in the agent's view cones"""
        descriptions = []
        directions = ['left', 'center', 'right']
        
        for direction, distance in zip(directions, distances):
            if distance == 0:
                descriptions.append(f"no food in {direction} direction")
            else:
                descriptions.append(f"food at distance {distance} in {direction} direction")
                
        return ", ".join(descriptions)
    
    def _analyze_performance(self, context: EnvironmentContext) -> str:
        """Generate performance analysis description"""
        efficiency = context.food_collected / max(1, context.lifetime)
        
        performance = []
        performance.append(f"Current energy level: {context.agent_energy}")
        performance.append(f"Total food collected: {context.food_collected}")
        performance.append(f"Agent lifetime: {context.lifetime} ticks")
        performance.append(f"Food collection efficiency: {efficiency:.2f} items per tick")
        
        return ". ".join(performance)
    
    def _analyze_movement_pattern(self, rule: str) -> str:
        """Analyze current movement rule pattern"""
        components = rule.split()
        pattern = []
        
        for i in range(0, len(components), 2):
            command = components[i]
            value = components[i + 1] if i + 1 < len(components) else ""
            
            if command == "fd":
                pattern.append(f"moves forward {value}")
            elif command == "rt":
                pattern.append(f"turns right {value}")
            elif command == "lt":
                pattern.append(f"turns left {value}")
                
        return ", ".join(pattern)
    
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
            
            # Build comprehensive description
            description_parts = [
                f"Current Movement Pattern: Agent {self._analyze_movement_pattern(context.current_rule)}",
                f"Environment State: {self._analyze_food_distribution(context.food_distances)}",
                f"Performance Metrics: {self._analyze_performance(context)}"
            ]
            
            if context.parent_rule:
                description_parts.append(
                    f"Evolved From: Agent previously {self._analyze_movement_pattern(context.parent_rule)}"
                )
            
            description = "\n".join(description_parts)
            
            # Add evolution guidance
            # Add evolution goals from centralized prompts
            prompt_library = LEARPrompts()
            description += "\n\n" + prompt_library.evolution_goals
            
            return description
            
        except Exception as e:
            self.logger.error(f"Error generating evolution description: {str(e)}")
            return f"Basic agent with rule: {agent_info[0]}"
