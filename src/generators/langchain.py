from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain
from typing import Optional, Union, Tuple
from src.utils.logging import get_logger
from src.utils.storeprompts import prompts

from src.generators.base import BaseCodeGenerator
from src.mutation.text_based_evolution import TextBasedEvolution
from src.verification.verify_netlogo import NetLogoVerifier
from src.langchain_providers.base import LangchainProviderBase


class LangChainCodeGenerator(BaseCodeGenerator):
    def __init__(self, provider: Union[LLMChain, LangchainProviderBase], verifier: NetLogoVerifier):
        """Initialize with LangChain provider and verifier

        Args:
            provider: Either a raw LLMChain or a LangchainProviderBase implementation
            verifier: NetLogoVerifier instance for code validation
        """
        super().__init__(verifier)
        self.provider = provider
        self.thought_log = []  # For future agentic capabilities
        self.logger = get_logger()

    def _build_chain_of_thought_prompt(self, agent_info: list, evolution_description: Optional[str] = None) -> ChatPromptTemplate:
        """Construct chain-of-thought prompt template with optional evolution description."""
        

        if evolution_description:
            
            return ChatPromptTemplate.from_messages([
                ("system", prompts["langchain"]["cot_system"]),
                ("user", "This is the evolution description: {evolution_description} Here is the code: {code}".format(evolution_description=evolution_description, code=agent_info[0]))
            ])
        else:
            base_prompt = self.get_base_prompt(agent_info)
            return ChatPromptTemplate.from_messages([
                ("system", prompts["langchain"]["cot_system"]),
                ("user", prompts["langchain"]["cot_template"].format(base_prompt=base_prompt, code=agent_info[0], inputs=agent_info[1]))
            ])

    def _generate_code_internal(self, agent_info: list, error_prompt: Optional[str] = None, use_text_evolution: bool = False) -> str:
        """Generate code using LangChain with chain-of-thought reasoning"""
        self.logger.info("Starting LangChain code generation")
        try: 
            if error_prompt:
                prompt = ChatPromptTemplate.from_template(error_prompt)
            else:
                evolution_description = None
                if use_text_evolution:
                    text_evolution = TextBasedEvolution(self.provider if isinstance(self.provider, LangchainProviderBase) else None)
                    evolution_description = text_evolution.generate_evolution_description(agent_info)
                    
                prompt = self._build_chain_of_thought_prompt(agent_info, evolution_description)
                
                
            self.logger.info(f"Code Generation with Text based Evolution prompt: {prompt}")

            # Handle both raw LLMChain and provider implementations
            if isinstance(self.provider, LangchainProviderBase):
                chain = prompt | self.provider.initialize_llm() | StrOutputParser()
            else:
                chain = prompt | self.provider | StrOutputParser()

            response = chain.invoke({"input": agent_info})

            # Extract code block from response
            if "```netlogo" in response:
                code = response.split("```netlogo")[1].split("```")[0].strip()
                self.logger.info(f"LangChain code generation successful. Generated code: {code}")
                return code
            self.logger.info(f"LangChain response: {response}")
            return response

        except Exception as e:
            self.logger.error(f"LangChain generation error: {str(e)}")
            return agent_info[0]

    def generate_code(self, agent_info: list, use_text_evolution: bool = False) -> str:
        """Generate code with LangChain integration"""
        self.logger.info("Starting LangChain code generation workflow")
        try:
            # Validate input format
            is_valid, error_msg = self.validate_input(agent_info)
            if not is_valid:
                self.logger.error(f"Invalid input: {error_msg}")
                return agent_info[0]

            # Use existing retry handler with LangChain integration
            result = self.retry_handler.execute_with_retry(
                original_code=agent_info[0],
                generate_fn=self._generate_code_internal,
                agent_info=agent_info,
                use_text_evolution=use_text_evolution
            )
            self.logger.info(f"LangChain code generation workflow complete. Result: {result}")
            return result

        except Exception as e:
            self.logger.error(f"LangChain workflow error: {str(e)}")
            return agent_info[0]
