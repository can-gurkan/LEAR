"""Collection of prompts used throughout the LEAR system

PROMPT STRUCTURE:
- evolution_strategies: Different approaches for code evolution
  - simple: Basic incremental evolution with minimal changes
  - complex: Advanced evolution with sophisticated patterns
  - [add more strategies as needed]
- Each strategy contains:
  - pseudocode_prompt: For generating pseudocode 
  - code_prompt: For converting pseudocode to NetLogo code
- Other specialized prompt categories (langchain, groq, claude, etc.)
"""

prompts = {
    # Evolution goals used in text-based evolution
    "evolution_goals": """Evolution Goals:
    1. Optimize movement for efficient food collection
    2. Balance exploration and exploitation
    3. Maintain simple, efficient NetLogo commands
    4. Consider both immediate food sources and long-term survival""",
    
    # Evolution strategies for different approaches to code evolution
    "evolution_strategies": {
        # Simple evolution strategy with minimal changes
        "simple": {
            "pseudocode_prompt": """You are an AI assistant tasked with improving the movement code for a turtle agent in NetLogo. Your goal is to create new pseudocode with slight modifications using paradigms of genetic programming. The improved code should help the agent collect as much food as possible while adhering to specific constraints and strategic goals.

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

      Do not include any explanations outside the code block.""",
            "code_prompt": """You are tasked with converting pseudocode into well-structured NetLogo code for agent movement. Your goal is to generate only the movement code based on the provided pseudocode, adhering to specific constraints and requirements.

    Here is the pseudocode you will be working with:
    
    <pseudocode>
    {}
    </pseudocode>
    
    STRICT GUIDELINES FOR CODE GENERATION:
    
    1. UNDERSTANDING THE PSEUDOCODE:
       - Focus on understanding the FUNCTIONALITY described in the pseudocode
       - DO NOT use variable names from the pseudocode directly in your NetLogo code
       - Translate conceptual descriptions into valid NetLogo syntax
       - The pseudocode is a guideline for behavior, not a direct translation template
    
    2. VALID COMMANDS ONLY:
       - Use only these movement commands: fd, forward, rt, right, lt, left, bk, back
       - Use only these reporters: random, random-float, sin, cos, item, xcor, ycor, heading
       - All commands must be properly space-separated: "fd 1" not "fd1"
    
    3. ABSOLUTELY FORBIDDEN:
       - DO NOT use the "of" primitive/reporter - this will always cause errors
       - DO NOT use any non-existent or undefined variables
       - DO NOT use "ask", "with", "turtles", "patches" - these are not allowed
       - DO NOT use "set", "let", or create any variables
       - DO NOT include any infinite loops - avoid "while" or "loop" constructs
       - DO NOT copy variable names from pseudocode if they don't exist in NetLogo
    
    4. ALLOWED STRUCTURE:
       - You may use "if/ifelse" statements with item checks on the "input" list
       - Basic example: ifelse item 0 input > 0 [fd 1] [rt 90 fd 2]
       - For complex conditions, ensure proper bracket nesting and balance
       - Make sure every opening bracket '[' has a matching closing bracket ']'
       - Remember "input" is the only valid variable you can reference
       
    5. FORMATTING:
       - Each command (fd/rt/lt) must be followed by a number or simple expression
       - All commands must be properly separated by spaces
       - Keep the code simple, focused only on movement
       - Maximum nesting depth should be 3 levels to avoid complexity errors
    
    6. VALUE CONSTRAINTS:
       - All numeric values should be between -1000 and 1000
       - Prefer positive values when possible
       - For random functions, use reasonable ranges (e.g., random 360 for turning)
       - Avoid complex mathematical expressions - keep calculations simple
    
    7. ERROR PREVENTION:
       - Ensure each condition has both true and false branches in ifelse statements
       - Verify that each command has a valid parameter
       - Check that no undefined variables or functions are referenced
       - Make sure bracket pairs are properly matched
       - Include at least one movement command (fd, bk, rt, lt)
    
    8. ROBUST IMPLEMENTATION:
       - Generate code that is resilient to edge cases
       - If pseudocode mentions a variable that doesn't exist in NetLogo, translate its purpose 
         without using the variable name (e.g., if pseudocode uses "angle", implement the 
         calculation directly without referencing "angle")
       - Focus on capturing the intent and behavior, not the exact syntax
    
    Your task is to carefully analyze the provided pseudocode and translate it into NetLogo code that represents the agent's movement strategy. Focus solely on the movement aspects described in the pseudocode.
    
    Present your generated NetLogo code enclosed in triple backticks, following this format:
    
    ```
    [Your generated NetLogo code here]
    ```
    
    Ensure that your code accurately reflects the movement strategy described in the pseudocode while adhering to NetLogo syntax and the specified constraints. Do not add any explanations or comments outside the code block."""
        },
        
        # Complex evolution strategy with sophisticated patterns
        "complex": {
            "pseudocode_prompt": """You are an expert NetLogo pseudocode creator specializing in complex turtle agent movement. Your task is to evolve the existing pseudocode into a more sophisticated version, balancing simplicity with advanced behavior patterns.

    CURRENT PSEUDOCODE TO EVOLVE:
    ```
    {}
    ```

    EVOLUTIONARY ADVANCEMENT OBJECTIVES:

    1. PROGRESSIVE COMPLEXITY ENHANCEMENT:
       - Build upon the existing pseudocode's core logic
       - Add 1-2 advanced movement concepts or conditional behaviors
       - Incorporate more sophisticated decision-making based on food sensor inputs
       - Explore mathematical relationships (trigonometric, probabilistic) for movement

    2. INNOVATION GUIDELINES:
       - Introduce adaptive movement that responds to changing environments
       - Create multi-stage movement sequences that balance local and global exploration
       - Develop intelligent turning behaviors that optimize path trajectories
       - Implement energy-efficient movement strategies that minimize unnecessary actions
       - Consider emergent swarm-like behaviors when multiple agents use this rule

    3. VALID MOVEMENT CONCEPTS ONLY:
       - "Move forward" (will become fd or forward in NetLogo)
       - "Turn right" (will become rt or right in NetLogo)
       - "Turn left" (will become lt or left in NetLogo)
       - "Move backward" (will become bk or back in NetLogo)
       - Randomness (will use random or random-float in NetLogo)
       - Trigonometric concepts (sin, cos)
       - Conditional movements based on food sensor readings (the "input" list)

    4. ABSOLUTELY FORBIDDEN CONCEPTS:
       - DO NOT include any reference to "of" relationships between agents
       - DO NOT create or reference any variables that don't exist
       - DO NOT include asking other agents to perform actions
       - DO NOT include creating or killing agents
       - DO NOT include setting or changing environment variables
       - DO NOT use loops or recursive patterns

    5. ALLOWED STRUCTURE:
       - You may include "if/else" logic based on the "input" list values
       - Example: "If there is food to the left, turn left and move forward, otherwise turn right at a random angle between 30-60 degrees and move forward"
       - You may combine multiple movement commands in sequence
       - You may use mathematical concepts like sine and cosine for turning angles

    6. SOPHISTICATED PATTERN EXAMPLES:
       - Adaptive Exploration: "Move forward a small random distance (0-2), then turn right by an angle based on sine of a random value (0-90), then move forward again"
       - Sensor-Responsive: "If food is detected on the left, turn left by an angle proportional to the food's distance and move forward; otherwise turn right randomly and move forward further"
       - Trigonometric Navigation: "Move forward, then turn right by an angle calculated using sine of a random value multiplied by 45, then move forward a variable distance"
       - Multi-Stage Movement: "Move forward a short distance, turn right by an angle based on cosine of a random value, move forward again, then turn left by a small angle"

    7. FORMATTING:
       - Keep the pseudocode readable and focused on movement logic
       - Use plain English descriptions of movement patterns
       - Be specific about how food sensor readings influence movement
       - Be clear about mathematical relationships while keeping them implementable

    Present your evolved pseudocode enclosed in triple backticks:

    ```
    [Your evolved pseudocode here]
    ```

    Do not include any explanations outside the code block.""",       
            "code_prompt": """You are an expert NetLogo programmer tasked with translating sophisticated movement pseudocode into valid, executable NetLogo code. Your goal is to faithfully implement the pseudocode while ensuring the code adheres to NetLogo syntax and execution constraints.

    PSEUDOCODE TO TRANSLATE:
    ```
    {}
    ```

    TRANSLATION REQUIREMENTS:

    1. UNDERSTANDING THE PSEUDOCODE:
       - Focus on understanding the FUNCTIONALITY described in the pseudocode
       - DO NOT use variable names from the pseudocode directly in your NetLogo code
       - Translate conceptual descriptions into valid NetLogo syntax
       - The pseudocode is a guideline for behavior, not a direct translation template

    2. VALID COMMANDS AND SYNTAX:
       - Movement: fd/forward, rt/right, lt/left, bk/back
       - Reporters: random, random-float, sin, cos, item, xcor, ycor, heading
       - Format: [command] [number | expression] with proper spacing
       - All commands must be properly space-separated: "fd 1" not "fd1"

    3. COMPLEXITY IMPLEMENTATION:
       - Accurately implement all described movement patterns
       - Convert trigonometric concepts to NetLogo sin/cos functions
       - Translate conditional logic to ifelse statements with proper brackets
       - Implement sensor-responsive behavior using the "input" list only
       - Convert multi-stage movements into appropriate command sequences

    4. ABSOLUTELY FORBIDDEN:
       - DO NOT use the "of" primitive/reporter - this will cause errors
       - DO NOT use any non-existent or undefined variables
       - DO NOT use "ask", "with", "turtles", "patches" - these are not allowed
       - DO NOT use "set", "let", or create any variables
       - DO NOT include any infinite loops - avoid "while" or "loop" constructs
       - DO NOT copy variable names from pseudocode if they don't exist in NetLogo

    5. ALLOWED STRUCTURE:
       - You may use "if/ifelse" statements with item checks on the "input" list
       - Example: ifelse item 0 input > 0 [lt (45 - item 0 input / 2) fd 1] [rt random 45 fd 2]
       - For complex or nested conditions, ensure proper bracket nesting and balance
       - Make sure every opening bracket '[' has a matching closing bracket ']'
       - Maximum nesting depth should be 3 levels to avoid complexity errors
       - Remember "input" is the only valid variable you can reference

    6. ADVANCED PATTERN IMPLEMENTATION:
       - For random movement: Use random or random-float with appropriate ranges
       - For trigonometric functions: Use sin/cos with appropriate arguments
       - For sensor-responsive behavior: Use ifelse with item 0, 1, or 2 of the input list
       - For multi-stage movements: Implement as a sequence of commands
       - For complex expressions: Use parentheses to ensure correct order of operations

    7. ERROR PREVENTION:
       - Ensure each condition has both true and false branches in ifelse statements
       - Verify that each command has a valid parameter
       - Enclose complex expressions in parentheses for clarity: sin (random 90)
       - Make sure bracket pairs are properly matched and nested
       - Include at least one movement command (fd, bk, rt, lt)
       - Keep all numeric values between -1000 and 1000

    8. ROBUST IMPLEMENTATION:
       - Generate code that is resilient to edge cases
       - If pseudocode mentions a variable that doesn't exist in NetLogo, translate its purpose 
         without using the variable name (e.g., if pseudocode uses "angle", implement the 
         calculation directly without referencing "angle")
       - Focus on capturing the intent and behavior, not the exact syntax

    Your task is to carefully analyze the provided pseudocode and translate it into well-formed NetLogo code that represents the described movement strategy. Focus on creating executable code that accurately implements the sophisticated patterns described in the pseudocode.

    Present your generated NetLogo code enclosed in triple backticks:

    ```
    [Your generated NetLogo code here]
    ```

    Ensure that your code accurately reflects the movement strategy described in the pseudocode while adhering to NetLogo syntax and the specified constraints. Do not add any explanations or comments outside the code block."""
        },

        # Add more evolution strategies as needed...
    },

    # Code generation prompt for advanced agent movement rules
    "complex_prompts": {
       "prompt1": """You are an expert NetLogo movement code evolution specialist. Your task is to advance the agent's movement rules by enhancing the existing rule with more sophisticated behavior patterns while maintaining NetLogo compatibility.

      CURRENT RULE TO EVOLVE:
      ```
      {}
      ```

      EVOLUTIONARY ADVANCEMENT OBJECTIVES:

      1. PROGRESSIVE COMPLEXITY ENHANCEMENT:
         - Build upon the existing rule's core structure
         - Add 1-2 advanced movement patterns or conditional behaviors
         - Incorporate more sophisticated decision-making based on food sensor inputs
         - Explore mathematical relationships (trigonometric, probabilistic) for movement

      2. INNOVATION GUIDELINES:
         - Introduce adaptive movement that responds to changing environments
         - Create multi-stage movement sequences that balance local and global exploration
         - Develop intelligent turning behaviors that optimize path trajectories
         - Implement energy-efficient movement strategies that minimize unnecessary actions
         - Consider emergent swarm-like behaviors when multiple agents use this rule

      3. VALID COMMANDS AND SYNTAX:
         - Movement: fd/forward, rt/right, lt/left, bk/back
         - Reporters: random, random-float, sin, cos, item, xcor, ycor, heading
         - Structure: Simple conditionals using ifelse with input list values
         - Format: [command] [number | expression] with proper spacing

      4. TECHNICAL GUARDRAILS:
         - DO NOT use "of" primitives (will cause errors)
         - DO NOT create variables with "set" or "let"
         - DO NOT use "ask", "with", "turtles", or "patches"
         - DO NOT use undefined variables or commands
         - DO NOT implement loops or recursive patterns
         - DO NOT exceed 3 levels of nested conditionals

      5. SOPHISTICATED PATTERN EXAMPLES:
         - Adaptive Exploration: fd random-float 2 rt sin (random 90) fd 1
         - Sensor-Responsive: ifelse item 0 input > 0 [lt (45 - item 0 input / 2) fd 1] [rt random 45 fd 2]
         - Trigonometric Navigation: fd 1 rt (sin (random 90) * 45) fd random-float 3
         - Multi-Stage Movement: fd 1 rt cos (random 60) * 30 fd 2 lt sin (random 45) * 20

      6. EVALUATION CRITERIA:
         - Balance between exploration and exploitation
         - Efficiency in food collection capability
         - Robustness against getting stuck in local optima
         - Mathematical elegance and behavioral complexity
         - NetLogo syntax compliance and error prevention

      7. EVOLUTIONARY APPROACH:
         - Analyze the strengths and limitations of the current rule
         - Identify specific areas for enhancement (decision-making, efficiency, adaptability)
         - Implement targeted improvements while preserving working components
         - Ensure the evolved rule represents a clear advancement from its predecessor

      Return ONLY the evolved NetLogo code without explanation, enclosed in triple backticks:

      ```
      [Your evolved NetLogo code here]
      ```
      """},

    "retry_prompts": {
      "generate_code_with_error": """You are an expert NetLogo coder tasked with fixing a movement code error for a turtle agent. Your goal is to update the provided NetLogo movement code to fix the error message shown below.

      Here is the current rule:
      {}

      Here is the error message:
      {}
      
      STRICT GUIDELINES FOR FIXING THE CODE:
      
      1. VALID COMMANDS ONLY:
         - Use only these movement commands: fd, forward, rt, right, lt, left, bk, back
         - Use only these reporters: random, random-float, sin, cos, item, xcor, ycor, heading
      
      2. ABSOLUTELY FORBIDDEN:
         - DO NOT use the "of" primitive/reporter - this will always cause errors
         - DO NOT use any non-existent or undefined variables
         - DO NOT use "ask", "with", "turtles", "patches" - these are not allowed
         - DO NOT use "set", "let", or create any variables
         - DO NOT use loops or recursion - these create infinite loops
      
      3. ALLOWED STRUCTURE:
         - You may use "if/ifelse" statements with item checks on the "input" list
         - Basic example: ifelse item 0 input != 0 [fd 1] [rt 90 fd 2]
         - For complex or nested conditions, maintain proper bracket balance
         
      4. FORMATTING:
         - Each command (fd/rt/lt) must be followed by a number or simple expression
         - All commands must be properly separated by spaces
         - Keep the code simple, focused only on movement
         - Ensure all brackets are properly paired and balanced

      5. ERROR-SPECIFIC FIXES:
         - For "Dangerous primitives" errors: Remove ALL prohibited commands
         - For "Unclosed brackets" errors: Check and fix ALL bracket pairs
         - For "Invalid value" errors: Ensure all numeric values are valid and positive
         - For "No movement commands" errors: Include at least one movement command (fd, rt, lt)
         - For "Command needs a value" errors: Ensure every command has a parameter

      Generate ONLY basic movement code that strictly avoids the error mentioned. The code must be runnable in NetLogo turtle context. Present your corrected NetLogo code enclosed in triple backticks:

      ```
      [Your corrected NetLogo code here]
      ```

      Do not include any explanations - the code itself should be the only output.
      """,
      
      "generate_code_with_pseudocode_and_error": """You are an expert NetLogo coder tasked with fixing a movement code error for a turtle agent. Your goal is to update the NetLogo movement code to fix the error message while following the provided pseudocode.

      Here is the current rule:
      {}

      Here is the error message:
      {}
      
      Here is the pseudocode to follow:
      {}
      
      STRICT GUIDELINES FOR FIXING THE CODE:
      
      1. FOLLOW THE PSEUDOCODE:
         - Use the pseudocode as a guide for the movement logic
         - Implement the logic described in the pseudocode while fixing the error
         - Ensure the fixed code aligns with the pseudocode's intent and strategy
      
      2. VALID COMMANDS ONLY:
         - Use only these movement commands: fd, forward, rt, right, lt, left, bk, back
         - Use only these reporters: random, random-float, sin, cos, item, xcor, ycor, heading
      
      3. ABSOLUTELY FORBIDDEN:
         - DO NOT use the "of" primitive/reporter - this will always cause errors
         - DO NOT use any non-existent or undefined variables
         - DO NOT use "ask", "with", "turtles", "patches" - these are not allowed
         - DO NOT use "set", "let", or create any variables
         - DO NOT use loops or recursion - these create infinite loops
      
      4. ALLOWED STRUCTURE:
         - You may use "if/ifelse" statements with item checks on the "input" list
         - Basic example: ifelse item 0 input != 0 [fd 1] [rt 90 fd 2]
         - For complex or nested conditions, maintain proper bracket balance
         
      5. FORMATTING:
         - Each command (fd/rt/lt) must be followed by a number or simple expression
         - All commands must be properly separated by spaces
         - Keep the code simple, focused only on movement
         - Ensure all brackets are properly paired and balanced

      6. ERROR-SPECIFIC FIXES:
         - For "Dangerous primitives" errors: Remove ALL prohibited commands
         - For "Unclosed brackets" errors: Check and fix ALL bracket pairs
         - For "Invalid value" errors: Ensure all numeric values are valid and positive
         - For "No movement commands" errors: Include at least one movement command (fd, rt, lt)
         - For "Command needs a value" errors: Ensure every command has a parameter

      Generate NetLogo code that follows the pseudocode while fixing the error. The code must be runnable in NetLogo turtle context. Present your corrected NetLogo code enclosed in triple backticks:

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
        "prompt2": """You are an expert NetLogo coder tasked with refining a turtle agent's movement code through small, incremental improvements. Your objective is to evolve the existing rule slightly rather than redesigning it entirely.

      **Current Rule to Evolve:**
      {}
      
      **Evolution Guidelines:**
      
      1. **Preserve the Core Structure:**
         - Retain most of the original code.
         - Implement only 1-2 minor, strategic changes.
         - Emulate genetic evolution: small mutations, not complete rewrites.
      
      2. **Potential Improvement Areas:**
         - Introduce slight randomness to fixed values.
         - Modify movement parameters slightly (distances or angles).
         - Incorporate or enhance simple conditionals based on the "input" list.
         - Optimize existing logic minimally.
      
      3. **Valid Commands and Reporters:**
         - Movement: `fd`, `forward`, `rt`, `right`, `lt`, `left`, `bk`, `back`
         - Reporters: `random`, `random-float`, `sin`, `cos`, `item`, `xcor`, `ycor`, `heading`
      
      4. **Absolutely Forbidden:**
         - Do not use the `of` primitive/reporter (will cause errors).
         - Do not use `ask`, `with`, `turtles`, `patches`.
         - Do not create variables with `set` or `let`.
         - Do not use any undefined variables.
         - Do not introduce infinite loops or recursion.
      
      5. **Error Prevention:**
         - Ensure balanced brackets `[ ]`.
         - Verify that `ifelse` statements have both true and false branches.
         - Confirm that all commands have parameters.
         - Keep numerical values between -1000 and 1000.
      
      **Evolutionary Approach:**
      
      Consider this as a genetic algorithm where the current rule is the parent, and your task is to create a slightly mutated offspring with potentially better fitness. The mutation should be recognizable as being derived from the parent, not a completely different solution.
      
      Present your evolved NetLogo code enclosed in triple backticks:
      
      ```
      [Your evolved NetLogo code here]
      ```
        """,     
        "prompt3": """You are an expert NetLogo programmer tasked with evolving the movement code for a turtle agent in a food-collection simulation. Your goal is to enhance and improve the previous agent rule through small, incremental modifications rather than complete rewrites.

        Here is the current rule for the turtle's movement:
        {}
        
        ENHANCEMENT GUIDELINES:
        
        1. MAKE SMALL, TARGETED IMPROVEMENTS:
           - Preserve most of the original code structure
           - Add or modify only 1-2 elements at a time
           - Maintain the core movement pattern of the original rule
        
        2. FOCUS AREAS FOR IMPROVEMENT:
           - Add slight randomness to fixed movements
           - Enhance turning angles or movement distances
           - Improve responsiveness to the "input" list (food sensor readings)
           - Subtly adjust movement parameters for better performance
        
        3. VALID COMMANDS AND SYNTAX:
           - Use only these movement commands: fd, forward, rt, right, lt, left, bk, back
           - Use only these reporters: random, random-float, sin, cos, item, xcor, ycor, heading
           - Format: [command] [positive_number | reporter_expression]
        
        4. ABSOLUTELY FORBIDDEN:
           - DO NOT use "of" primitives - will cause errors
           - DO NOT modify the overall structure drastically
           - DO NOT create new variables with "set" or "let"
           - DO NOT use "ask", "with", "turtles", or "patches"
           - DO NOT use any undefined variables
           - DO NOT use while loops or recursive constructs
        
        5. ERROR PREVENTION:
           - Ensure all bracket pairs match
           - Make sure every movement command has a parameter
           - Keep values within reasonable ranges (-1000 to 1000)
           - Ensure at least one movement command is included
           - Validate that all conditions have both true/false branches
        
        STRATEGY:
        Think of this as an evolutionary process where each generation makes small beneficial mutations rather than complete redesigns. Introduce slight variations that might improve performance while respecting the existing structure and logic of the rule.
        
        Present your evolved NetLogo code enclosed in triple backticks:

        ```
        [Your evolved NetLogo code here]
        ```
        """,
        "prompt4": """You are an expert NetLogo coder. You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible. Improve the given agent movement code following these precise specifications:

INPUT CONTEXT:
- Current rule: {}
- Food sensor readings: 
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
        "prompt3": """You are an expert NetLogo evolution specialist tasked with carefully evolving turtle agent movement code. Your goal is to make SMALL, INCREMENTAL improvements to the existing rule while preserving its core structure and behavior.

CURRENT RULE TO EVOLVE:
```
{}
```

EVOLUTION APPROACH:

1. GENETIC PROGRAMMING MINDSET:
   - Make 1-2 small, targeted "mutations" to the code
   - Preserve 80-90% of the original structure
   - Think of this as creating a slightly modified offspring
   - DO NOT completely rewrite or redesign the rule

2. POTENTIAL MUTATION TYPES:
   - Slightly adjust numeric parameters (angles, distances)
   - Add small amounts of randomness to fixed values
   - Enhance existing conditional logic
   - Add minor responsiveness to input list (food sensors)
   - Optimize movement efficiency with minimal changes

3. TECHNICAL REQUIREMENTS:
   - Use only: fd, rt, lt, bk (movement) and random, random-float, sin, cos, item, xcor, ycor, heading (reporters)
   - Keep all values within reasonable bounds (-1000 to 1000)
   - Do not use any "set" or "let" statements
   - Do not use "ask", "with", "turtles", "patches" primitives
   - Ensure all brackets are properly paired
   - Every command must have a valid parameter

4. ERROR PREVENTION:
   - Verify that ifelse statements have both true/false branches
   - Check that no undefined variables or primitives are used
   - Ensure at least one movement command is included
   - Add spacing between commands and values
   - Verify syntax after making changes

Think of yourself as performing careful genetic modifications rather than creating a new design from scratch. The evolved code should be clearly recognizable as a descendant of the original rule, with small improvements that might enhance its performance.

Return ONLY the evolved NetLogo code with no explanations:

```
[Your evolved NetLogo code here]
```
""",
    },
"collection_simple": {
      "zero_shot_code": """You are an expert NetLogo coder. 
      You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible. 
      Improve the given agent movement code following these precise specifications:

      Here is the current code of the turtle agent:

      ```
        {}
      ```

      INPUT CONTEXT:
      - You have access to a variable called input
      - Input is a NetLogo list that contains three values representing distances to food in three cone regions of 20 degrees each
      - The first item in the input list is the distance to the nearest food in the left cone, the second is the right cone, and the third is the front cone
      - Each value encodes the distance to nearest food source where a value of 0 indicates no food
      - Non-zero lower values indicate closer food
      - Use the information in this variable to inform movement strategy
      - Remember that you only have access to the variable named input and no other variables

      SIMULATION ENVIRONMENT:
      - The turtle agent is in a food collection simulation
      - The goal is to collect as much food as possible
      - The turtle agent can detect food in three cone regions encoded in the input list
      - The food sources are randomly distributed in the environment

      CONSTRAINTS:
      1. Do not include code to kill or control any other agents
      2. Do not include code to interact with the environment
      3. Do not include code to change the environment
      4. Do not include code to create new agents
      5. Do not include code to create new food sources
      6. Do not include code to change the rules of the simulation
      7. Follow NetLogo syntax and constraints
      8. Do not use any undefined variables or commands besides the input variable
      9. Focus on movement strategies based on the input variable

      VALID COMMANDS AND SYNTAX:
         - Use only these movement commands: fd, forward, rt, right, lt, left, bk, back
         - Use only these reporters: random, random-float, sin, cos, item, xcor, ycor, heading
         - The syntax of the if primitive is as follows: if boolean [ commands ]
         - The syntax of the ifelse primitive is as follows: ifelse boolean [ commands1 ] [ commands2 ]
         - An ifelse block  that contains multiple boolean conditions must be enclosed in parentheses as follows: 
         (ifelse boolean1 [ commands1 ] boolean2 [ commands2 ] ... [ elsecommands ])
        
      ABSOLUTELY FORBIDDEN:
         - DO NOT use "of" primitives - will cause errors
         - DO NOT use "ask", "with", "turtles", or "patches"
         - DO NOT use any undefined variables
         - DO NOT use while loops or recursive constructs
        
      ERROR PREVENTION:
         - Ensure all bracket pairs match
         - Make sure every movement command has a parameter
         - Keep values within reasonable ranges (-1000 to 1000)
         - Ensure at least one movement command is included
         - There is no such thing as an `else` statement in NetLogo

      STRATEGIC GOALS:
      1. Balance exploration and food-seeking behavior
      2. Respond to sensor readings intelligently
      3. Combine different movement patterns
      4. Be creative in your movement strategy

      The code must be runnable in NetLogo in the context of a turtle. Do not write any procedures and assume that the code will be run in an ask turtles block.
      Return ONLY the changed NetLogo code. Do not include any explanations or outside the code block.

      ```
      [Your changed NetLogo code goes here]
      ```
      """,
      "one_shot_code": """You are an expert NetLogo coder. 
      You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible. 
      Improve the given agent movement code following these precise specifications:

      Here is the current code of the turtle agent:

      ```
        {}
      ```

      INPUT CONTEXT:
      - You have access to a variable called input
      - Input is a NetLogo list that contains three values representing distances to food in three cone regions of 20 degrees each
      - The first item in the input list is the distance to the nearest food in the left cone, the second is the right cone, and the third is the front cone
      - Each value encodes the distance to nearest food source where a value of 0 indicates no food
      - Non-zero lower values indicate closer food
      - Use the information in this variable to inform movement strategy
      - Remember that you only have access to the variable named input and no other variables

      SIMULATION ENVIRONMENT:
      - The turtle agent is in a food collection simulation
      - The goal is to collect as much food as possible
      - The turtle agent can detect food in three cone regions encoded in the input list
      - The food sources are randomly distributed in the environment

      CONSTRAINTS:
      1. Do not include code to kill or control any other agents
      2. Do not include code to interact with the environment
      3. Do not include code to change the environment
      4. Do not include code to create new agents
      5. Do not include code to create new food sources
      6. Do not include code to change the rules of the simulation
      7. Follow NetLogo syntax and constraints
      8. Do not use any undefined variables or commands besides the input variable
      9. Focus on movement strategies based on the input variable

      VALID COMMANDS AND SYNTAX:
         - Use only these movement commands: fd, forward, rt, right, lt, left, bk, back
         - Use only these reporters: random, random-float, sin, cos, item, xcor, ycor, heading
         - The syntax of the if primitive is as follows: if boolean [ commands ]
         - The syntax of the ifelse primitive is as follows: ifelse boolean [ commands1 ] [ commands2 ]
         - An ifelse block  that contains multiple boolean conditions must be enclosed in parentheses as follows: 
         (ifelse boolean1 [ commands1 ] boolean2 [ commands2 ] ... [ elsecommands ])
        
      ABSOLUTELY FORBIDDEN:
         - DO NOT use "of" primitives - will cause errors
         - DO NOT use "ask", "with", "turtles", or "patches"
         - DO NOT use any undefined variables
         - DO NOT use while loops or recursive constructs
        
      ERROR PREVENTION:
         - Ensure all bracket pairs match
         - Make sure every movement command has a parameter
         - Keep values within reasonable ranges (-1000 to 1000)
         - Ensure at least one movement command is included
         - There is no such thing as an `else` statement in NetLogo

      STRATEGIC GOALS:
      1. Balance exploration and food-seeking behavior
      2. Respond to sensor readings intelligently
      3. Combine different movement patterns
      4. Be creative in your movement strategy

      EXAMPLES OF VALID CODE GENERATION:
      Current Code: ```fd 1 rt random 45 fd 2 lt 30```
      Changed Code: ```ifelse item 0 input != 0 [rt 15 fd 0.5] [rt random 30 lt random 30 fd 5]```
      Why: This code uses the information in the input list to turn right and go forward a little to reach food if the first element of input list contains a non-zero value, else moves forward in big steps and turns randomly to explore

      The code must be runnable in NetLogo in the context of a turtle. Do not write any procedures and assume that the code will be run in an ask turtles block.
      Return ONLY the changed NetLogo code. Do not include any explanations or outside the code block.

      ```
      [Your changed NetLogo code goes here]
      ```
      """,
      "two_shot_code": """You are an expert NetLogo coder. 
      You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible. 
      Improve the given agent movement code following these precise specifications:

      Here is the current code of the turtle agent:

      ```
        {}
      ```

      INPUT CONTEXT:
      - You have access to a variable called input
      - Input is a NetLogo list that contains three values representing distances to food in three cone regions of 20 degrees each
      - The first item in the input list is the distance to the nearest food in the left cone, the second is the right cone, and the third is the front cone
      - Each value encodes the distance to nearest food source where a value of 0 indicates no food
      - Non-zero lower values indicate closer food
      - Use the information in this variable to inform movement strategy
      - Remember that you only have access to the variable named input and no other variables

      SIMULATION ENVIRONMENT:
      - The turtle agent is in a food collection simulation
      - The goal is to collect as much food as possible
      - The turtle agent can detect food in three cone regions encoded in the input list
      - The food sources are randomly distributed in the environment

      CONSTRAINTS:
      1. Do not include code to kill or control any other agents
      2. Do not include code to interact with the environment
      3. Do not include code to change the environment
      4. Do not include code to create new agents
      5. Do not include code to create new food sources
      6. Do not include code to change the rules of the simulation
      7. Follow NetLogo syntax and constraints
      8. Do not use any undefined variables or commands besides the input variable
      9. Focus on movement strategies based on the input variable

      VALID COMMANDS AND SYNTAX:
         - Use only these movement commands: fd, forward, rt, right, lt, left, bk, back
         - Use only these reporters: random, random-float, sin, cos, item, xcor, ycor, heading
         - The syntax of the if primitive is as follows: if boolean [ commands ]
         - The syntax of the ifelse primitive is as follows: ifelse boolean [ commands1 ] [ commands2 ]
         - An ifelse block  that contains multiple boolean conditions must be enclosed in parentheses as follows: 
         (ifelse boolean1 [ commands1 ] boolean2 [ commands2 ] ... [ elsecommands ])
        
      ABSOLUTELY FORBIDDEN:
         - DO NOT use "of" primitives - will cause errors
         - DO NOT use "ask", "with", "turtles", or "patches"
         - DO NOT use any undefined variables
         - DO NOT use while loops or recursive constructs
        
      ERROR PREVENTION:
         - Ensure all bracket pairs match
         - Make sure every movement command has a parameter
         - Keep values within reasonable ranges (-1000 to 1000)
         - Ensure at least one movement command is included
         - There is no such thing as an `else` statement in NetLogo

      STRATEGIC GOALS:
      1. Balance exploration and food-seeking behavior
      2. Respond to sensor readings intelligently
      3. Combine different movement patterns
      4. Be creative in your movement strategy

      EXAMPLES OF VALID CODE GENERATION:
      Current Code: ```fd 1 rt random 45 fd 2 lt 30```
      Changed Code: ```ifelse item 0 input != 0 [rt 15 fd 0.5] [rt random 30 lt random 30 fd 5]```
      Why: This code uses the information in the input list to turn right and go forward a little to reach food if the first element of input list contains a non-zero value, else moves forward in big steps and turns randomly to explore

      Current Code: 
      ```
      ifelse item 0 input != 0 [
         lt 5
         fd 0.2
         ] [
         ifelse item 1 input != 0 [
            rt 5
            fd 0.2
         ] [
            ifelse item 2 input != 0 [
               fd 0.2
            ] [
               ifelse random 100 < 50 [
               fd 2
               rt random-float 45
               ] [
               rt random-float 30
               fd 5
               ]
            ]
         ]
      ]      
      ```
      Changed Code: 
      ```
      ifelse item 0 input < item 1 input [
         ifelse item 0 input != 0 [
            lt 15 fd 0.5
         ] [
            ifelse item 1 input != 0 [
               rt 15 fd 0.5
            ] [
               ifelse item 2 input > 0 [
                  fd 1
               ] [
               rt random 30 lt random 30 fd 5
               ]
            ]
         ]
         ] [ 
         ifelse item 1 input != 0 [
            ifelse item 1 input < item 0 input [
               rt 15 fd 0.5
            ] [
               ifelse item 2 input > 0 [
               lt 15 fd 0.5
               ] [ fd 1 ]
            ]
         ] [
            ifelse item 2 input > 0 [
               lt 15 fd 1
            ] [
               rt random 30 lt random 30 fd 5
            ]
         ]
      ]
      ```
      Why: This code uses the information in the input list to make decisions based on the distances to food in different directions

      The code must be runnable in NetLogo in the context of a turtle. Do not write any procedures and assume that the code will be run in an ask turtles block.
      Return ONLY the changed NetLogo code. Do not include any explanations or outside the code block.

      ```
      [Your changed NetLogo code goes here]
      ```
      """,
    }
}
