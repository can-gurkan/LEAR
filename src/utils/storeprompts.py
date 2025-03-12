"""Collection of prompts used throughout the LEAR system"""

prompts = {
    # Evolution goals used in text-based evolution
    "evolution_goals": """Evolution Goals:
    1. Optimize movement for efficient food collection
    2. Balance exploration and exploitation
    3. Maintain simple, efficient NetLogo commands
    4. Consider both immediate food sources and long-term survival""",



    # Text based evolution prompts
    "text_evolution": {
      "pseudo_gen_prompt": """You are an AI assistant tasked with improving the movement code for a turtle agent in NetLogo. Your goal is to create new pseudocode with slight modifications using paradigms of genetic programming. The improved code should help the agent collect as much food as possible while adhering to specific constraints and strategic goals.

      Evolution Goals:
      1. Optimize movement for efficient food collection
      2. Balance exploration and exploitation
      3. Maintain simple, efficient NetLogo commands
      4. Consider both immediate food sources and long-term survival

      You will be given this initial pseudocode to improve:

      <initial_pseudocode>
      {}
      </initial_pseudocode>

      STRICT GUIDELINES FOR PSEUDOCODE CREATION:
      
      1. FOCUS ON THESE MOVEMENT CONCEPTS ONLY:
         - "Move forward" (will become fd or forward in NetLogo)
         - "Turn right" (will become rt or right in NetLogo)
         - "Turn left" (will become lt or left in NetLogo)
         - Randomness (will use random or random-float in NetLogo)
         - Simple trigonometric concepts (sin, cos)
         - Conditional movements based on food sensor readings
      
      2. ABSOLUTELY FORBIDDEN CONCEPTS:
         - DO NOT include any reference to "of" relationships between agents
         - DO NOT create or reference any variables that don't exist
         - DO NOT include asking other agents to perform actions
         - DO NOT include creating or killing agents
         - DO NOT include setting or changing environment variables
      
      3. ALLOWED STRUCTURE:
         - You may include "if/else" logic based on the "input" list values
         - Basic example: "If there is food to the left, turn left and move forward, otherwise turn randomly and move forward"
         
      4. FORMATTING:
         - Keep the pseudocode simple, concise and readable
         - Use plain English descriptions of movement patterns
         - Focus on turtle movement logic only

      To improve the pseudocode, follow these guidelines:
      1. Analyze the initial pseudocode to understand the existing movement strategy
      2. Consider ways to balance exploration and food-seeking behavior
      3. Combine different movement patterns to create a more effective strategy
      4. Ensure that the new pseudocode adheres to the given constraints

      Present your improved pseudocode enclosed in triple backticks:

      ```
      [Your improved pseudocode here]
      ```

      Do not include any explanations outside the code block.
      """,


      "code_gen_prompt": """You are tasked with converting pseudocode into well-structured NetLogo code for agent movement. Your goal is to generate only the movement code based on the provided pseudocode, adhering to specific constraints and requirements.

    Here is the pseudocode you will be working with:
    
    <pseudocode>
    {}
    </pseudocode>
    
    STRICT GUIDELINES FOR CODE GENERATION:
    
    1. VALID COMMANDS ONLY:
       - Use only these movement commands: fd, forward, rt, right, lt, left
       - Use only these reporters: random, random-float, sin, cos, item
    
    2. ABSOLUTELY FORBIDDEN:
       - DO NOT use the "of" primitive/reporter - this will always cause errors
       - DO NOT use any non-existent or undefined variables
       - DO NOT use "ask", "with", "turtles", "patches" - these are not allowed
       - DO NOT use "set", "let", or create any variables
    
    3. ALLOWED STRUCTURE:
       - You may use "if/ifelse" statements with item checks on the "input" list
       - Basic example: ifelse item 0 input != 0 [fd 1] [rt 90 fd 2]
       
    4. FORMATTING:
       - Each command (fd/rt/lt) must be followed by a number or simple expression
       - All commands must be properly separated by spaces
       - Keep the code simple, focused only on movement
    
    5. OTHER CONSTRAINTS:
       a. Do not include code to kill or control any other agents
       b. Do not include code to interact with the environment
       c. Do not include code to change the environment
       d. Do not include code to create new agents
       e. Do not include code to create new food sources
       f. Do not include code to change the rules of the simulation
    
    Your task is to carefully analyze the provided pseudocode and translate it into NetLogo code that represents the agent's movement strategy. Focus solely on the movement aspects described in the pseudocode.
    
    Present your generated NetLogo code enclosed in triple backticks, following this format:
    
    ```
    [Your generated NetLogo code here]
    ```
    
    Ensure that your code accurately reflects the movement strategy described in the pseudocode while adhering to NetLogo syntax and the specified constraints. Do not add any explanations or comments outside the code block."""
    },
    
    
    "retry_prompts": {
      
      "generate_code_with_error": """You are an expert NetLogo coder tasked with fixing a movement code error for a turtle agent. Your goal is to update the provided NetLogo movement code to fix the error message shown below.

      Here is the current rule:
      {}

      Here is the error message:
      {}
      
      STRICT GUIDELINES FOR FIXING THE CODE:
      
      1. VALID COMMANDS ONLY:
         - Use only these movement commands: fd, forward, rt, right, lt, left
         - Use only these reporters: random, random-float, sin, cos, item
      
      2. ABSOLUTELY FORBIDDEN:
         - DO NOT use the "of" primitive/reporter - this will always cause errors
         - DO NOT use any non-existent or undefined variables
         - DO NOT use "ask", "with", "turtles", "patches" - these are not allowed
         - DO NOT use "set", "let", or create any variables
      
      3. ALLOWED STRUCTURE:
         - You may use "if/ifelse" statements with item checks on the "input" list
         - Basic example: ifelse item 0 input != 0 [fd 1] [rt 90 fd 2]
         
      4. FORMATTING:
         - Each command (fd/rt/lt) must be followed by a number or simple expression
         - All commands must be properly separated by spaces
         - Keep the code simple, focused only on movement

      Generate ONLY basic movement code that strictly avoids the error mentioned. The code must be runnable in NetLogo turtle context. Present your corrected NetLogo code enclosed in triple backticks:

      ```
      [Your corrected NetLogo code here]
      ```

      Do not include any explanations - the code itself should be the only output.
      """
      },


    # Chain of thought prompts for langchain providers
    "langchain": {
        "cot_system": "You are a NetLogo code evolution expert. Think step-by-step.",
        "cot_template": """{}
            
        Current code block to evolve:
        ```netlogo
        {code}
        ```

        Food distance inputs: {inputs}

        Analysis steps:
        1. Identify patterns in existing code
        2. Determine needed modifications based on food inputs
        3. Propose updated code with clear explanations
        4. Validate syntax before final answer""",
    },
    
    # Groq prompts
    "groq": {
        "prompt": """You are an expert NetLogo movement code generator. Generate movement code following these precise specifications:

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
        
        Generate ONLY the movement code with no explanations or comments. Code must be runnable in NetLogo.""",

        "prompt1": """Modify the given NetLogo movement rule according to the following guidelines:

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

        Remember, the goal is to create an efficient movement rule that balances exploration and exploitation, aiming to find food in both the short and long term.""",
        
        "prompt2": """You are an expert NetLogo coder. You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible. Improve the given agent movement code following these precise specifications:

        INPUT CONTEXT:
        - Current rule: {}


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

        Generate ONLY the movement code. Code must be runnable in NetLogo in the context of a turtle.
        Present your generated NetLogo code enclosed in triple backticks, following this format:

        ```
        [Your generated NetLogo code here]
        ```
        """,
        
        "prompt3": """You are an expert NetLogo programmer tasked with optimizing the movement code for a turtle agent in a food-collection simulation. Your goal is to enhance the given agent movement code while adhering to specific guidelines and focusing on simple, effective movement strategies.

        Here is the current rule for the turtle's movement:
        
        <current_rule>
        {}
        </current_rule>
        
        Your task is to improve this rule by focusing on the following objectives:
        
        1. Implement simple, effective movement commands.
        2. Balance exploration and food-seeking behavior.
        3. Respond intelligently to sensor readings.
        4. Combine different movement patterns efficiently.
        
        When improving the code, adhere to these constraints:
        
        1. Use only NetLogo commands related to turtle movement and sensing.
        2. Do not assume and use any variables or state names. 
        3. Utilize only existing variables; do not create new ones.
        4. Keep the code concise and focused on movement optimization.
        5. Modify the above code slightly more complex
        
        Before generating the final code, wrap your analysis in <movement_optimization_analysis> tags. Follow these steps:
        
        1. Evaluate the strengths and weaknesses of the current rule.
        2. Identify key NetLogo commands for movement and sensing that could be useful.
        3. Outline a strategy for balancing exploration and food-seeking behaviour. 
        
        Present your generated NetLogo code enclosed in triple backticks, following this format:

        ```
        [Your generated NetLogo code here]
        ```
        """
    },
    # Claude prompts
    "claude": {
        "prompt": """You are an expert NetLogo movement code generator. Generate movement code following these precise specifications:

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

Generate ONLY the movement code with no explanations or comments. Code must be runnable in NetLogo.""",
        "prompt1": """Modify the given NetLogo movement rule according to the following guidelines:

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
        
        Return ONLY the modified NetLogo code with no explanations.""",
        "prompt2": """You are an expert NetLogo agent movement behavior generator. Your task is to create sophisticated movement patterns that balance efficiency with complexity. Generate code that follows these specifications while pushing the boundaries of complexity:

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

        Return ONLY the NetLogo code with no explanations. Make it mathematically interesting and behaviorally complex while ensuring it remains valid NetLogo syntax.""",
        "prompt3": """You are an expert NetLogo coder. You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible. Improve the given agent movement code following these precise specifications:

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

Generate ONLY the movement code. Code must be runnable in NetLogo in the context of a turtle.""",
    },
}
