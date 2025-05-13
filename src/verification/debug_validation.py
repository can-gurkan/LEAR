from verify_netlogo import NetLogoVerifier
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def debug_validation():
    v = NetLogoVerifier()
    
    # Test with xcor in condition
    code1 = 'ifelse xcor = 0 [fd 1] [fd 2]'
    print(f"Testing code1: {code1}")
    
    tokens = list(v._tokenize(code1))
    print("Tokens:", [(t.type, t.value) for t in tokens])
    
    result = v.validate(code1)
    print(f"Validation result: {result.is_valid}")
    for error in result.errors:
        print(f"Error: {error}")

    # Try with a reporter we know works
    code2 = 'ifelse random 10 > 5 [fd 1] [fd 2]'
    print(f"\nTesting code2: {code2}")
    
    tokens = list(v._tokenize(code2))
    print("Tokens:", [(t.type, t.value) for t in tokens])
    
    result = v.validate(code2)
    print(f"Validation result: {result.is_valid}")
    for error in result.errors:
        print(f"Error: {error}")

# Add debugging for the core issue with xcor in the broken test case
def debug_test_case58():
    v = NetLogoVerifier()
    
    test_code = """
ifelse weight > 10 [
  ifelse xcor = 0 and ycor = 0 [
    rt random 20 lt random 20 fd 1
  ][
    lt towards [0 0] fd 1
  ]
][
  (ifelse item 0 input-resource-distances < item 1 input-resource-distances and item 0 input-resource-distances < item 2 input-resource-distances [
    lt 20 fd 1
  ] item 1 input-resource-distances < item 0 input-resource-distances and item 1 input-resource-distances < item 2 input-resource-distances [
    rt 20 fd 1
  ] [
    fd 1
  ])
]
"""
    
    print(f"Testing the problematic test case (simplified):")
    test_xcor = """
ifelse weight > 10 [
  ifelse xcor = 0 [
    fd 1
  ][
    fd 2
  ]
][ 
  fd 3
]
"""
    
    result = v.validate(test_xcor)
    print(f"Validation result: {result.is_valid}")
    for error in result.errors:
        print(f"Error: {error}")

if __name__ == "__main__":
    debug_validation()
    debug_test_case58() 