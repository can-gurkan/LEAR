import instructor
import os
from pydantic import BaseModel
from groq import Groq

api_key = "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"

class NLogoCode(BaseModel):
    new_code: str

def mutate_code(code_str):
    print(code_str)
    client = instructor.from_groq(Groq(api_key=api_key), mode=instructor.Mode.JSON)

    new_code = client.chat.completions.create(
        model="mixtral-8x7b-32768",#"llama-3.1-70b-versatile",
        response_model=NLogoCode,
        messages=[
            #{"role": "system", "content": "Modify the given NetLogo code and output new code."},
            #{"role": "user", "content": code_str},
            {
            "role": "user",
            "content": "Improve the given NetLogo code: "+code_str}
        ],
        temperature=0.65,
    )

    print(new_code.new_code)
    return new_code.new_code

if __name__ == "__main__":
    mutate_code("lt random 20 fd 1")