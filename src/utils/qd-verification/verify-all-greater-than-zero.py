import re

# Import the variables list from verify-variables-present.py
def get_energy_variables():
    """Extract the energy variables from verify-variables-present.py function."""
    # Read the verify-variables-present.py file to extract variables
    try:
        with open('verify-variables-present.py', 'r') as f:
            content = f.read()
            
        # Extract variables from the verify_variables_present function
        variables = []
        lines = content.split('\n')
        for line in lines:
            if 'energy-' in line and 'in code' in line:
                # Extract variable name between quotes
                import re
                matches = re.findall(r'"(energy-[^"]+)"', line)
                variables.extend(matches)
        
        return variables
    except:
        # Fallback to hardcoded list if file reading fails
        return [
            "energy-ahead-close", "energy-left-close", "energy-right-close",
            "energy-ahead-medium", "energy-left-medium", "energy-right-medium", 
            "energy-ahead-far", "energy-left-far", "energy-right-far"
        ]

# The nine energy variables that must all be checked for > 0
ENERGY_VARIABLES = get_energy_variables()

def verify_all_greater_than_zero(code):
    """
    Verify that all nine energy variables are checked for being greater than zero.
    Handles both nested ifelse and switch-style (ifelse ...) syntax.
    
    Returns True if all variables are properly verified > 0, False otherwise.
    """
    # Clean the code - remove comments and normalize whitespace
    cleaned_code = clean_code(code)
    
    # Track which variables have been verified to be > 0
    verified_variables = set()
    
    # Parse the code to extract conditions and track variable verification
    parse_conditions(cleaned_code, verified_variables)
    
    # Debug output (uncomment to see what variables were found)
    # print(f"Verified variables: {sorted(verified_variables)}")
    # print(f"Missing variables: {set(ENERGY_VARIABLES) - verified_variables}")
    
    # Check if all nine variables are verified
    return len(verified_variables) == len(ENERGY_VARIABLES) and all(var in verified_variables for var in ENERGY_VARIABLES)

def clean_code(code):
    """Clean and normalize the code for parsing."""
    # Remove comments (lines starting with ;)
    lines = []
    for line in code.split('\n'):
        # Remove inline comments
        if ';' in line:
            line = line[:line.index(';')]
        lines.append(line.strip())
    
    # Join back and normalize whitespace
    cleaned = ' '.join(lines)
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def parse_conditions(code, verified_variables):
    """Parse the code to extract and analyze conditions."""
    # Find all condition expressions within ifelse statements
    conditions = extract_conditions(code)
    
    # Debug: print(f"Extracted conditions: {conditions}")
    print(f"Extracted conditions: {conditions}")
    
    for condition in conditions:
        analyze_condition(condition, verified_variables)

def extract_conditions(code):
    """Extract condition expressions from ifelse statements."""
    conditions = []
    
    # Check if this is switch-style (contains parenthesized ifelse)
    if '(ifelse' in code:
        # Extract the content between (ifelse ... )
        start_idx = code.find('(ifelse')
        if start_idx != -1:
            # Find the matching closing parenthesis
            paren_count = 0
            end_idx = start_idx
            for i in range(start_idx, len(code)):
                if code[i] == '(':
                    paren_count += 1
                elif code[i] == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        end_idx = i
                        break
            
            if end_idx > start_idx:
                switch_content = code[start_idx+7:end_idx]  # Skip "(ifelse"
                conditions.extend(extract_switch_conditions(switch_content))
    else:
        # Handle nested ifelse
        conditions.extend(extract_nested_conditions(code))
    
    return conditions

def extract_switch_conditions(content):
    """Extract conditions from switch-style ifelse."""
    conditions = []
    
    # Split by brackets to separate condition-action pairs
    # Remove leading/trailing whitespace
    content = content.strip()
    
    # Use a simple state machine to parse conditions
    current_condition = ""
    bracket_depth = 0
    in_condition = True
    
    i = 0
    while i < len(content):
        char = content[i]
        
        if char == '[':
            if bracket_depth == 0 and in_condition:
                # End of condition, start of action
                if current_condition.strip():
                    cleaned = current_condition.strip()
                    # Remove parentheses
                    cleaned = re.sub(r'^\(+', '', cleaned)
                    cleaned = re.sub(r'\)+$', '', cleaned)
                    if 'energy-' in cleaned:
                        conditions.append(cleaned)
                current_condition = ""
                in_condition = False
            bracket_depth += 1
        elif char == ']':
            bracket_depth -= 1
            if bracket_depth == 0:
                # End of action, next thing should be a condition
                in_condition = True
        elif in_condition:
            current_condition += char
        
        i += 1
    
    # Handle any remaining condition
    if current_condition.strip() and in_condition:
        cleaned = current_condition.strip()
        cleaned = re.sub(r'^\(+', '', cleaned)
        cleaned = re.sub(r'\)+$', '', cleaned)
        if 'energy-' in cleaned:
            conditions.append(cleaned)
    
    return conditions

def extract_nested_conditions(code):
    """Extract conditions from nested ifelse statements."""
    conditions = []
    
    # Use regex to find ifelse patterns
    pattern = r'ifelse\s+([^[\]]+?)\s*\['
    matches = re.finditer(pattern, code)
    
    for match in matches:
        condition = match.group(1).strip()
        if condition:
            conditions.append(condition)
    
    return conditions

def analyze_condition(condition, verified_variables):
    """Analyze a single condition to determine which variables are verified > 0."""
    # Check for invalid comparisons (> 1, > 2, etc.) first
    invalid_pattern = r'(energy-[a-z-]+)\s*>\s*([1-9]\d*)'
    if re.search(invalid_pattern, condition):
        # If we find any variable compared to > 1 or higher, this invalidates the whole thing
        return
    
    # Check for direct > 0 comparisons
    gt_zero_pattern = r'(energy-[a-z-]+)\s*>\s*0'
    matches = re.finditer(gt_zero_pattern, condition)
    
    newly_verified = set()
    for match in matches:
        var = match.group(1)
        if var in ENERGY_VARIABLES:
            verified_variables.add(var)
            newly_verified.add(var)
    
    # Now check for >= or > comparisons between variables
    # We need to do this iteratively since dependencies can chain
    # Keep going until no new variables are added
    changed = True
    while changed:
        changed = False
        comparison_pattern = r'(energy-[a-z-]+)\s*(>=?)\s*(energy-[a-z-]+)'
        comp_matches = re.finditer(comparison_pattern, condition)
        
        for comp_match in comp_matches:
            var_a = comp_match.group(1)
            operator = comp_match.group(2)
            var_b = comp_match.group(3)
            
            # If var_b is already verified > 0, and var_a >= var_b or var_a > var_b,
            # then var_a is also implicitly > 0
            if (var_b in verified_variables and 
                var_a in ENERGY_VARIABLES and 
                var_a not in verified_variables):
                verified_variables.add(var_a)
                newly_verified.add(var_a)
                changed = True