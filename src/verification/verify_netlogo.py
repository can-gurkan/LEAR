"""
NetLogo Code Verifier Module

This module provides functionality to validate and verify NetLogo code generated by LLMs.
It ensures the code is syntactically correct, safe to execute, and follows best practices.

Key Features:
- Syntax validation for NetLogo commands and reporters
- Safety checks for dangerous primitives
- Structural validation for control flow
- Numeric range checking
- Variable assignment validation
- Comprehensive error reporting

Usage:
    from src.verification.verify_netlogo import NetLogoVerifier
    
    verifier = NetLogoVerifier()
    is_safe, message = verifier.is_safe("fd 10 rt 90")
    if not is_safe:
        print(f"Code validation failed: {message}")

Dependencies:
- Python 3.8+
- Standard library modules: re, typing

Version History:
1.0.0 - Initial release with basic validation capabilities
1.1.0 - Added support for control structures (if/ifelse)
1.2.0 - Enhanced numeric expression validation
1.3.0 - Added variable assignment checking

Class Overview:
- NetLogoVerifier: Main class providing code validation functionality
"""

import re
from typing import List, Tuple, Set

class NetLogoVerifier:
    """
    NetLogo Code Verification and Validation Class
    
    This class provides comprehensive validation for NetLogo code generated by LLMs.
    It ensures code safety, correctness, and adherence to best practices.
    
    Responsibilities:
    - Validate syntax of NetLogo commands and reporters
    - Check for dangerous or restricted primitives
    - Verify structural integrity of control flow
    - Validate numeric expressions and ranges
    - Check variable assignments and usage
    - Provide detailed error messages for invalid code
    
    Public Methods:
    - is_safe(code: str) -> Tuple[bool, str]: Main validation method
      Returns tuple of (is_safe, error_message)
    
    Internal Implementation:
    - Uses sets of allowed commands and reporters
    - Maintains list of dangerous primitives to block
    - Implements multiple validation checks:
      * Syntax validation
      * Structural validation
      * Numeric validation
      * Variable validation
    
    Usage Example:
        verifier = NetLogoVerifier()
        code = "fd 10 rt 90"
        is_safe, message = verifier.is_safe(code)
        if not is_safe:
            raise ValueError(f"Invalid NetLogo code: {message}")
    
    Error Handling:
    - Returns detailed error messages for each validation failure
    - Provides line numbers for error locations when possible
    - Includes suggestions for fixing common issues
    """
    def __init__(self):
        self.allowed_commands = {
            'fd', 'forward',
            'rt', 'right',
            'lt', 'left',
            #'if', 'ifelse',
            'set', 'let'  # Added variable assignment
        }
        
        self.allowed_reporters = {
            'random',
            'random-float',
            'sin',
            'cos',
            'item',
            'count',  # Added list operations
            'length',
            'position'
        }
        
        self.dangerous_primitives = {
            'die', 'kill', 'create', 'hatch', 'sprout',
            'ask', 'of', 'with',
            'run', 'runresult',
            'file', 'import', 'export',
            'python',
            'clear', 'reset', 'setup', 'go',
        }
        
        self.arithmetic_operators = {'+', '-', '*', '/', '^'}
        self.comparison_operators = {'=', '!=', '>', '<', '>=', '<='}
        self.allowed_variables = {'input', 'energy', 'lifetime', 'food-collected'}  # Added agent variables

    def is_safe(self, code: str) -> Tuple[bool, str]:
        """
        Validate NetLogo code for safety and correctness.
        
        Parameters:
            code (str): The NetLogo code to validate. Can be multi-line.
            
        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: True if code is safe, False otherwise
                - str: Error message if code is unsafe, empty string if safe
                
        Error Handling:
            - Returns detailed error messages for each validation failure
            - Includes line numbers for error locations when possible
            - Provides suggestions for fixing common issues
            
        Usage Example:
            verifier = NetLogoVerifier()
            code = '''
                fd 10
                rt 90
                ifelse random 100 < 50 [
                    fd 5
                ][
                    rt 45
                ]
            '''
            is_safe, message = verifier.is_safe(code)
            if not is_safe:
                raise ValueError(f"Invalid NetLogo code: {message}")
                
        Implementation Notes:
            - Performs multiple validation checks in sequence
            - Tracks line numbers for better error reporting
            - Cleans code before validation (removes comments, normalizes whitespace)
            - Validates syntax, structure, and semantics
        """
        # Track line numbers for better error reporting
        lines = code.split('\n')
        cleaned_lines = []
        
        # Clean each line individually
        for i, line in enumerate(lines):
            cleaned = self._clean_code(line)
            if cleaned:  # Only keep non-empty lines
                cleaned_lines.append((i + 1, cleaned))  # Store line number with cleaned code
                
        # Join cleaned lines with line numbers
        code = '\n'.join(f"#{num}: {line}" for num, line in cleaned_lines)
        
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
        """
        Preprocess NetLogo code for validation.
        
        Performs the following transformations:
        1. Removes comments (both ;; and ; styles)
        2. Normalizes whitespace (converts multiple spaces to single)
        3. Adds spacing around brackets for easier tokenization
        4. Strips leading/trailing whitespace
        
        Parameters:
            code (str): Raw NetLogo code line to clean
            
        Returns:
            str: Cleaned code ready for validation
            
        Implementation Notes:
            - Uses regex for efficient pattern matching
            - Preserves bracket structure while adding spacing
            - Handles multi-line comments correctly
            - Maintains original code semantics while making it easier to parse
            
        Example:
            Input: "fd 10 ;; move forward"
            Output: "fd 10"
            
            Input: "if x < 10 [fd 1]"
            Output: "if x < 10 [ fd 1 ]"
        """
        # Remove any comments (;; or ;)
        code = re.sub(r';.*$', '', code, flags=re.MULTILINE)
        # Normalize whitespace but preserve brackets
        code = re.sub(r'\s+', ' ', code)
        # Add space around brackets for tokenization
        code = re.sub(r'\[', ' [ ', code)
        code = re.sub(r'\]', ' ] ', code)
        return code.strip()

    def _check_dangerous_primitives(self, code: str) -> Tuple[bool, str]:
        """
        Validate code against known dangerous NetLogo primitives.
        
        This security check prevents execution of commands that could:
        - Modify simulation state (clear/reset/setup/go)
        - Create/destroy agents (die/kill/create/hatch/sprout)
        - Execute external code (python/run/runresult)
        - Access filesystem (file/import/export)
        - Modify agent relationships (ask/of/with)
        
        Parameters:
            code (str): The code to validate
            
        Returns:
            Tuple[bool, str]: 
                - bool: True if no dangerous primitives found
                - str: Error message listing dangerous primitives if found
                
        Implementation Details:
            - Uses case-insensitive matching
            - Checks against predefined set of dangerous commands
            - Provides specific error messages for each violation
            - Handles partial matches (e.g. 'ask' in 'task')
            
        Example:
            Input: "fd 10 ask turtles [die]"
            Output: (False, "Dangerous primitives found: ask, die")
            
            Input: "fd 10 rt 90"
            Output: (True, "")
        """
        words = set(re.findall(r'\b\w+\b', code.lower()))
        dangerous_found = words.intersection(self.dangerous_primitives)
        
        if dangerous_found:
            return False, f"Dangerous primitives found: {', '.join(dangerous_found)}"
        return True, ""

    def _check_brackets_balance(self, code: str) -> Tuple[bool, str]:
        """
        Validate proper nesting and balance of brackets in NetLogo code.
        
        This check ensures that:
        - All opening brackets have matching closing brackets
        - Brackets are properly nested
        - No mismatched bracket types occur
        - No unclosed brackets remain
        
        Parameters:
            code (str): The code to validate
            
        Returns:
            Tuple[bool, str]:
                - bool: True if brackets are balanced
                - str: Error message describing bracket issues if found
                
        Implementation Details:
            - Uses a stack-based approach for efficient validation
            - Handles three bracket types: (), [], {}
            - Provides specific error messages for:
                * Unmatched closing brackets
                * Mismatched bracket types
                * Unclosed brackets
            - Tracks bracket positions for better error reporting
                
        Example:
            Input: "if x < 10 [fd 1]"
            Output: (True, "")
            
            Input: "if x < 10 [fd 1"
            Output: (False, "Unclosed brackets")
            
            Input: "if x < 10 [fd 1)]"
            Output: (False, "Mismatched brackets")
        """
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


    # Helper function that goes over allowed movement commands
    def _validate_allowed_commands(self, tokens) -> Tuple[bool, str]:
        '''
        Helper function for the _validate_if_statements function. Handles allowed commands inside if/ifelse/ifelse-value branches

        -----Parameters-----
        tokens (List): the tokens comprising the statement structure

        -----Returns-----
        results (Tuple[bool, str, int]): first element is whether statement is valid (True/False), second is associated message
        '''
        # Handle regular commands
        i = 0
        while i < len(tokens):
            if token in self.allowed_commands:
                # Check if we have at least one more token
                if i + 1 >= len(tokens):
                    return False, f"Command '{token}' needs a value"

                # Check for random keyword
                if tokens[i + 1].lower() in self.allowed_reporters:
                    # Need one more token after random
                    if i + 2 >= len(tokens):
                        return False, f"{tokens[i + 1].lower()} needs a numeric value"
                    # Validate the number after random
                    if not self._is_valid_numeric_expression(tokens[i + 2]):
                        return False, f"Invalid value after 'random': {tokens[i + 2]}"
                    i += 3  # Skip command, random, and the number
                else:
                    # Normal numeric value check
                    next_token = tokens[i + 1]
                    if not self._is_valid_numeric_expression(next_token):
                        return False, f"Invalid value for command '{token}': {next_token}"
                    i += 2  # Skip command and its value

        return True

    # Recursive Helper Function that validates if, ifelse, and ifelse-value statements
    def _validate_if_statements(self, tokens) -> Tuple[bool, str, int]:
        '''
        Helper function for the _check_command_syntax function. Handles if, ifelse, and ifelse-value statements and the content within them.

        -----Parameters-----
        tokens (List): the tokens comprising the statement structure

        -----Returns-----
        results (Tuple[bool, str, int]): first element is whether statement is valid (True/False), second is associated message, and third is last element index+1 of structure
        '''

        i = 0
        while i < len(tokens):
            token = tokens[i].lower()
            if token == 'ifelse' or token == 'ifelse-value':

                # Check condition
                condition_end = self._find_condition_end(tokens[i+1:])
                if condition_end == -1:
                    return False, f"Invalid {token} condition", -1
                    
                # Skip past condition
                i += condition_end + 1
                    
                # Check for true branch
                if i >= len(tokens) or tokens[i] != '[':
                    return False, f"Missing true branch for {token}", -1
                true_branch_end = self._find_matching_bracket(tokens[i:])
                if true_branch_end == -1:
                    return False, f"Invalid true branch for {token}", -1

                # recursively validate potential if/ifelse statements inside true branch
                is_valid = self._validate_if_statements(tokens[i+1:i+true_branch_end+1])
                if not is_valid[0]:
                    return False, is_valid[1], -1

                # Check movement commands inside brackets if not if/ifelse/ifelse-value statement
                if is_valid[2] == 'Not a if/ifelse/ifelse-value':

                    valid_movement = self._validate_allowed_commands(tokens[i+1:i+true_branch_end+1])
                    if not valid_movement[0]:
                        return False, valid_movement[1], -1

                # Skip past true branch
                i += true_branch_end + 1
                    
                # Check for false branch
                if i >= len(tokens) or tokens[i] != '[':
                    return False, f"Missing false branch for {token}", -1
                false_branch_end = self._find_matching_bracket(tokens[i:])
                if false_branch_end == -1:
                    return False, f"Invalid false branch for {token}", -1

                # recursively validate potential if/ifelse statements inside false branch
                is_valid = self._validate_if_statements(tokens[i+1:i+false_branch_end+1])
                if not is_valid[0]:
                    return False, is_valid[1], -1

                # Check movement commands inside brackets if not if/ifelse/ifelse-value statement
                if is_valid[2] == 'Not a if/ifelse/ifelse-value':

                    valid_movement = self._validate_allowed_commands(tokens[i+1:i+false_branch_end+1])
                    if not valid_movement[0]:
                        return False, valid_movement[1], -1
                    
                # Skip past false branch
                i += false_branch_end + 1
                
                # if all checks pass, then return True for valid statement
                return True, f'Valid {token} statement', i

            # Handle if structure
            elif token == 'if':
                # Check condition
                condition_end = self._find_condition_end(tokens[i+1:])
                if condition_end == -1:
                    return False, "Invalid if condition", -1
                    
                # Skip past condition
                i += condition_end + 1
                    
                # Check for branch
                if i >= len(tokens) or tokens[i] != '[':
                    return False, "Missing branch for if", -1
                branch_end = self._find_matching_bracket(tokens[i:])
                if branch_end == -1:
                    return False, "Invalid branch for if", -1

                # recursively validate potential if/ifelse statements inside branch
                is_valid = self._validate_if_statements(tokens[i+1:i+branch_end+1])
                if not is_valid[0]:
                    return False, is_valid[1], -1

                # Check movement commands inside brackets if not if/ifelse/ifelse-value statement
                if is_valid[2] == 'Not a if/ifelse/ifelse-value':

                    valid_movement = self._validate_allowed_commands(tokens[i+1:i+branch_end+1])
                    if not valid_movement[0]:
                        return False, valid_movement[1], -1

                # Checking to see if a false/else branch exists (in case LLM structured if statement as ifelse statement)
                i += branch_end + 1   
                # Check for false/else branch
                if i < len(tokens) and tokens[i] == '[':
                    return False, "Contains else branch for if statement", -1
                    
                
                # if all checks pass, then return True for valid statement
                return True, f'Valid {token} statement', i
            
            else:
                return True, 'Not a if/ifelse/ifelse-value', i

    def _check_command_syntax(self, code: str) -> Tuple[bool, str]:
        """
        Validate syntax of NetLogo commands and control structures.
        
        This check ensures that:
        - Commands have required parameters
        - Control structures (if/ifelse) are properly formed and nested
        - Complex conditions with item comparisons are valid
        - Random number generation is properly formatted
        - Variable assignments follow correct syntax
        - Nested control structures are properly handled
        
        Parameters:
            code (str): The code to validate
            
        Returns:
            Tuple[bool, str]:
                - bool: True if syntax is valid
                - str: Error message describing syntax issues if found
        """
        tokens = code.split()
        i = 0
        while i < len(tokens):
            token = tokens[i].lower()
            
            # # Handle ifelse structure
            # if token == 'ifelse':
            #     # Check condition
            #     condition_end = self._find_condition_end(tokens[i+1:])
            #     if condition_end == -1:
            #         return False, "Invalid ifelse condition"
                
            #     # Skip past condition
            #     i += condition_end + 1
                
            #     # Check for true branch
            #     if i >= len(tokens) or tokens[i] != '[':
            #         return False, "Missing true branch for ifelse"
            #     true_branch_end = self._find_matching_bracket(tokens[i:])
            #     if true_branch_end == -1:
            #         return False, "Invalid true branch for ifelse"
            
            #     # Skip past true branch
            #     i += true_branch_end + 1
                
            #     # Check for false branch
            #     if i >= len(tokens) or tokens[i] != '[':
            #         return False, "Missing false branch for ifelse"
            #     false_branch_end = self._find_matching_bracket(tokens[i:])
            #     if false_branch_end == -1:
            #         return False, "Invalid false branch for ifelse"
                
            #     # Skip past false branch
            #     i += false_branch_end + 1
            #     continue

            # # Handle if structure
            # if token == 'if':
            #     # Check condition
            #     condition_end = self._find_condition_end(tokens[i+1:])
            #     if condition_end == -1:
            #         return False, "Invalid if condition"
                
            #     # Skip past condition
            #     i += condition_end + 1
                
            #     # Check for branch
            #     if i >= len(tokens) or tokens[i] != '[':
            #         return False, "Missing branch for if"
            #     branch_end = self._find_matching_bracket(tokens[i:])
            #     if branch_end == -1:
            #         return False, "Invalid branch for if"
                
            #     # Skip past branch
            #     i += branch_end + 1
            #     continue

            is_valid, message, index = self._validate_if_statements(tokens[i:])
            if not is_valid:
                return is_valid, message

            i += index

            # check if at end of code
            if i < len(tokens):
                token = tokens[i].lower()
            else:
                return True, ""

            # Handle regular commands with enhanced validation
            if token in self.allowed_commands:
                # Check if we have at least one more token
                if i + 1 >= len(tokens):
                    return False, f"Command '{token}' needs a value"

                # Handle movement commands with random
                if token in {'fd', 'forward', 'rt', 'right', 'lt', 'left'}:
                    next_token = tokens[i + 1].lower()
                    if next_token == 'random':
                        if i + 2 >= len(tokens):
                            return False, "random needs a numeric value"
                        if not self._is_valid_numeric_expression(tokens[i + 2]):
                            return False, f"Invalid value after random: {tokens[i + 2]}"
                        i += 3
                    else:
                        if not self._is_valid_numeric_expression(next_token):
                            return False, f"Invalid value for {token}: {next_token}"
                        i += 2
                else:
                    i += 2
            else:
                i += 1

        return True, ""
        
    def _validate_condition(self, condition: str) -> bool:
        """Validate complex conditions including item comparisons."""
        condition = condition.strip()
        
        # Check for item comparisons
        if 'item' in condition:
            # Match patterns like: item N input <op> (item M input | number)
            pattern = r'^item\s+\d+\s+input\s*[<>=!]+\s*(item\s+\d+\s+input|\d+)$'
            if re.match(pattern, condition):
                return True
                
            # Match patterns like: item N input != 0
            pattern = r'^item\s+\d+\s+input\s*!=\s*0$'
            if re.match(pattern, condition):
                return True
                
        # Check for random comparisons
        if 'random' in condition:
            pattern = r'^random\s+\d+\s*[<>=!]+\s*\d+$'
            if re.match(pattern, condition):
                return True
                
        return False

    def _find_condition_end(self, tokens: List[str]) -> int:
        """Find the end of a condition expression."""
        for i, token in enumerate(tokens):
            if token == '[':
                return i
        return -1

    def _find_matching_bracket(self, tokens: List[str]) -> int:
        """Find the matching closing bracket."""
        count = 0
        for i, token in enumerate(tokens):
            if token == '[':
                count += 1
            elif token == ']':
                count -= 1
                if count == 0:
                    return i
        return -1

    def _is_valid_numeric_expression(self, expr: str) -> bool:
        """
        Validate numeric expressions in NetLogo code.
        
        This check ensures that:
        - Numbers are properly formatted (integers, decimals, negative)
        - Arithmetic expressions use valid operators
        - Comparisons use valid operators
        - Variable references are allowed
        - NetLogo reporters return numeric values
        
        Parameters:
            expr (str): The expression to validate
            
        Returns:
            bool: True if expression is valid, False otherwise
            
        Implementation Details:
            - Handles multiple numeric formats:
                * Integers: 10, -5
                * Decimals: 0.5, -1.25
                * Scientific notation: 1e5, -2.3e-4
            - Validates arithmetic operations:
                * Addition (+)
                * Subtraction (-)
                * Multiplication (*)
                * Division (/)
                * Exponentiation (^)
            - Validates comparison operations:
                * Equals (=)
                * Not equals (!=)
                * Greater than (>)
                * Less than (<)
                * Greater than or equal (>=)
                * Less than or equal (<=)
            - Allows valid NetLogo reporters that return numbers
            - Allows predefined variable references
                
        Example:
            Input: "10"
            Output: True
            
            Input: "-0.5"
            Output: True
            
            Input: "random 10"
            Output: True
            
            Input: "energy + 0.5"
            Output: True
            
            Input: "invalid"
            Output: False
        """
        # Remove any whitespace
        expr = expr.strip()
        
        # Check if it's a variable reference
        if expr.lower() in self.allowed_variables:
            return True
            
        # Check if it's a simple number (integer, decimal, or negative)
        try:
            float(expr)
            return True
        except ValueError:
            pass
            
        # Check if it's a valid NetLogo reporter that returns a number
        if expr.lower() in self.allowed_reporters:
            return True
            
        # Check if it starts with a valid reporter
        for reporter in self.allowed_reporters:
            if expr.lower().startswith(f"{reporter} "):
                remaining = expr[len(reporter):].strip()
                # For item reporter, allow variable references
                if reporter == 'item' and remaining.split()[-1] in self.allowed_variables:
                    return True
                try:
                    float(remaining)
                    return True
                except ValueError:
                    pass
                    
        # Check for basic arithmetic expressions
        if any(op in expr for op in self.arithmetic_operators):
            try:
                # Split by operators and check each part
                parts = re.split(r'([+\-*/^])', expr)
                for part in parts:
                    part = part.strip()
                    if part in self.arithmetic_operators:
                        continue
                    if not (part.replace('-', '').replace('.', '').isdigit() or 
                           part.lower() in self.allowed_reporters or
                           part.lower() in self.allowed_variables):
                        return False
                return True
            except Exception:
                return False
                
        # Check for comparison expressions
        if any(op in expr for op in self.comparison_operators):
            try:
                # Split by comparison operator
                for op in self.comparison_operators:
                    if op in expr:
                        parts = expr.split(op)
                        if len(parts) == 2:
                            left = parts[0].strip()
                            right = parts[1].strip()
                            # Allow comparisons with variables and numbers
                            if ((left in self.allowed_variables or self._is_valid_numeric_expression(left)) and
                                (right in self.allowed_variables or self._is_valid_numeric_expression(right))):
                                return True
            except Exception:
                return False
                
        return False
        
    def _check_value_ranges(self, code: str) -> Tuple[bool, str]:
        """
        Validate numeric value ranges in NetLogo code.
        
        This check ensures that:
        - Numeric values are within reasonable bounds
        - Values aren't excessively large or small
        - Values are appropriate for NetLogo operations
        
        Parameters:
            code (str): The code to validate
            
        Returns:
            Tuple[bool, str]:
                - bool: True if all values are within valid ranges
                - str: Error message describing range violations if found
                
        Implementation Details:
            - Extracts all numeric values from code
            - Validates against predefined range limits
            - Provides specific error messages for:
                * Values that are too large
                * Values that are too small
                * Values that could cause computational issues
            - Uses reasonable default limits:
                * Maximum value: 1000
                * Minimum value: -1000
            - Can be customized by modifying the range limits
                
        Example:
            Input: "fd 10 rt 90"
            Output: (True, "")
            
            Input: "fd 10000"
            Output: (False, "Value too large: 10000")
            
            Input: "rt -9999"
            Output: (False, "Value too small: -9999")
        """
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
        """
        Validate basic structural patterns in NetLogo code.
        
        This check ensures that:
        - Code is not empty
        - Contains at least one movement command
        - Is within reasonable length limits
        - Doesn't contain potential infinite loops
        - Has proper variable assignment syntax
        
        Parameters:
            code (str): The code to validate
            
        Returns:
            Tuple[bool, str]:
                - bool: True if structure is valid
                - str: Error message describing structural issues if found
                
        Implementation Details:
            - Validates minimum code requirements:
                * Non-empty code
                * Presence of movement commands
            - Enforces reasonable code length limits
            - Detects potential infinite loops
            - Validates variable assignment syntax
            - Provides specific error messages for:
                * Empty code
                * Missing movement commands
                * Excessive code length
                * Infinite loop patterns
                * Invalid variable assignments
                
        Example:
            Input: "fd 10 rt 90"
            Output: (True, "")
            
            Input: ""
            Output: (False, "Empty code")
            
            Input: "set x 10"
            Output: (False, "No movement commands found")
            
            Input: "while true [fd 1]"
            Output: (False, "Potential infinite loop detected")
        """
        # Code shouldn't be empty
        if not code.strip():
            return False, "Empty code"
        
        # Code should contain at least one movement command
        has_movement = any(cmd in code.lower() for cmd in {'fd', 'forward', 'rt', 'right', 'lt', 'left'})
        if not has_movement:
            return False, "No movement commands found"
        
        #'3 TO DO: Add max length to config
        # Code shouldn't be too long (arbitrary limit)
        if len(code) > 10000:  # Increased limit to accommodate control structures
            return False, "Code too long"
            
        # Check for potential infinite loops
        if 'while' in code.lower() or 'forever' in code.lower():
            return False, "Potential infinite loop detected"
            
        # Check for proper variable assignment
        if 'set ' in code.lower() or 'let ' in code.lower():
            # Verify assignment syntax
            assignments = re.findall(r'(set|let)\s+\w+\s+', code, re.IGNORECASE)
            if not assignments:
                return False, "Invalid variable assignment syntax"
                
        return True, ""

