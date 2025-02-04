import os
import logging
from langchain_community.chat_models import ChatDeepseek
from langchain.chains import LLMChain

from .base import LangchainProviderBase
from ..verify_netlogo_code import NetLogoVerifier

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
            llm = ChatDeepseek(
                model_name="deepseek-chat",
                deepseek_api_key=self.api_key,
                temperature=0.7,
                max_tokens=1000
            )
            return LLMChain(llm=llm)
            
        except Exception as e:
            logging.error(f"Failed to initialize Deepseek LLM chain: {str(e)}")
            raise
