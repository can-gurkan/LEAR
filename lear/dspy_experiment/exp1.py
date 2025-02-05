import difflib
import logging
import dspy
from dspy.teleprompt import MIPROv2
import os
from dspy import Example
import litellm

#litellm.suppress_debug_info = True


# Configure the language model
lm = dspy.LM(
    model="mistral/codestral-2501", 
    api_key=os.getenv("MISTRAL_API_KEY"), 
    temperature=0
)

dspy.configure(lm=lm)
#logging.basicConfig(level=logging.INFO)
# -----------------------------------------------------------------------------
# Step 1: Define signatures and modules for NetLogo code conversion
# -----------------------------------------------------------------------------
class NetLogoConversion(dspy.Signature):
    """Convert pseudocode to NetLogo code with verification."""
    pseudocode = dspy.InputField(desc="Natural language description of NetLogo behavior")
    netlogo_code = dspy.OutputField(desc="Syntactically correct NetLogo code that implements the desired pseudocode behavior")

class ConvertToNetlogo(dspy.ChainOfThought):
    """Module that implements the NetLogo conversion signature."""
    def __init__(self):
        super().__init__(NetLogoConversion)

convert_to_netlogo = ConvertToNetlogo()

# -----------------------------------------------------------------------------
# Step 2: Define verification signature and module
# -----------------------------------------------------------------------------
class NetLogoVerification(dspy.Signature):
    """Verify NetLogo code by converting back to pseudocode."""
    netlogo_code = dspy.InputField(desc="NetLogo code to verify")
    pseudocode = dspy.OutputField(desc="Natural language description of what the NetLogo code does")

class NetLogoToPseudocode(dspy.ChainOfThought):
    """Module that implements the NetLogo verification signature."""
    def __init__(self):
        super().__init__(NetLogoVerification)

class NetLogoJudgement(dspy.Signature):
    original_pseudocode: str = dspy.InputField(desc="Natural language description of intended NetLogo behavior")
    netlogo_code: str = dspy.InputField(desc="Generated NetLogo code to be judged")
    syntax_reasoning: str = dspy.OutputField(desc="Reasoning about the similarity of the syntax of the NetLogo code to the original pseudocode")
    behavior_reasoning: str = dspy.OutputField(desc="Reasoning about the similarity in functionality of the NetLogo code to the original pseudocode")
    score: float = dspy.OutputField(desc="Evaluation score between 0 (poor) and 1 (perfect)")

class NetLogoJudge(dspy.ChainOfThought):
    """Module that judges the NetLogo conversion output with detailed reasoning."""
    def __init__(self):
        super().__init__(NetLogoJudgement)
# -----------------------------------------------------------------------

def verify_conversion(original_pseudocode: str, generated_netlogo: str) -> float:
    """
    Verifies the conversion by using a second LLM as a judge.
    
    The judge (via NetLogoJudge) evaluates the generated NetLogo code on:
      1. Syntactic correctness.
      2. Faithfulness to the intended behavior.
    
    The judge explains its reasoning and returns a score between 0 (poor) and 1 (perfect).
    """
    netlogo_judge = NetLogoJudge()
    result = netlogo_judge(original_pseudocode=original_pseudocode, netlogo_code=generated_netlogo)
    logging.info(f"Judge evaluation score: {result.score}")
    try:
        score = float(result.score)
    except Exception as e:
        logging.error(f"Error parsing judgement score: {str(e)}", exc_info=True)
        score = 0.0
    return score

def conversion_metric(prediction, reference, trace=None):
    """Returns an evaluation score between original and round-trip converted code using the LLM judge."""
    try:
        if isinstance(prediction, dspy.primitives.example.Example):
            ref_text = prediction.pseudocode
            gen_code = prediction.netlogo_code
        elif isinstance(reference, dspy.primitives.prediction.Prediction):
            ref_text = prediction.pseudocode
            gen_code = reference.netlogo_code
        else:
            return 0.0

        if not gen_code or not ref_text:
            return 0.0
            
        return verify_conversion(ref_text, gen_code)
    except Exception as e:
        logging.error(f"Error in conversion_metric: {str(e)}", exc_info=True)
        return 0.0

