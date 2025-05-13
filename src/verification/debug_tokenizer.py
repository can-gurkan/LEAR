from verify_netlogo import NetLogoVerifier
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create a debug tokenizer function
def debug_tokenize(code):
    v = NetLogoVerifier()
    print('Tokens:')
    for token in v._tokenize(code):
        print(f'{token.type}: {token.value} (Line {token.line}, Col {token.column})')

# Test with xcor
code = 'ifelse xcor = 0 [fd 1] [fd 2]'
print('Testing code:', code)
debug_tokenize(code)

# Test with a reporter from the official list
code2 = 'ifelse random 10 > 5 [fd 1] [fd 2]'
print('\nTesting code:', code2)
debug_tokenize(code2) 