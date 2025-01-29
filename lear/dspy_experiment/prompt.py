import dspy
import dspy_experiment.config
from prompts import LEARPrompts


# Define the signature for the NetLogo movement program
class NetLogoMovement(dspy.Signature):
    """Generate movement code for a NetLogo turtle agent optimized for food collection."""

    current_rule = dspy.InputField(
        desc="Current movement rule being used by the turtle"
    )
    sensor_readings = dspy.InputField(
        desc="List of 3 values representing food distances"
    )
    movement_code = dspy.OutputField(desc="NetLogo code for turtle movement")
    reasoning = dspy.OutputField(
        desc="Step-by-step reasoning for the movement strategy"
    )


# Create the program using ChainOfThought for explicit reasoning
class NetLogoPrompt(dspy.Module):
    def __init__(self):
        super().__init__()
        self.chain = dspy.ChainOfThought(NetLogoMovement)
        self.prompts = LEARPrompts()

    def forward(self, current_rule, sensor_readings):
        prompt = self.prompts.groq_prompt2.format(current_rule, sensor_readings)

        return self.chain(current_rule=current_rule, sensor_readings=sensor_readings)
