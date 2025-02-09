import os
import datetime
import logging

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
    def __init__(self, log_directory="logs"):
        """Initialize a new logger instance."""
        self.log_directory = log_directory
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = os.path.join(self.log_directory, f"log_{timestamp}.log")

        self.logger = logging.getLogger("NetLogoLogger")
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def log_initial_parameters(self, params):
        """Log simulation parameters at the start."""
        self.logger.info(f"Simulation Parameters: {params}")

    def log_base_prompt(self, prompt):
        """Log the LLM base prompt."""
        self.logger.info(f"Base Prompt: {prompt}")

    def log_generation(self, generation, best_rule, mean_energy, best_energy, mean_food_collected, error_log, current_rule, mutated_rule):
        """Log per-generation evolution stats."""
        self.logger.info(
            f"Generation: {generation},\n Best Rule: {best_rule}, "
            f"\n Mean Energy: {mean_energy},\n Best Energy: {best_energy},\n Mean Food Collected: {mean_food_collected},\n Error Log: {error_log}"
            f"\n Current Rule: {current_rule}"
            f"\n Mutated Rule: {mutated_rule}"
        )