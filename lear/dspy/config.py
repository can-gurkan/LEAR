import dspy
import os

lm = dspy.LM(model='groq/llama3-70b-8192', api_key=os.getenv('GROQ_API_KEY'),
            system_prompt="You are an expert in evolving NetLogo agent behaviors. Focus on creating efficient, survival-optimized netlogo code.",
            temperature=0.65)

dspy.configure(lm=lm)
