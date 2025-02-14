class LEARPrompts:
    """Collection of prompts used throughout the LEAR system"""
    
    def __init__(self):
        # Evolution goals used in text-based evolution
        self.evolution_goals = "Optimize movement for food, balance exploration, keep commands simple."

        # Chain of thought prompt for langchain providers
        self.langchain_cot_system = "You are a NetLogo expert."
        self.langchain_cot_template = """Evolve code:\n{code}\n\nInputs: {inputs}"""

        self.evolution_performance = "Energy: {energy}, Food: {food}, Lifetime: {lifetime}, Efficiency: {efficiency:.2f}"
        self.evolution_movement_pattern = "moves {direction} {value}"
        self.evolution_movement_pattern_none = "no movement"
        self.evolution_goals_prompt = "Optimize movement for food, balance exploration, keep commands simple."

        # Code analysis prompts
        self.code_analysis_system_message = """You are a NetLogo expert specializing in analyzing agent behavior code. 
Provide clear, natural language descriptions of NetLogo code patterns, explaining what the code does in simple terms."""

        self.code_analysis_user_message = """Analyze this NetLogo code and describe what it does:
{code}

Focus on:
1. Movement patterns and conditions
2. Decision-making logic
3. Use of variables and reporters
4. Overall behavior strategy

Provide a clear, concise description that a non-programmer could understand."""

        # LLM-based explanation prompts
        self.explanation_system_message = """You are a NetLogo expert analyzing agent behavior. Provide clear, concise explanations of agent movement patterns and their effectiveness in collecting food."""
        
        self.explanation_user_message = """Analyze the agent's behavior and environment:

Current Movement: {movement_pattern}
Performance: {performance_metrics}
Previous Movement (if any): {parent_pattern}

Explain:
1. How effective is the current movement pattern?
2. How well does it respond to the environment?
3. What improvements could make it more effective?

Keep the explanation concise and focused on behavior analysis."""

        self.langchain_system_message = "You are a NetLogo expert."
        self.langchain_user_message_evolution = """Evolve code:\n{code}\n\nAnalysis: {evolution_description}"""

        self.langchain_user_message = """Evolve code:\n{code}\n\nInputs: {inputs}"""

        self.groq_prompt = """You are an expert NetLogo movement code generator. Generate code:
- Movement: fd/forward, rt/right, lt/left
- Reporters: random, random-float, sin, cos
Format: [command] [number | reporter]

INPUT CONTEXT:
- Current rule: {}
- Food: {} (0 = no food, lower = closer)

Generate ONLY the code."""

        self.groq_prompt1 = """Modify NetLogo movement rule:
1. Use only existing variables
2. Use only fd, rt, lt
3. Consider food distances (0 = no food)
4. Only movement commands
5. < 100 chars, no comments

rule: {} 
input: {}"""
        
        self.groq_prompt2 = """You are an expert NetLogo coder. You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible. Improve the given agent movement code following these precise specifications:

INPUT CONTEXT:
- Current rule: {}
- Food sensor readings: {}
  - Input list contains three values representing distances to food in three cone regions of 20 degrees each
  - The first item in the input list is the distance to the nearest food in the left cone, the second is the right cone, and the third is the front cone
  - Each value encodes the distance to nearest food source where a value of 0 indicates no food
  - Non-zero lower values indicate closer food
  - Use these to inform movement strategy

CONSTRAINTS:
1. Do not include code to kill or control any other agents
2. Do not include code to interact with the environment
3. Do not include code to change the environment
4. Do not include code to create new agents
5. Do not include code to create new food sources
6. Do not include code to change the rules of the simulation

EXAMPLES OF VALID PATTERNS:
Current Rule: fd 1 rt random 45 fd 2 lt 30
Valid: ifelse item 0 input != 0 [rt 15 fd 0.5] [rt random 30 lt random 30 fd 5]
Why: Turns right and goes forward a little to reach food if the first element of input list contains a non-zero value, else moves forward in big steps and turns randomly to explore

INVALID EXAMPLES:
❌ ask turtle 1 [die]
❌ ask other turtles [die]
❌ set energy 100
❌ hatch-food 5
❌ clear-all

STRATEGIC GOALS:
1. Balance exploration and food-seeking behavior
2. Respond to sensor readings intelligently
3. Combine different movement patterns

Generate ONLY the movement code. Code must be runnable in NetLogo in the context of a turtle."""

        self.claude_prompt = """You are an expert NetLogo movement code generator. Generate code:
- Movement: fd/forward, rt/right, lt/left
- Reporters: random, random-float, sin, cos
Format: [command] [number | reporter]

INPUT CONTEXT:
- Current rule: {}
- Food: {} (0 = no food, lower = closer)

Generate ONLY the code."""
        
        self.claude_prompt1 = """Modify NetLogo movement rule:
1. Use only fd, rt, lt, random N
2. Keep expressions simple
3. Positive numbers only
4. Format: fd/rt/lt -> number or random N

CURRENT STATE:
- Rule: {}
- Food: {}
        
Return ONLY the code."""
        
        
        
        self.claude_prompt2 = """You are an expert NetLogo agent movement behavior generator creating sophisticated patterns.

CORE:
Movement: fd/forward, rt/right, lt/left
Math: random, random-float, sin, cos
Format: [command] [number | expression]

CURRENT STATE:
Rule: {0}
Sensor: {1} (left, front, right, 0 = no food, lower = closer)

Return ONLY the code."""

        self.claude_prompt3 = """You are an expert NetLogo coder. You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible. Improve the given agent movement code following these precise specifications:

INPUT CONTEXT:
- Current rule: {}
- Food sensor readings: {}
  - Input list contains three values representing distances to food in three cone regions of 20 degrees each
  - The first item in the input list is the distance to the nearest food in the left cone, the second is the right cone, and the third is the front cone
  - Each value encodes the distance to nearest food source where a value of 0 indicates no food
  - Non-zero lower values indicate closer food
  - Use these to inform movement strategy

CONSTRAINTS:
1. Do not include code to kill or control any other agents
2. Do not include code to interact with the environment
3. Do not include code to change the environment
4. Do not include code to create new agents
5. Do not include code to create new food sources
6. Do not include code to change the rules of the simulation

EXAMPLES OF VALID PATTERNS:
Current Rule: fd 1 rt random 45 fd 2 lt 30
Valid: ifelse item 0 input != 0 [rt 15 fd 0.5] [rt random 30 lt random 30 fd 5]
Why: Turns right and goes forward a little to reach food if the first element of input list contains a non-zero value, else moves forward in big steps and turns randomly to explore

INVALID EXAMPLES:
❌ ask turtle 1 [die]
❌ ask other turtles [die]
❌ set energy 100
❌ hatch-food 5
❌ clear-all

STRATEGIC GOALS:
1. Balance exploration and food-seeking behavior
2. Respond to sensor readings intelligently
3. Combine different movement patterns

Generate ONLY the movement code. Code must be runnable in NetLogo in the context of a turtle."""
