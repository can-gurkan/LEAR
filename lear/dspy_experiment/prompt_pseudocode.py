import dspy
import dspy_experiment.config
from prompts import LEARPrompts


# Define the signature for the reasoning step
class MovementReasoning(dspy.Signature):
    """Generate movement strategy and pseudocode for a NetLogo turtle agent."""
    
    current_rule = dspy.InputField(
        desc="Current movement rule being used by the turtle"
    )
    sensor_readings = dspy.InputField(
        desc="List of 3 values representing food distances"
    )
    strategy = dspy.OutputField(
        desc="Brief strategy explanation"
    )
    pseudocode = dspy.OutputField(
        desc="Movement pseudocode with embedded reasoning as comments"
    )


# Define the signature for the code generation step
class NetLogoCodeGen(dspy.Signature):
    """Convert movement strategy and pseudocode into valid NetLogo code."""
    
    strategy = dspy.InputField(
        desc="Movement strategy explanation"
    )
    pseudocode = dspy.InputField(
        desc="Movement pseudocode with reasoning"
    )
    movement_code = dspy.OutputField(
        desc="Valid NetLogo movement code"
    )


# Create the two-step program
class NetLogoPromptPseudocode(dspy.Module):
    def __init__(self):
        super().__init__()
        self.reasoning_step = dspy.ChainOfThought(MovementReasoning)
        self.code_step = dspy.ChainOfThought(NetLogoCodeGen)
        self.prompts = LEARPrompts()

    def forward(self, current_rule, sensor_readings):
        # Step 1: Generate strategy and pseudocode
        reasoning_result = self.reasoning_step(
            current_rule=current_rule,
            sensor_readings=sensor_readings
        )

        # Step 2: Convert to NetLogo code
        code_result = self.code_step(
            strategy=reasoning_result.strategy,
            pseudocode=reasoning_result.pseudocode
        )

        return dspy.Prediction(
            strategy=reasoning_result.strategy,
            pseudocode=reasoning_result.pseudocode,
            movement_code=code_result.movement_code
        )
