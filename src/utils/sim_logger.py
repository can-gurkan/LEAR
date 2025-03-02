import os
import datetime
import logging
import json

_logger_instance = None  # Global variable to hold the logger instance

def initialize_logger():
    """Reinitialize the logger (called every time NetLogo setup runs)."""

    global _logger_instance

    _logger_instance = NetLogoLogger()  # Create a new logger instance
    
    return _logger_instance

def get_logger():
    """Retrieve the current logger instance."""


    if _logger_instance is None:
        raise ValueError("Logger has not been initialized. Call initialize_logger() first.")

    return _logger_instance

class NetLogoLogger:
    def __init__(self, base_log_directory="../Logs"):
        """Initialize a new logger instance."""
        self.base_log_directory = base_log_directory

        # Create a new folder with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_directory = os.path.join(self.base_log_directory, timestamp)
        os.makedirs(self.log_directory, exist_ok=True)

        # Define log file path
        self.log_file = os.path.join(self.log_directory, "simulation.log")
        self.json_file = os.path.join(self.log_directory, "generation_output.json")

        # Setup logger
        self.logger = logging.getLogger(f"NetLogoLogger_{timestamp}")
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

        # json output list
        self.generation_data = []

    def log_initial_parameters(self, params):
        """Log simulation parameters at the start."""
        self.logger.info(f"Simulation Parameters: {params}")

    def log_base_prompt(self, prompt):
        """Log the LLM base prompt."""
        self.logger.info(f"Base Prompt: {prompt}")

    def log_generation(self, generation, best_rule, mean_energy, best_energy, mean_food_collected, error_log, current_rule, mutated_rule, initial_pseudocode=None, modified_pseudocode=None):
        ## TO DO: Modify this so that which parameters are logged can be controlled by the user so that it is nlogo model agnostic
        ## TO DO: Modify so that this works even if multiple agents are being evolved per generation
        """Log per-generation evolution stats."""

        # Append to json data
        generation_entry = {
            "generation": generation,
            "best_rule": best_rule,
            "mean_energy": mean_energy,
            "best_energy": best_energy,
            "mean_food_collected": mean_food_collected,
            "error_log": error_log,
            "current_rule": current_rule,
            "mutated_rule": mutated_rule
        }
        
        # Add pseudocode entries if provided
        if initial_pseudocode is not None:
            generation_entry["initial_pseudocode"] = initial_pseudocode
        
        if modified_pseudocode is not None:
            generation_entry["modified_pseudocode"] = modified_pseudocode
            
        self.generation_data.append(generation_entry)

        # Save to json file
        with open(self.json_file, "w") as f:
            json.dump(self.generation_data, f, indent=4)
