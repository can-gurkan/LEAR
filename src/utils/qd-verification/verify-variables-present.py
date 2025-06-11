def verify_variables_present(code):
    return ("energy-ahead-close" in code and
            "energy-left-close" in code and
            "energy-right-close" in code and
            "energy-ahead-medium" in code and
            "energy-left-medium" in code and
            "energy-right-medium" in code and
            "energy-ahead-far" in code and
            "energy-left-far" in code and
            "energy-right-far" in code)