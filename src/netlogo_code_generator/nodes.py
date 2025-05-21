"""
Node implementations for the NetLogo code generation graph.
"""

import logging
from typing import Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, END

from src.netlogo_code_generator.state import GenerationState
from src.mutation.text_based_evolution import TextBasedEvolution
from src.graph_providers.base import GraphProviderBase
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils.logging import get_logger
from src.utils.retry_config import should_retry

# Get the global logger instance
logger = get_logger()

class GenerationState(TypedDict):
    """State for the NetLogo code generation graph."""
    original_code: str
    current_code: str
    agent_info: list
    error_message: Optional[str]
    retry_count: int
    use_text_evolution: bool
    initial_pseudocode: str
    modified_pseudocode: Optional[str]

def evolve_pseudocode(
    state: GenerationState,
    provider: GraphProviderBase,
) -> GenerationState:
    """
    Evolve pseudocode using the provider.

    Args:
        state: Current generation state
        provider: Model provider for text generation

    Returns:
        Updated generation state with evolved pseudocode
    """
    logger.info("NODE: evolve_pseudocode - Starting pseudocode evolution")
    
    # Skip if not using text evolution
    if not state["use_text_evolution"]:
        logger.info("Text evolution disabled, skipping pseudocode evolution")
        return state

    try:
        # Get current pseudocode
        current_pseudocode = state.get("modified_pseudocode", state["initial_pseudocode"])
        logger.info(f"Current pseudocode: {current_pseudocode}")

        # Generate evolved pseudocode
        # Instantiate TextBasedEvolution with the LLM provider
        text_evolver = TextBasedEvolution(provider=provider)
        evolved_pseudocode = text_evolver.generate_pseudocode(
            agent_info=state["agent_info"],
            current_text=current_pseudocode,
            original_code=state["original_code"]
        )
        logger.info(f"Evolved pseudocode: {evolved_pseudocode}")

        # Update state with evolved pseudocode
        return {**state, "modified_pseudocode": evolved_pseudocode}

    except Exception as e:
        logger.error(f"Error in evolve_pseudocode: {str(e)}")
        return state

def generate_code(
    state: GenerationState,
    provider: GraphProviderBase
) -> GenerationState:
    """
    Generate code using the provider.

    Args:
        state: Current generation state
        provider: Model provider for code generation

    Returns:
        Updated generation state with new code
    """
    retry_count = state.get('retry_count', 0)
    error_msg = state.get('error_message', None)
    logger.info(f"NODE: generate_code - retry_count: {retry_count}, error_message: {error_msg}")
    
    try:
        # Check if we have both modified_pseudocode and error_message for retry scenario
        if state.get("modified_pseudocode") and state.get("error_message"):
            logger.info("Using both modified_pseudocode and error_message for code generation")
        elif state.get("modified_pseudocode"):
             logger.info("Using modified_pseudocode for code generation")
        elif state.get("error_message"):
             logger.info("Using error_message for code generation retry")
        else:
             logger.info("Generating code based on initial state (no pseudocode modification or error)")

        # Call the provider using the new state-based interface
        new_code = provider.generate_code_from_state(state)

    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        new_code = state["current_code"]
    
    code_sample = new_code
    logger.info(f"Generated new code (sample): {code_sample}")
    return {**state, "current_code": new_code}

def verify_code(
    state: GenerationState, 
    verifier: NetLogoVerifier
) -> GenerationState:
    """
    Verify the generated code.
    
    Args:
        state: Current generation state
        verifier: NetLogo verifier for code validation
        
    Returns:
        Updated generation state with verification results
    """
    logger.info(f"NODE: verify_code - current retry count: {state.get('retry_count', 0)}")
    
    is_safe, error_message = verifier.is_safe(state["current_code"])
    error_msg_sample = error_message if error_message else None
    logger.info(f"Verification result: is_safe={is_safe}, error_message={error_msg_sample}")
    
    result = {
        **state, 
        "error_message": None if is_safe else error_message
    }
    
    # If verification failed, increment retry count and update initial_pseudocode
    if result["error_message"]:
        logger.info(f"Verification failed with error: {error_msg_sample}, incrementing retry count")
        result["retry_count"] = state["retry_count"] + 1
        
        # Update initial_pseudocode with modified_pseudocode if available
        if state.get("modified_pseudocode"):
            logger.info("Updating initial_pseudocode with modified_pseudocode")
            result["initial_pseudocode"] = state["modified_pseudocode"]
        else:
            logger.info("Updating code with Error")
    else:
        logger.info("Verification successful")
    
    return result

def should_retry_node(state: GenerationState) -> str:
    """
    Determine if code generation should be retried.
    
    Args:
        state: Current generation state
        
    Returns:
        "retry" if should retry, "end" otherwise
    """
    retry_decision = should_retry(state["retry_count"], state["error_message"])
    logger.info(f"Should retry decision: {retry_decision}")
    return "retry" if retry_decision else "end"
