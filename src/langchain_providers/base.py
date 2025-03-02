from abc import abstractmethod
import os
from typing import Optional
import logging
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain


from src.generators.base import BaseCodeGenerator
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils.storeprompts import prompts

# Load environment variables
load_dotenv()

class LangchainProviderBase(BaseCodeGenerator):
    """Base class for Langchain-based code generators."""
    
    def __init__(self, verifier: NetLogoVerifier):
        """Initialize with verifier instance."""
        super().__init__(verifier)
        self.llm_chain = None  # To be set by child classes
        
    @abstractmethod
    def initialize_llm(self) -> LLMChain:
        """Initialize and return provider-specific LLM chain."""
        pass
        
    def _build_chain_of_thought_prompt(self, agent_info: list) -> ChatPromptTemplate:
        """Construct chain-of-thought prompt template."""
        base_prompt = self.get_base_prompt(agent_info, 'langchain')
        
        return ChatPromptTemplate.from_messages([
            ("system", prompts["langchain"]["cot_system"]),
            ("user", prompts["langchain"]["cot_template"].format(
                base_prompt,
                code=agent_info[0],
                inputs=agent_info[1]
            ))
        ])
    
    def _generate_code_internal(self, agent_info: list, error_prompt: Optional[str] = None) -> str:
        """Generate code using LangChain with chain-of-thought reasoning."""
        try:
            if not self.llm_chain:
                self.llm_chain = self.initialize_llm()
                
            if error_prompt:
                prompt = ChatPromptTemplate.from_template(error_prompt)
            else:
                prompt = self._build_chain_of_thought_prompt(agent_info)
            
            chain = prompt | self.llm_chain | StrOutputParser()
            response = chain.invoke({"input": agent_info})
            
            # Extract code block from response
            if "```netlogo" in response:
                return response.split("```netlogo")[1].split("```")[0].strip()
            return response
            
        except Exception as e:
            logging.error(f"LangChain generation error: {str(e)}")
            return agent_info[0]

    def generate_code(self, agent_info: list) -> str:
        """Generate code with LangChain integration."""
        try:
            # Validate input format
            is_valid, error_msg = self.validate_input(agent_info)
            if not is_valid:
                logging.error(f"Invalid input: {error_msg}")
                return agent_info[0]
                
            # Use existing retry handler with LangChain integration
            return self.retry_handler.execute_with_retry(
                original_code=agent_info[0],
                generate_fn=self._generate_code_internal,
                agent_info=agent_info
            )
            
        except Exception as e:
            logging.error(f"LangChain workflow error: {str(e)}")
            return agent_info[0]
