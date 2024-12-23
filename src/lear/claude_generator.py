from anthropic import Anthropic
import logging
from code_generator_base import BaseCodeGenerator
from verify_netlogo_code import NetLogoVerifier

class ClaudeCodeGenerator(BaseCodeGenerator):
    def __init__(self, api_key: str, verifier: NetLogoVerifier):
        """Initialize with API key and verifier instance."""
        self.api_key = api_key
        self.verifier = verifier
        try:
            self.client = Anthropic(api_key=api_key)
        except Exception as e:
            logging.error(f"Failed to initialize Claude client: {str(e)}")
            raise

    def generate_code(self, agent_info: list) -> str:
        """Generate new NetLogo code using Claude API."""
        try:
            # Validate input
            is_valid, error_msg = self.validate_input(agent_info)
            if not is_valid:
                logging.error(f"Invalid input: {error_msg}")
                return agent_info[0]
            
            # Log attempt
            logging.info(f"Attempting generation for rule: {agent_info[0]} with food input: {agent_info[1]}")
            
            # Generate new code
            prompt = self.get_base_prompt(agent_info=agent_info, model_type='claude')
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    },
                ],
                temperature=0.7,
            )
            
            new_code = response.content[0].text.strip()
            
            # Verify safety
            # is_safe, safety_msg = self.verifier.is_safe(new_code)
            is_safe = True
            
            if is_safe:
                logging.info(f"Successfully generated new code: {new_code}")
                return new_code
            else:
                logging.warning(f"Generated unsafe code: {new_code}. Safety message: {safety_msg}")
                return agent_info[0]
            
        except Exception as e:
            logging.error(f"Error during code generation: {str(e)}")
            return agent_info[0]