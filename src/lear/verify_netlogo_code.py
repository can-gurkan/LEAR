import re
from typing import List, Tuple, Set

class NetLogoVerifier:
    def __init__(self):
        self.allowed_commands = {
            'fd', 'forward',
            'rt', 'right',
            'lt', 'left'
        }
        
        self.allowed_reporters = {
            'random',
            'random-float',
            'sin',
            'cos'
        }
        
        self.dangerous_primitives = {
            'die', 'kill', 'create', 'hatch', 'sprout',
            'ask', 'of', 'with',
            'set', 'let',
            'run', 'runresult',
            'file', 'import', 'export',
            'python',
            'clear', 'reset', 'setup', 'go'
        }
        
        self.arithmetic_operators = {'+', '-', '*', '/', '^'}

    def is_safe(self, code: str) -> Tuple[bool, str]:
        """
        Check if the NetLogo code is safe to run.
        Returns (is_safe, error_message).
        """
        # Remove comments and extra whitespace
        code = self._clean_code(code)
        
        # Basic safety checks
        checks = [
            self._check_dangerous_primitives,
            self._check_brackets_balance,
            self._check_command_syntax,
            self._check_value_ranges,
            self._check_basic_structure
        ]
        
        for check in checks:
            is_safe, message = check(code)
            if not is_safe:
                return False, message
        
        return True, "Code appears safe"

    def _clean_code(self, code: str) -> str:
        """Remove comments and normalize whitespace."""
        # Remove any comments (;; or ;)
        code = re.sub(r';.*$', '', code, flags=re.MULTILINE)
        # Normalize whitespace
        return ' '.join(code.split())

    def _check_dangerous_primitives(self, code: str) -> Tuple[bool, str]:
        """Check for presence of dangerous primitives."""
        words = set(re.findall(r'\b\w+\b', code.lower()))
        dangerous_found = words.intersection(self.dangerous_primitives)
        
        if dangerous_found:
            return False, f"Dangerous primitives found: {', '.join(dangerous_found)}"
        return True, ""

    def _check_brackets_balance(self, code: str) -> Tuple[bool, str]:
        """Verify that brackets and parentheses are balanced."""
        stack = []
        brackets = {'(': ')', '[': ']', '{': '}'}
        
        for char in code:
            if char in brackets.keys():
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    return False, "Unmatched closing bracket"
                if char != brackets[stack.pop()]:
                    return False, "Mismatched brackets"
        
        if stack:
            return False, "Unclosed brackets"
        return True, ""

    def _check_command_syntax(self, code: str) -> Tuple[bool, str]:
        """Check if commands are properly formed."""
        tokens = code.split()
        i = 0
        
        while i < len(tokens):
            token = tokens[i].lower()
            
            # Check if token is a command
            if token in self.allowed_commands:
                # Commands should be followed by a numeric value or expression
                if i + 1 >= len(tokens):
                    return False, f"Command '{token}' needs a value"
                
                # Basic check for numeric value or expression
                next_token = tokens[i + 1]
                if not self._is_valid_numeric_expression(next_token) and not next_token.lower() in ['random', 'random-float']:
                    return False, f"Invalid value for command '{token}': {next_token}"
                i += 2
            else:
                i += 1
        
        return True, ""

    def _is_valid_numeric_expression(self, expr: str) -> bool:
        """Check if expression is a valid numeric value or calculation."""
        try:
            # Try to evaluate as a number
            float(expr)
            return True
        except ValueError:
            # Check if it's a valid reporter or expression
            # This is a simplified check - could be made more robust
            valid_chars = set('0123456789.+-*/() ')
            valid_chars.update(self.allowed_reporters)
            return all(c in valid_chars for c in expr)

    def _check_value_ranges(self, code: str) -> Tuple[bool, str]:
        """Check if numeric values are within reasonable ranges."""
        # Extract numeric values
        numbers = re.findall(r'\b\d+\.?\d*\b', code)
        
        for num in numbers:
            value = float(num)
            # Arbitrary limits - adjust as needed
            if value > 1000:
                return False, f"Value too large: {value}"
            if value < -1000:
                return False, f"Value too small: {value}"
        
        return True, ""

    def _check_basic_structure(self, code: str) -> Tuple[bool, str]:
        """Check basic code structure and patterns."""
        # Code shouldn't be empty
        if not code.strip():
            return False, "Empty code"
        
        # Code should contain at least one movement command
        has_movement = any(cmd in code.lower() for cmd in self.allowed_commands)
        if not has_movement:
            return False, "No movement commands found"
        
        # Code shouldn't be too long (arbitrary limit)
        if len(code) > 500:
            return False, "Code too long"
            
        return True, ""

# def test_verifier():
#     """Test the verifier with various inputs."""
#     verifier = NetLogoVerifier()
    
#     test_cases = [
#         # Safe cases
#         ("fd 1 rt 90 lt 45", True),
#         ("fd random 10", True),
#         ("rt random-float 90 fd 5", True),
        
#         # Unsafe cases
#         ("ask neighbors [fd 1]", False),
#         ("fd 1 die", False),
#         ("rt 90 python:run", False),
#         ("fd (1", False),
#         ("fd -9999", False),
#         ("", False),
        
#         # Edge cases
#         ("fd 1 + 2", True),
#         ("rt random 360 * 0.5", True),
#         ("FD 1 RT 90", True)  # Case insensitive
#     ]
    
#     for code, expected_safe in test_cases:
#         is_safe, message = verifier.is_safe(code)
#         print(f"\nTesting: {code}")
#         print(f"Expected safe: {expected_safe}, Got: {is_safe}")
#         print(f"Message: {message}")
#         assert is_safe == expected_safe, f"Test failed for: {code}"

# if __name__ == "__main__":
#     test_verifier()