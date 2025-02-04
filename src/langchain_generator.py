from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain
from typing import Optional
import logging
from code_generator_base import BaseCodeGenerator, NLogoCode
from verify_netlogo_code import NetLogoVerifier

class LangChainCodeGenerator(BaseCodeGenerator):
    def __init__(self, llm_chain: LLMChain, verifier: NetLogoVerifier):
        """Initialize with LangChain LLMChain and verifier"""
        super().__init__(verifier)
        self.llm_chain = llm_chain
        self.thought_log = []  # For future agentic capabilities
        
    def _build_chain_of_thought_prompt(self, agent_info: list) -> ChatPromptTemplate:
        """Construct chain-of-thought prompt template"""
        base_prompt = self.get_base_prompt(agent_info, 'langchain')
        
        return ChatPromptTemplate.from_messages([
            ("system", "You are a NetLogo code evolution expert. Think step-by-step."),
            ("user", f"""{base_prompt}
            
            Current code block to evolve:
            ```netlogo
            {agent_info[0]}
            ```
            
            Food distance inputs: {agent_info[1]}
            
            Analysis steps:
            1. Identify patterns in existing code
            2. Determine needed modifications based on food inputs
            3. Propose updated code with clear explanations
            4. Validate syntax before final answer""")
        ])
    
    def _generate_code_internal(self, agent_info: list, error_prompt: Optional[str] = None) -> str:
        """Generate code using LangChain with chain-of-thought reasoning"""
        try:
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
        """Generate code with LangChain integration"""
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
