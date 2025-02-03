import instructor
from groq import Groq
import logging
from code_generator_base import BaseCodeGenerator, NLogoCode
from verify_netlogo_code import NetLogoVerifier
import traceback
# from langchain_groq import ChatGroq

class GroqCodeGenerator(BaseCodeGenerator):
    def __init__(self, api_key: str, verifier: NetLogoVerifier):
        """Initialize with API key and verifier instance."""
        super().__init__(verifier)
        self.api_key = api_key
        try:
            self.client = instructor.from_groq(
                Groq(api_key=api_key), 
                mode=instructor.Mode.JSON
            )
        except Exception as e:
            logging.error(f"Failed to initialize Groq client: {str(e)}")
            raise

    def _generate_code_internal(self, agent_info: list, error_prompt: str = None) -> str:
        """Internal method to generate code using Groq API."""
        if error_prompt:
            # Use error prompt for retry attempts
            prompt = error_prompt
        else:
            # Use base prompt for initial generation
            prompt = self.get_base_prompt(agent_info=agent_info, model_type='groq')
            
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=NLogoCode,
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert in evolving NetLogo agent behaviors.
                    Focus on creating efficient, survival-optimized netlogo code."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.65,
        )
        return response.new_code.strip()

    def generate_code(self, agent_info: list) -> str:
        """Generate new NetLogo code using Groq API with retry logic."""
        try:
            # Validate input
            is_valid, error_msg = self.validate_input(agent_info)
            if not is_valid:
                logging.error(f"Invalid input: {error_msg}")
                return agent_info[0]
            
            # Log attempt
            logging.info(f"Attempting generation for rule: {agent_info[0]} with food input: {agent_info[1]}")
            
            # Use retry handler with single LLM instance
            return self.retry_handler.execute_with_retry(
                original_code=agent_info[0],
                generate_fn=self._generate_code_internal,
                agent_info=agent_info
            )
            
        except Exception as e:
            logging.error(f"Error during code generation: {traceback.format_exc()}")
            return agent_info[0]
