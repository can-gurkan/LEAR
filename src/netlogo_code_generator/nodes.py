"""
Node implementations for the NetLogo code generation graph.
"""

import logging
from typing import Dict, Any

from src.netlogo_code_generator.state import GenerationState
from src.mutation.text_based_evolution import TextBasedEvolution
from src.graph_providers.base import GraphProviderBase
from src.verification.verify_netlogo import NetLogoVerifier
from src.utils.logging import get_logger

# Get the global logger instance
logger = get_logger()


def evolve_pseudocode(
    state: GenerationState,
    provider: GraphProviderBase,
) -> GenerationState:
    """
    Generate modified pseudocode if text-based evolution is enabled.

    Args:
        state: Current generation state
        provider: Model provider for text generation
        use_text_evolution: Whether to use text-based evolution

    Returns:
        Updated generation state with modified pseudocode
    """
    logger.info(f"NODE: evolve_pseudocode")
    use_text_evolution = state.get("use_text_evolution", False)
    logger.info(f"Evolving pseudocode, use_text_evolution: {use_text_evolution}")

    
    logger.info(f"Original code: {state['original_code']}")
    logger.info(f"Initial pseudocode: {state['initial_pseudocode']}")
    
    if not state["use_text_evolution"]:
        logger.info("Text evolution disabled, skipping pseudocode generation")
        return state

    logger.info("Text evolution enabled, generating pseudocode")
    text_evolution = TextBasedEvolution(provider)
    modified_pseudocode = text_evolution.generate_pseudocode( 
        state["agent_info"], 
        state["initial_pseudocode"], 
        state["original_code"]
    )
    logger.info(f"Generated modified pseudocode: \n{modified_pseudocode}")
    
    state["modified_pseudocode"] = modified_pseudocode
    return state

def generate_code(
    state: GenerationState,
    provider: GraphProviderBase
) -> GenerationState:
    logger.info(f"Generating code, retry_count: {state['retry_count']}, error_message: {state['error_message']}")
    """
    Generate code using the provider.

    Args:
        state: Current generation state
        provider: Model provider for code generation

    Returns:
        Updated generation state with new code
    """
    
    # Generate code using provider
    # logger.info(f"Agent info: {state['agent_info']}")
    # logger.info(f"Modified pseudocode: {state['modified_pseudocode']}")
    logger.info(f"NODE: generate_code")
    
    new_code = provider.generate_code_with_model(
        state["agent_info"],
        state["current_code"],
        state["modified_pseudocode"],
        state["error_message"],
    )
    
    logger.info(f"Generated new code: {new_code}")
    return {**state, "current_code": new_code}

def verify_code(
    state: GenerationState, 
    verifier: NetLogoVerifier
) -> GenerationState:
    logger.info(f"Verifying code, current retry count: {state['retry_count']}")
    """
    Verify the generated code.
    
    Args:
        state: Current generation state
        verifier: NetLogo verifier for code validation
        
    Returns:
        Updated generation state with verification results
    """
    logger.info(f"NODE: verify_code")
    # logger.info(f"Code to verify: {state['current_code']}")
    is_safe, error_message = verifier.is_safe(state["current_code"])
    logger.info(f"Verification result: is_safe={is_safe}, error_message={error_message}")
    
    result = {
        **state, 
        "error_message": None if is_safe else error_message
    }
    
    # If verification failed, increment retry count and update initial_pseudocode
    if result["error_message"]:
        logger.info(f"Verification failed with error: {result['error_message']}, incrementing retry count")
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

def should_retry(state: GenerationState, max_attempts: int = 5) -> str:
    logger.info(f"Checking if should retry, retry_count: {state['retry_count']}, max_attempts: {max_attempts}, error_message: {state['error_message']}")
    """
    Determine if code generation should be retried.
    
    Args:
        state: Current generation state
        max_attempts: Maximum number of retry attempts
        
    Returns:
        "retry" if should retry, "end" otherwise
    """
    should_retry_value = "retry" if state["error_message"] and state["retry_count"] < max_attempts else "end"
    logger.info(f"Should retry decision: {should_retry_value}")
    return should_retry_value

def increment_retry_count(state: Dict[str, Any], node_name: str, node_output: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Increment retry count middleware called, node_name: {node_name}, error_message: {node_output.get('error_message')}")
    """
    Middleware to increment retry count when verification fails.
    Also updates initial_pseudocode with modified_pseudocode for the next iteration.

    Args:
        state: Current state before node execution
        node_name: Name of the node that was executed
        node_output: Output from the node execution

    Returns:
        Updated state with incremented retry count if needed
    """
    if node_name == "verify_code" and node_output.get("error_message"):
        logger.info(f"Verification failed, incrementing retry count from {node_output['retry_count']} to {node_output['retry_count'] + 1}")
        # Increment retry count
        result = {**node_output, "retry_count": node_output["retry_count"] + 1}
        
        # Update initial_pseudocode with modified_pseudocode if available
        if node_output.get("modified_pseudocode"):
            logger.info("Updating initial_pseudocode with modified_pseudocode in middleware")
            result["initial_pseudocode"] = node_output["modified_pseudocode"]
            
        return result
    logger.info("No error message or not verify_code node, skipping retry count increment")
    return node_output
