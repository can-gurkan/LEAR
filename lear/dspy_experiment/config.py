import dspy
import os

lm = dspy.LM(
    model="groq/llama3-70b-8192", api_key=os.getenv("GROQ_API_KEY"), temperature=0.65
)

dspy.configure(lm=lm)