# -----------------------------------------------------------------------------
# Step 3: Create and optimize with training examples
# -----------------------------------------------------------------------------
# Existing training set of examples (as dictionaries)
training_set = [
    {
        "pseudocode": "For each turtle in the world, if the turtle sees food then the turtle picks up the food.",
        "netlogo": "ask turtles [ if any? food-here [ pickup-food ] ]"
    },
    {
        "pseudocode": "If a patch has a tree, then the tree drops a fruit onto the patch below.",
        "netlogo": ("ask patches [ if tree? [ let target one-of patches with [ pxcor = [pxcor] of myself "
                    "and pycor = [pycor] of myself - 1 ]; if target != nobody [ drop-fruit target ] ] ]")
    },
    {
        "pseudocode": "For each turtle, if its energy is below 50, then it seeks food.",
        "netlogo": "ask turtles [ if energy < 50 [ seek-food ] ]"
    },
    {
        "pseudocode": "For every turtle, if its x-coordinate is less than the maximum, move forward.",
        "netlogo": "ask turtles [ if xcor < max-pxcor [ forward 1 ] ]"
    },
    {
        "pseudocode": "For each turtle, if it sees another turtle within a radius of 2, then it follows it.",
        "netlogo": ("ask turtles [ "
                    "if any? turtles in-radius 2 [ "
                    "face one-of turtles in-radius 2 move-to one-of turtles in-radius 2 ] ]")
    },
    {
        "pseudocode": "For each patch, if there are no turtles on it, then change its color to green.",
        "netlogo": "ask patches [ if not any? turtles-here [ set pcolor green ] ]"
    },
    {
        "pseudocode": "For each turtle, if it is on a patch with food-dots, then it eats the food.",
        "netlogo": "ask turtles [ if any? food-dots-here [ eat-food ] ]"
    },
    {
        "pseudocode": "For each turtle, if it is on a patch with a tree, then it sets its 'sheltered' variable to true.",
        "netlogo": "ask turtles [ if [ tree? ] of patch-here [ set sheltered true ] ]"
    },
    {
        "pseudocode": "For every turtle, if its age is greater than 10, then it reproduces.",
        "netlogo": "ask turtles [ if age > 10 [ hatch 1 ] ]"
    },
    {
        "pseudocode": "For each patch, if it contains water, then spawn a fish.",
        "netlogo": "ask patches [ if water? [ sprout fishes 1 ] ]"
    },
    {
        "pseudocode": "For every turtle, if it detects a predator within a radius of 3, then it runs away.",
        "netlogo": "ask turtles [ if any? turtles with [ predator? ] in-radius 3 [ run-away ] ]"
    },
    {
        "pseudocode": "For each turtle, if its heading is 90 degrees (east), then it turns left by 45 degrees.",
        "netlogo": "ask turtles [ if heading = 90 [ left 45 ] ]"
    },
    {
        "pseudocode": "For each turtle, if it does not see any other turtles in a radius of 1, then it sings.",
        "netlogo": "ask turtles [ if not any? turtles in-radius 1 [ sing ] ]"
    },
    {
        "pseudocode": "For every turtle, if it is at the edge of the world, then it turns around.",
        "netlogo": ("ask turtles [ if xcor = max-pxcor or xcor = min-pxcor or "
                    "ycor = max-pycor or ycor = min-pycor [ rt 180 ] ]")
    },
    {
        "pseudocode": "For every turtle, if its energy is above 80, then it rests.",
        "netlogo": "ask turtles [ if energy > 80 [ set resting true ] ]"
    },
    {
        "pseudocode": "For each patch, if it is barren, then grow a tree on it.",
        "netlogo": "ask patches [ if not tree? [ sprout trees 1 ] ]"
    },
    {
        "pseudocode": "For each turtle, if it is not facing south, then it rotates until it does.",
        "netlogo": "ask turtles [ while [ heading != 180 ] [ right 10 ] ]"
    },
    {
        "pseudocode": "For every turtle, if it is on a patch with shade, then it hides.",
        "netlogo": "ask turtles [ if [ shaded? ] of patch-here [ hide ] ]"
    },
    {
        "pseudocode": "For each patch, if it contains both a tree and a rock, then mark the patch yellow.",
        "netlogo": ("ask patches [ if (any? turtles with [ breed = trees ]) and "
                    "(any? turtles with [ breed = rocks ]) [ set pcolor yellow ] ]")
    },
    {
        "pseudocode": "For each turtle, if it is carrying food and is on its home patch, then it drops the food.",
        "netlogo": "ask turtles [ if carrying-food and patch-here = home-patch [ drop-food ] ]"
    },
    {
        "pseudocode": "For each turtle, if it is the only turtle on its patch, then it dances.",
        "netlogo": "ask turtles [ if count turtles-here = 1 [ dance ] ]"
    },
    {
        "pseudocode": "For every turtle, if it detects a bright light, then it stops.",
        "netlogo": "ask turtles [ if bright-light? [ stop ] ]"
    }
]

