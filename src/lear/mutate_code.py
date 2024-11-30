import instructor
import os
from random import randrange
from pydantic import BaseModel
from groq import Groq

from verify_netlogo_code import NetLogoVerifier

api_key = "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"

verifier = NetLogoVerifier()


class NLogoCode(BaseModel):
    new_code: str

def mutate_code(agent_info):
    """Perform rule mutation proided current rule and environment obseration."""
    
    try:
        # print(agent_info)
        client = instructor.from_groq(Groq(api_key=api_key), mode=instructor.Mode.JSON)

        prompt = get_prompt(agent_info=agent_info)

        new_code = client.chat.completions.create(
            model="mixtral-8x7b-32768",#"llama-3.1-70b-versatile",
            response_model=NLogoCode,
            messages=[
                {"role": "system", 
                 "content": """You are an expert in evolving NetLogo agent behaviors.
                Focus on creating efficient, survival-optimized netlogo code."""},
                {
                "role": "user",
                "content": prompt
                }
            ],
            temperature=0.65,
        )

        # print(f"New Code : {new_code.new_code}")
    
        # Check safety
        is_safe = verifier.is_safe(new_code.new_code)

        if is_safe:
            return new_code.new_code
        else:
            return agent_info[0]
        
    except:
        return agent_info[0]
    
def get_prompt(agent_info):
    """Construct and return prompt provided current rule and environment observations"""
    rule = agent_info[0]
    food_input = agent_info[1]
    
    prompt = f"""Modify the given NetLogo movement rule according to the following guidelines:

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

        Input:
        rule: {rule} 
        food-input: {food_input}

        Remember, the goal is to create an efficient movement rule that balances exploration and exploitation, aiming to find food in both the short and long term."""

    
    return prompt

# if __name__ == "__main__":
#     verifier = NetLogoVerifier()
#     code = "lt random 20 fd 1"
#     print(f"original: {code}")
    
#     agent_info = [code, [randrange(0, 7), randrange(0, 7), randrange(0, 7)]]
    
#     for i in range(10):
#         code = mutate_code(agent_info)
#         print(f"V{i+1}: {code}")
#         is_safe, _ = verifier.is_safe(code)
#         print(f"Safe Status: {is_safe}")
#         # agent_info = [code, [randrange(0, 7), randrange(0, 7), randrange(0, 7)]]
#         print(f"="*40)