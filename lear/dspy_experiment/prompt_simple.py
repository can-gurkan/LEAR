import dspy
import dspy_experiment.config
from prompts import LEARPrompts


class NetLogoMovement(dspy.Signature):
    """Generate movement code for a NetLogo turtle agent optimized for food collection."""

    current_rule = dspy.InputField(
        desc="Current movement rule being used by the turtle"
    )
    sensor_readings = dspy.InputField(
        desc="List of 3 values representing food distances"
    )

    reasoning = dspy.OutputField(
        desc="Step-by-step reasoning for the movement strategy."
    )
    pseudocode = dspy.OutputField(
        desc="In psuedocode, detail the movement strategy."
    )

    movement_code = dspy.OutputField(
        desc="NetLogo code for turtle movement. 'item 0 input' is the distance to the left cone, 'item 1 input' is the distance to the middle cone, and 'item 2 input' is the distance to the right cone."
    )

class NetLogoPrompt(dspy.Module):
    def __init__(self):
        super().__init__()
        self.chain = dspy.ChainOfThought(NetLogoMovement)
        self.prompts = LEARPrompts()

    def forward(self, current_rule, sensor_readings):
        prompt = self.prompts.groq_prompt2.format(current_rule, sensor_readings)

        return self.chain(current_rule=current_rule, sensor_readings=sensor_readings)