# Append more challenging examples to the training set
challenging_examples = [
    {
        "pseudocode": (
            "For every turtle: If it is located on a patch that contains both a tree and a rock, "
            "and its energy is between 30 and 70, and it is facing north, then check all adjacent patches: "
            "if any patch contains food, move to the nearest food patch and then perform a left turn; "
            "otherwise, if there is water two patches ahead (provided the path is unobstructed by trees), "
            "move forward two patches and perform a right turn; if neither condition is met, remain stationary for one tick."
        ),
        "netlogo": (
            "ask turtles [\n"
            "  if ([tree?] of patch-here and [rock?] of patch-here) and (energy > 30 and energy < 70) and (heading = 0) [\n"
            "    if any? neighbors with [ food? ] [\n"
            "      let target min-one-of neighbors with [ food? ] [ distance myself ]\n"
            "      move-to target\n"
            "      left 45\n"
            "    ] else if (patch-at 0 2 != nobody and [water?] of patch-at 0 2 and not [tree?] of patch-at 0 1) [\n"
            "      forward 2\n"
            "      right 45\n"
            "    ]\n"
            "    ; else remain stationary\n"
            "  ]\n"
            "]"
        )
    },
    {
        "pseudocode": (
            "For each turtle: If its current patch is surrounded by patches where the sum of numeric values "
            "(each derived from the patch's pcolor converted to a number) exceeds 10, compute the average energy "
            "of turtles on those neighboring patches. If the turtle's energy is below that average and it is the only "
            "turtle on its patch, move towards the neighbor with the lowest energy; otherwise, randomly select a cardinal "
            "direction (0, 90, 180, or 270) and move, ensuring that its heading does not match the average heading of "
            "turtles within a radius of 3."
        ),
        "netlogo": (
            "ask turtles [\n"
            "  let nbrs neighbors\n"
            "  if (sum [ pcolor ] of nbrs) > 10 [\n"
            "    let avg-energy mean [ energy ] of turtles-on nbrs\n"
            "    if (energy < avg-energy and count turtles-here = 1) [\n"
            "      let target min-one-of nbrs with [ any? turtles ] [ distance myself ]\n"
            "      if target != nobody [ move-to target ]\n"
            "    ] else [\n"
            "      let cardinals [0 90 180 270]\n"
            "      let new-heading one-of cardinals\n"
            "      let avg-heading mean [ heading ] of turtles in-radius 3\n"
            "      if new-heading = avg-heading [ set new-heading (new-heading + 90) mod 360 ]\n"
            "      set heading new-heading\n"
            "      forward 1\n"
            "    ]\n"
            "  ]\n"
            "]"
        )
    },
    {
        "pseudocode": (
            "For every patch that is not on the world's boundary: If the patch contains at least one of the following: "
            "a tree, a rock, or water, then for every turtle on that patch that is carrying food and whose energy is below "
            "the global median, make the turtle drop its food, wait for 2 ticks, then signal all turtles within a radius of 1 "
            "to converge to that patch. If no such turtle exists, change the patch's pcolor to a gradient determined by "
            "the number of turtles present on that patch."
        ),
        "netlogo": (
            "ask patches [\n"
            "  if (pxcor != max-pxcor and pxcor != min-pxcor and pycor != max-pycor and pycor != min-pycor) [\n"
            "    if (tree? or rock? or water?) [\n"
            "      if any? turtles-here with [ carrying-food and energy < global-median ] [\n"
            "        ask turtles-here with [ carrying-food and energy < global-median ] [\n"
            "          drop-food\n"
            "          wait 2\n"
            "          ask turtles in-radius 1 [ move-to patch-here ]\n"
            "        ]\n"
            "      ] else [\n"
            "        let tcount count turtles-here\n"
            "        set pcolor scale-color blue tcount 0 10\n"
            "      ]\n"
            "    ]\n"
            "  ]\n"
            "]"
        )
    },
    {
        "pseudocode": (
            "For every turtle: If its age is even and its energy is less than (max_energy - min_energy) divided by the "
            "total number of turtles, then initiate a zigzag movement pattern by moving diagonally up-right, then diagonally "
            "down-right, and then upward; if a tree is encountered at any step, abort the sequence and perform a 180-degree turn. "
            "If the sequence completes without interruption, set the turtle's 'ambitious' flag to true."
        ),
        "netlogo": (
            "ask turtles [\n"
            "  if (age mod 2 = 0 and energy < ((max_energy - min_energy) / count turtles)) [\n"
            "    let interrupted false\n"
            "    if any? patches at (1, 1) with [ tree? ] [\n"
            "      set interrupted true\n"
            "    ] else [\n"
            "      move-to patch-at 1 1\n"
            "    ]\n"
            "    if not interrupted [\n"
            "      if any? patches at (1, -1) with [ tree? ] [\n"
            "         set interrupted true\n"
            "      ] else [\n"
            "         move-to patch-at 1 -1\n"
            "      ]\n"
            "    ]\n"
            "    if not interrupted [\n"
            "      if any? patches at (0, 1) with [ tree? ] [\n"
            "         set interrupted true\n"
            "      ] else [\n"
            "         forward 1\n"
            "      ]\n"
            "    ]\n"
            "    if interrupted [ rt 180 ]\n"
            "    else [ set ambitious true ]\n"
            "  ]\n"
            "]"
        )
    },
    {
        "pseudocode": (
            "For each turtle labeled 'leader': If it is on a yellow patch and its energy exceeds the average energy of all turtles, "
            "broadcast a 'follow' signal to every turtle within a radius of 4 so that they calculate the direction toward the leader and "
            "move exactly 1 patch toward it. If any turtle receives signals from multiple leaders with an energy difference greater than 20, "
            "it should ignore all signals and move randomly. Finally, if at least 3 turtles successfully follow the leader's signal, "
            "change the leader's patch pcolor to green."
        ),
        "netlogo": (
            "ask turtles with [ leader? ] [\n"
            "  if (pcolor = yellow and energy > mean [ energy ] of turtles) [\n"
            "    ask turtles in-radius 4 with [ not leader? ] [\n"
            "      face myself\n"
            "      forward 1\n"
            "      set following-leader who\n"
            "    ]\n"
            "  ]\n"
            "]\n"
            "ask turtles with [ not leader? ] [\n"
            "  let leaders turtles in-radius 4 with [ leader? ]\n"
            "  if (count leaders > 1) [\n"
            "    let energies map [ t -> [energy] of t ] leaders\n"
            "    if (max energies - min energies > 20) [\n"
            "      set following-leader nobody\n"
            "      rt random 360\n"
            "      forward 1\n"
            "    ]\n"
            "  ]\n"
            "]\n"
            "ask turtles with [ leader? ] [\n"
            "  if count turtles with [ following-leader = who ] >= 3 [\n"
            "     ask patch-here [ set pcolor green ]\n"
            "  ]\n"
            "]"
        )
    },
    {
        "pseudocode": (
            "For every turtle: If it detects a high density of turtles within a radius of 3 (more than half of the total turtles), "
            "record the current tick number. If 5 ticks have elapsed since the last recorded tick, move forward by 2 patches and then "
            "backtrack by 1 patch; otherwise, perform a random turn between 45 and 135 degrees. After the action, log the movement details."
        ),
        "netlogo": (
            "ask turtles [\n"
            "  if (count turtles in-radius 3 > (count turtles / 2)) [\n"
            "    if (ticks - last-dense-tick >= 5) [\n"
            "      forward 2\n"
            "      back 1\n"
            "      set last-dense-tick ticks\n"
            "    ] else [\n"
            "      rt (45 + random 91)\n"
            "    ]\n"
            "    show (word \"Turtle \" who \" action at tick \" ticks)\n"
            "  ]\n"
            "]"
        )
    }
]