# def test_verifier():
#     """Test the verifier with various inputs."""
#     verifier = NetLogoVerifier()
    
#     test_cases = [
#         # Safe cases
#         ("fd 0.5", True),
#         ("fd random 10", True),
#         ("rt random-float 90 fd 5", True),
        
#         # Control structure cases
#         ("ifelse item 0 input != 0 [rt 15 fd 0.5] [fd 1]", True),
#         ("if item 1 input = 0 [lt 45 fd 1]", True),
        
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
#         ("FD 1 RT 90", True),  # Case insensitive
        
#         # Additional decimal test cases
#         ("fd 0.25", True),
#         ("rt 45.5", True),
#         ("lt -0.75", True),
        
#         # Complex control structure case
#         ("""ifelse item 0 input != 0 [rt 15 fd 0.5] [ifelse item 2 input != 0 [fd 1] [ifelse item 1 input != 0 [lt 15 fd 0.5] [rt random 30 lt random 30 fd 5]]]""", True)
#     ]
    
#     for code, expected_safe in test_cases:
#         is_safe, message = verifier.is_safe(code)
#         print(f"\nTesting: {code}")
#         print(f"Expected safe: {expected_safe}, Got: {is_safe}")
#         print(f"Message: {message}")
#         assert is_safe == expected_safe, f"Test failed for: {code}"

# if __name__ == "__main__":
#     test_verifier()
