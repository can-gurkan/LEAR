import os
import logging
from langchain_deepseek import ChatDeepSeek
from langchain.chains import LLMChain

from src.langchain_providers.base import LangchainProviderBase
from src.verification.verify_netlogo import NetLogoVerifier

class LangchainDeepseekGenerator(LangchainProviderBase):
    """Deepseek implementation using Langchain."""
    
    def __init__(self, verifier: NetLogoVerifier):
        """Initialize with verifier instance."""
        super().__init__(verifier)
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")
            
    def initialize_llm(self) -> LLMChain:
        """Initialize and return Deepseek-specific LLM chain."""
        try:
            llm = ChatDeepSeek(
                model_name="deepseek-chat",
                api_key=self.api_key,
                temperature=0.7,
                max_tokens=100
            )
            return llm
            
        except Exception as e:
            logging.error(f"Failed to initialize Deepseek LLM chain: {str(e)}")
            raise
