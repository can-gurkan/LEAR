from anthropic import Anthropic
import logging, gin
from src.generators.base import BaseCodeGenerator
from src.verification.verify_netlogo import NetLogoVerifier
# from langchain_anthropic import ChatAnthropic

@gin.configurable
class ClaudeCodeGenerator(BaseCodeGenerator):
    def __init__(self, api_key: str, verifier: NetLogoVerifier, temp=0, max_tokens=1024, model_name="claude-3-5-sonnet-20241022"):
        """Initialize with API key and verifier instance."""
        super().__init__(verifier)
        self.api_key = api_key
        try:
            self.client = Anthropic(api_key=api_key)
        except Exception as e:
            logging.error(f"Failed to initialize Claude client: {str(e)}")
            raise
        self.temperature = temp
        self.max_tokens = max_tokens
        self.model_name = model_name

    def _generate_code_internal(self, agent_info: list, error_prompt: str = None, use_text_evolution=False) -> str:
        """Internal method to generate code using Claude API."""
        if error_prompt:
            # Use error prompt for retry attempts
            prompt = error_prompt
        else:
            # Use base prompt for initial generation
            prompt = self.get_base_prompt(agent_info=agent_info, model_type='claude')
            
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            temperature=self.temperature,
        )
        return response.content[0].text.strip()

    def generate_code(self, agent_info: list) -> str:
        """Generate new NetLogo code using Claude API with retry logic."""
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
            logging.error(f"Error during code generation: {str(e)}")
            return agent_info[0]
