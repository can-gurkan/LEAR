import instructor
from groq import Groq
import logging
from code_generator_base import BaseCodeGenerator, NLogoCode
from verify_netlogo_code import NetLogoVerifier
import traceback
from dspy_experiment.prompt import NetLogoPrompt

class GroqCodeGenerator(BaseCodeGenerator):
    def __init__(self, api_key: str, verifier: NetLogoVerifier):
        """Initialize with API key and verifier instance."""
        self.api_key = api_key
        self.verifier = verifier
        try:
            self.client = instructor.from_groq(
                Groq(api_key=api_key), 
                mode=instructor.Mode.JSON
            )
        except Exception as e:
            logging.error(f"Failed to initialize Groq client: {str(e)}")
            raise

    def generate_code(self, agent_info: list) -> str:
        """Generate new NetLogo code using Groq API."""
        try:
            # Validate input
            is_valid, error_msg = self.validate_input(agent_info)
            if not is_valid:
                logging.error(f"Invalid input: {error_msg}")
                return agent_info[0]
            
            # Log attempt
            logging.info(f"Attempting generation for rule: {agent_info[0]} with food input: {agent_info[1]}")
            
            # Generate new code
            # prompt = self.get_base_prompt(agent_info=agent_info, model_type='groq')
            # response = self.client.chat.completions.create(
            #     model="llama-3.3-70b-versatile",
            #     response_model=NLogoCode,
            #     messages=[
            #         {
            #             "role": "system", 
            #             "content": """You are an expert in evolving NetLogo agent behaviors.
            #             Focus on creating efficient, survival-optimized netlogo code."""
            #         },
            #         {
            #             "role": "user",
            #             "content": prompt
            #         }
            #     ],
            #     temperature=0.65,
            # )
            prompt = NetLogoPrompt()
            result = prompt(
                current_rule=agent_info[0],
                sensor_readings=str(agent_info[1])
            )
            reasoning = result.reasoning
            logging.info(f"Reasoning: {reasoning}")
            new_code = result.movement_code
            
            # Verify safety
            is_safe, safety_msg = self.verifier.is_safe(new_code)
            
            if is_safe:
                logging.info(f"Successfully generated new code: {new_code}")
                return new_code
            else:
                logging.warning(f"Generated unsafe code: {new_code}. Safety message: {safety_msg}")
                return agent_info[0]
            
        except Exception as e:
            logging.error(f"Error during code generation: {traceback.print_exc()}")
            return agent_info[0]