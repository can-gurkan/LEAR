import os
import logging
from typing import Optional
from dotenv import load_dotenv
from enum import Enum

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain

from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from src.generators.base import BaseCodeGenerator
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils.storeprompts import prompts

# Load environment variables
load_dotenv()

class SupportedModels(Enum):
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    OPENAI = "openai"

class LangchainUnifiedGenerator(BaseCodeGenerator):
    """
    Unified Langchain provider that supports multiple models.
    """

    def __init__(self, model_name: str, verifier: NetLogoVerifier):
        """
        Initialize with model name and verifier instance.
        """
        super().__init__(verifier)
        self.model_name = model_name
        self.llm_chain = None
        self.api_key = None

        if self.model_name == SupportedModels.CLAUDE.value:
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        elif self.model_name == SupportedModels.DEEPSEEK.value:
            self.api_key = os.getenv('DEEPSEEK_API_KEY')
            if not self.api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        elif self.model_name == SupportedModels.GROQ.value:
            self.api_key = os.getenv('GROQ_API_KEY')
            if not self.api_key:
                raise ValueError("GROQ_API_KEY environment variable is required")
        elif self.model_name == SupportedModels.OPENAI.value:
            self.api_key = os.getenv('OPENAI_API_KEY')
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
        else:
            raise ValueError(f"Unsupported model name: {self.model_name}")

    def initialize_llm(self) -> LLMChain:
        """
        Initialize and return provider-specific LLM chain based on model name.
        """
        try:
            if self.model_name == SupportedModels.CLAUDE.value:
                llm = ChatAnthropic(
                    model="claude-3-sonnet-20240229",
                    anthropic_api_key=self.api_key,
                    temperature=0.7,
                    max_tokens=1000
                )
            elif self.model_name == SupportedModels.DEEPSEEK.value:
                llm = ChatDeepSeek(
                    model_name="deepseek-chat",
                    api_key=self.api_key,
                    temperature=0.7,
                    max_tokens=100
                )
            elif self.model_name == SupportedModels.GROQ.value:
                llm = ChatGroq(
                    model_name="llama-3.3-70b-versatile",
                    groq_api_key=self.api_key,
                    temperature=0.65,
                    max_tokens=1000
                )
            elif self.model_name == SupportedModels.OPENAI.value:
                llm = ChatOpenAI(
                    model="gpt-4o",
                    openai_api_key=self.api_key,
                    temperature=0.7,
                    max_tokens=1000
                )
            else:
                raise ValueError(f"Unsupported model name: {self.model_name}")
            return llm

        except Exception as e:
            logging.error(f"Failed to initialize LLM chain for {self.model_name}: {str(e)}")
            raise

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

def create_langchain_provider(model_name: str, verifier: NetLogoVerifier):
    """
    Factory method to create Langchain provider based on model name.
    """
    return LangchainUnifiedGenerator(model_name, verifier)
