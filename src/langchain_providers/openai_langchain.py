import os
import logging
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

from src.langchain_providers.base import LangchainProviderBase
from src.verification.verify_netlogo import NetLogoVerifier

class LangchainOpenAIGenerator(LangchainProviderBase):
    """OpenAI implementation using Langchain."""
    
    def __init__(self, verifier: NetLogoVerifier):
        """Initialize with verifier instance."""
        super().__init__(verifier)
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
    def initialize_llm(self) -> LLMChain:
        """Initialize and return OpenAI-specific LLM chain."""
        try:
            llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                openai_api_key=self.api_key,
                temperature=0.7,
                max_tokens=1000
            )
            return llm
            
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI LLM chain: {str(e)}")
            raise
