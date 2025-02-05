class LEARPrompts:
    """Collection of prompts used throughout the LEAR system"""
    
    def __init__(self):
        # Evolution goals used in text-based evolution
        self.evolution_goals = """Evolution Goals:
1. Optimize movement for efficient food collection
2. Balance exploration and exploitation
3. Maintain simple, efficient NetLogo commands
4. Consider both immediate food sources and long-term survival"""

        # Chain of thought prompt for langchain providers
        self.langchain_cot_system = "You are a NetLogo code evolution expert. Think step-by-step."
        self.langchain_cot_template = """{}
            
Current code block to evolve:
```netlogo
{code}
```

Food distance inputs: {inputs}

Analysis steps:
1. Identify patterns in existing code
2. Determine needed modifications based on food inputs
3. Propose updated code with clear explanations
4. Validate syntax before final answer"""

        self.groq_prompt = """You are an expert NetLogo movement code generator. Generate movement code following these precise specifications:

VALID COMMANDS AND SYNTAX:
- Movement: fd/forward, rt/right, lt/left
- Reporters: random, random-float, sin, cos
- Format: [command] [positive_number | reporter_expression]

CONSTRAINTS:
1. Commands must only use the above valid commands and reporters
2. All numbers must be positive
3. No variable definitions or new commands
4. Maximum 5 movement commands per sequence
5. Each command must be space-separated
6. Code must be a single line with no comments

INPUT CONTEXT:
- Current rule: {}
- Food sensor readings: {}
  - Each value is distance to nearest food (0 = no food)
  - Lower values indicate closer food
  - Use these to inform movement strategy

EXAMPLES OF VALID PATTERNS:
Input: [5, 0, 2]
Valid: rt random 45 fd 2 lt 30
Why: Turns right to explore when no food ahead, moves forward, adjusts left toward food

Input: [0, 3, 0]
Valid: fd 1 rt random-float 90 fd random-float 2
Why: Moves toward detected food, then random exploration

Input: [4, 4, 4]
Valid: fd 1 rt sin 45 fd 2 lt cos 30
Why: Uses trigonometric functions for complex movement when food is distant

INVALID EXAMPLES:
❌ fd -1 rt 90
❌ set x random 30
❌ forward 1.5 + 2
❌ rt random-normal 45 20

STRATEGIC GOALS:
1. Balance exploration and food-seeking behavior
2. Create unpredictable yet purposeful movement
3. Respond to sensor readings intelligently
4. Combine different movement patterns

Generate ONLY the movement code with no explanations or comments. Code must be runnable in NetLogo."""

        self.groq_prompt1 = """Modify the given NetLogo movement rule according to the following guidelines:

        1. Use only existing variables and data types; do not define new variables.
        2. Use only fd, rt, and lt for movement; exclude other NetLogo commands.
        3. Consider the distances to the nearest food in the three cone regions given in the observation list. If a distance is 0, no food is present in that region.
        4. The modified code should only contain movement commands.
        5. Provide a concise (less than 100 characters) NetLogo code with no comments or explanations.

        Example: Given rule: lt random 20 fd 1 Food input: [5, 2, 0] Updated rule: rt 20 fd 2

        INNOVATION GUIDELINES:

        - Do not reuse example codes
        - Develop unique movement patterns
        - Think about efficient food-finding strategies
        - Consider trade-offs between exploration and exploitation
        - Design for both immediate and long-term survival

        rule: {} 
        input: {}

        Remember, the goal is to create an efficient movement rule that balances exploration and exploitation, aiming to find food in both the short and long term."""
        
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

        self.claude_prompt = """You are an expert NetLogo movement code generator. Generate movement code following these precise specifications:

VALID COMMANDS AND SYNTAX:
- Movement: fd/forward, rt/right, lt/left
- Reporters: random, random-float, sin, cos
- Format: [command] [positive_number | reporter_expression]

CONSTRAINTS:
1. Commands must only use the above valid commands and reporters
2. All numbers must be positive
3. No variable definitions or new commands
4. Maximum 5 movement commands per sequence
5. Each command must be space-separated
6. Code must be a single line with no comments

INPUT CONTEXT:
- Current rule: {}
- Food sensor readings: {}
  
  - Each value is distance to nearest food (0 = no food)
  - Lower values indicate closer food
  - Use these to inform movement strategy

EXAMPLES OF VALID PATTERNS:
Input: [5, 0, 2]
Valid: rt random 45 fd 2 lt 30
Why: Turns right to explore when no food ahead, moves forward, adjusts left toward food

Input: [0, 3, 0]
Valid: fd 1 rt random-float 90 fd random-float 2
Why: Moves toward detected food, then random exploration

Input: [4, 4, 4]
Valid: fd 1 rt sin 45 fd 2 lt cos 30
Why: Uses trigonometric functions for complex movement when food is distant

INVALID EXAMPLES:
❌ fd -1 rt 90
❌ set x random 30
❌ forward 1.5 + 2
❌ rt random-normal 45 20

STRATEGIC GOALS:
1. Balance exploration and food-seeking behavior
2. Create unpredictable yet purposeful movement
3. Respond to sensor readings intelligently
4. Combine different movement patterns

Generate ONLY the movement code with no explanations or comments. Code must be runnable in NetLogo."""
        
        self.claude_prompt1 = """Modify the given NetLogo movement rule according to the following guidelines:

        1. Use only fd, rt, or lt commands with numbers or 'random N'
        2. Keep expressions simple - avoid complex arithmetic
        3. Use positive numbers only
        4. Format: Each command (fd/rt/lt) must be followed by either:
           - A single number (e.g., "fd 1")
           - random N (e.g., "rt random 30")
           - random-float N (e.g., "lt random-float 45")

        CURRENT STATE:
        - Current rule: {}
        - Food distances: {}
        
        EXAMPLES OF VALID CODE:
        - fd 1 rt random 30
        - lt 45 fd 2
        - rt random-float 90 fd 1
        
        Return ONLY the modified NetLogo code with no explanations."""
        
        
        
        self.claude_prompt2 = """You are an expert NetLogo agent movement behavior generator. Your task is to create sophisticated movement patterns that balance efficiency with complexity. Generate code that follows these specifications while pushing the boundaries of complexity:

        CORE COMMANDS AND FUNCTIONS:
        Movement Commands: fd/forward, rt/right, lt/left
        Mathematical Functions: random, random-float, sin, cos
        Format: [command] [number | expression]

        CURRENT STATE:
        Original Rule: {0}
        Sensor Data: {1}
        - Represents [left_cone, front_cone, right_cone] distances
        - 0 indicates no food in that direction
        - Lower non-zero values mean closer food

        COMPLEXITY GOALS:
        1. Combine trigonometric functions with random movements
        2. Create multi-step movement sequences
        3. Use sensor data to inform movement decisions
        4. Balance predictable and chaotic patterns

        EXAMPLE PATTERNS - From Simple to Complex:

        Basic Valid:
        rt random 45 fd 2

        Intermediate Valid:
        rt sin 60 fd random-float 3 lt cos 45

        Advanced Valid:
        fd random-float 2 rt sin 90 fd 1 lt cos random 60 fd random-float 3

        INNOVATION GUIDELINES:
        - Combine multiple movement commands creatively
        - Use mathematical functions in unexpected ways
        - Create emergent behavior patterns
        - Design for both local optimization and global exploration
        - Consider both immediate food-seeking and long-term survival

        TECHNICAL CONSTRAINTS:
        - Use only allowed commands and functions
        - Maintain positive numbers
        - Keep code executable in NetLogo
        - No variable definitions or new commands
        - Commands must be space-separated

        You are encouraged to be creative and generate complex patterns that go beyond basic movement rules. Focus on creating sophisticated behaviors that could lead to emergent patterns in the simulation.

        Return ONLY the NetLogo code with no explanations. Make it mathematically interesting and behaviorally complex while ensuring it remains valid NetLogo syntax."""
