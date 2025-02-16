import os
import logging
from langchain_groq import ChatGroq
from langchain.chains import LLMChain

from src.langchain_providers.base import LangchainProviderBase
from src.verification.verify_netlogo import NetLogoVerifier

class LangchainGroqGenerator(LangchainProviderBase):
    """Groq implementation using Langchain."""
    
    def __init__(self, verifier: NetLogoVerifier):
        """Initialize with verifier instance."""
        super().__init__(verifier)
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
            
    def initialize_llm(self) -> LLMChain:
        """Initialize and return Groq-specific LLM chain."""
        try:
            llm = ChatGroq(
                model_name="llama2-70b-4096",
                groq_api_key=self.api_key,
                temperature=0.65,
                max_tokens=1000
            )
            return llm
            
        except Exception as e:
            logging.error(f"Failed to initialize Groq LLM chain: {str(e)}")
            raise