# Append the challenging examples into the training set list
training_set += challenging_examples

# Finally, convert the dictionaries into Example objects.
training_set = [
    Example(
        pseudocode=ex["pseudocode"],
        netlogo_code=ex["netlogo"]
    ).with_inputs("pseudocode")
    for ex in training_set
]

# Quick Optimization Setup using MIPROv2 (Advanced) with minimal runs for fast iteration
#
# This configuration uses a very low number of trials and demos.
# See the advanced usage docs on MIPROv2:
# https://dspy.ai/deep-dive/optimizers/miprov2/?h=miprov2#optimizing-with-miprov2-advanced

quick_optimizer = MIPROv2(
    metric=conversion_metric,
    auto="light", # Can choose between light, medium, and heavy optimization runs
    verbose=True
)

quick_optimized_program = quick_optimizer.compile(
    convert_to_netlogo,        # Our conversion module
    trainset=training_set,       # The training set of examples
    max_bootstrapped_demos=3,
    max_labeled_demos=4,
    requires_permission_to_run=False,
)

def generate_netlogo(pseudocode_input: str) -> str:
    """Converts pseudocode to NetLogo code using the optimized module."""
    output = optimized_program(pseudocode=pseudocode_input)
    return output.netlogo_code

def generate_netlogo_quick(pseudocode_input: str) -> str:
    """Converts pseudocode to NetLogo code using the quickly optimized program for fast feedback."""
    output = quick_optimized_program(pseudocode=pseudocode_input)
    return output.netlogo_code

if __name__ == "__main__":
    sample_pseudocode = "For each turtle in the world, if the turtle sees food then the turtle picks up the food."
    netlogo_output = generate_netlogo_quick(sample_pseudocode)
    print(f"Input: {sample_pseudocode}")
    print(f"Output: {netlogo_output}")

    quick_optimized_program.save("optimized_program.json")

    # After a call to the optimized execution, you might try:
    print("Final prompt:", quick_optimized_program._prompt)