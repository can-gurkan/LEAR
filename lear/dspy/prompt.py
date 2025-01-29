import dspy
import dspy.config
import prompts
# Define the signature for the NetLogo movement program
class NetLogoMovement(dspy.Signature):
    """Generate movement code for a NetLogo turtle agent optimized for food collection."""
    current_rule = dspy.InputField(desc="Current movement rule being used by the turtle")
    sensor_readings = dspy.InputField(desc="List of 3 values representing food distances")
    movement_code = dspy.OutputField(desc="NetLogo code for turtle movement")
    reasoning = dspy.OutputField(desc="Step-by-step reasoning for the movement strategy")

# Create the program using ChainOfThought for explicit reasoning
class NetLogoPrompt(dspy.Module):
    def __init__(self):
        super().__init__()
        self.chain = dspy.ChainOfThought(NetLogoMovement)
    
    def forward(self, current_rule, sensor_readings):
        prompt = f"""You are an expert NetLogo coder. You are trying to improve the code of a given turtle agent that is trying to collect as much food as possible. Improve the given agent movement code following these precise specifications:

INPUT CONTEXT:
- Current rule: {current_rule}
- Food sensor readings: {sensor_readings}
  - Input list contains three values representing distances to food in three cone regions of 20 degrees each
  - The first item in the input list is the distance to the nearest food in the left cone, the second is the right cone, and the third is the front cone
  - Each value encodes the distance to nearest food source where a value of 0 indicates no food
  - Non-zero lower values indicate closer food
  - Use these to inform movement strategy

CONSTRAINTS:
1. Do not include code to kill or control any other agents
2. Do not include code to interact with the environment
3. Do not include code to change the environment
4. Do not include code to create new agents
5. Do not include code to create new food sources
6. Do not include code to change the rules of the simulation

EXAMPLES OF VALID PATTERNS:
Current Rule: fd 1 rt random 45 fd 2 lt 30
Valid: ifelse item 0 input != 0 [rt 15 fd 0.5] [rt random 30 lt random 30 fd 5]
Why: Turns right and goes forward a little to reach food if the first element of input list contains a non-zero value, else moves forward in big steps and turns randomly to explore

INVALID EXAMPLES:
❌ ask turtle 1 [die]
❌ ask other turtles [die]
❌ set energy 100
❌ hatch-food 5
❌ clear-all

STRATEGIC GOALS:
1. Balance exploration and food-seeking behavior
2. Respond to sensor readings intelligently
3. Combine different movement patterns

Let's think about this step by step:
1. First, analyze the current sensor readings to understand food locations
2. Consider if any food is detected and where it is relative to the turtle
3. Compare the current rule with potential improvements
4. Determine if we should prioritize exploration or food-seeking
5. Design movement pattern based on the analysis
6. Ensure the code follows all constraints
7. Output the optimized movement code

Generate ONLY the movement code. Code must be runnable in NetLogo in the context of a turtle."""

        return self.chain(
            current_rule=current_rule,
            sensor_readings=sensor_readings
        )

# Example usage
prompt = NetLogoPrompt()
result = prompt(
    current_rule="lt random 20 rt random 20 fd 1",
    sensor_readings=str([0, 0, 0.6805890740381396])
)
print(result)