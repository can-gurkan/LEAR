from typing import Union
import logging
from config import load_config
from verify_netlogo_code import NetLogoVerifier
from groq_generator import GroqCodeGenerator
from claude_generator import ClaudeCodeGenerator

LOG_FILE = "../../Logs/netlogo_evolution.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


config = load_config()
verifier = NetLogoVerifier()


def get_code_generator(model_type: str = "groq") -> Union[GroqCodeGenerator, ClaudeCodeGenerator]:
    if model_type.lower() == "groq":
        return GroqCodeGenerator(config['GROQ_API_KEY'], verifier)
    elif model_type.lower() == "claude":
        return ClaudeCodeGenerator(config["ANTHROPIC_API_KEY"], verifier)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
def mutate_code(agent_info: list, model_type: str = "groq") -> str:
    try:
        generator = get_code_generator(model_type)
        return generator.generate_code(agent_info)
    except Exception as e:
        logging.error(f"Error in mutate_code: {str(e)}")
        # print(f"Error in mutate_code: {str(e)}")
        return 

# def mutate_code(agent_info):
#     """Perform rule mutation proided current rule and environment obseration."""
    
#     try:
#         # print(agent_info)
#         client = instructor.from_groq(Groq(api_key=GROQ_API_KEY), 
#                                       mode=instructor.Mode.JSON)

#         prompt = get_prompt(agent_info=agent_info)

#         new_code = client.chat.completions.create(
#             model="llama-3.3-70b-versatile", # "llama-3.1-70b-versatile", 
#             response_model=NLogoCode,
#             messages=[
#                 {"role": "system", 
#                  "content": """You are an expert in evolving NetLogo agent behaviors.
#                 Focus on creating efficient, survival-optimized netlogo code."""},
#                 {
#                 "role": "user",
#                 "content": prompt
#                 }
#             ],
#             temperature=0.65,
#         )

#         # print(f"New Code : {new_code.new_code}")
    
#         # Check safety
#         is_safe = verifier.is_safe(new_code.new_code)
        
#         if is_safe:
#             return new_code.new_code
#         else:
#             print(f'Unsafe code generated. Returning initial command')
#             return agent_info[0]
        
#     except Exception as e:
#         print(f"Encountered Error: {e}")
#         return agent_info[0]
    
# def get_prompt(agent_info):
#     """Construct and return prompt provided current rule and environment observations"""
#     rule = agent_info[0]
#     food_input = agent_info[1]
    
    # prompt = f"""Modify the given NetLogo movement rule according to the following guidelines:

    #     1. Use only existing variables and data types; do not define new variables.
    #     2. Use only fd, rt, and lt for movement; exclude other NetLogo commands.
    #     3. Consider the distances to the nearest food in the three cone regions given in the observation list. If a distance is 0, no food is present in that region.
    #     4. The modified code should only contain movement commands.
    #     5. Provide a concise (less than 100 characters) NetLogo code with no comments or explanations.

    #     Example: Given rule: lt random 20 fd 1 Food input: [5, 2, 0] Updated rule: rt 20 fd 2

    #     INNOVATION GUIDELINES:

    #     - Do not reuse example codes
    #     - Develop unique movement patterns
    #     - Think about efficient food-finding strategies
    #     - Consider trade-offs between exploration and exploitation
    #     - Design for both immediate and long-term survival

    #     rule: {rule} 
    #     input: {food_input}

    #     Remember, the goal is to create an efficient movement rule that balances exploration and exploitation, aiming to find food in both the short and long term."""

#     prompt = f"""Modify the given NetLogo movement rule according to the following guidelines:

#          1. Use only fd, rt, or lt commands with numbers or 'random N'
#          2. Keep expressions simple - avoid complex arithmetic
#          3. Use positive numbers only
#          4. Format: Each command (fd/rt/lt) must be followed by either:
#             - A single number (e.g., "fd 1")
#             - random N (e.g., "rt random 30")
#             - random-float N (e.g., "lt random-float 45")
            
#          CURRENT STATE:
#          - Current rule: {rule}
#          - Food distances: {food_input}
       
#          EXAMPLES OF VALID CODE:
#          - fd 1 rt random 30
#          - lt 45 fd 2
#          - rt random-float 90 fd 1
       
#          Return ONLY the modified NetLogo code with no explanations."""
    
#     return prompt

# if __name__ == "__main__":
    # config = load_config()
    # GROQ_API_KEY = config['GROQ_API_KEY']
#     if not GROQ_API_KEY:
#         raise ValueError("GROQ_API_KEY environment variable not set")
    
#     verifier = NetLogoVerifier()
#     mutator = NetLogoMutator(GROQ_API_KEY, verifier)