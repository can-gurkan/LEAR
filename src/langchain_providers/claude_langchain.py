import os
import logging
from langchain_anthropic import ChatAnthropic
from langchain.chains import LLMChain

from src.langchain_providers.base import LangchainProviderBase
from src.verification.verify_netlogo import NetLogoVerifier

class LangchainClaudeGenerator(LangchainProviderBase):
    """Claude implementation using Langchain."""
    
    def __init__(self, verifier: NetLogoVerifier):
        """Initialize with verifier instance."""
        super().__init__(verifier)
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            
    def initialize_llm(self) -> LLMChain:
        """Initialize and return Claude-specific LLM chain."""
        try:
            llm = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                anthropic_api_key=self.api_key,
                temperature=0.7,
                max_tokens=1000
            )
            return llm
            
        except Exception as e:
            logging.error(f"Failed to initialize Claude LLM chain: {str(e)}")
            raise
