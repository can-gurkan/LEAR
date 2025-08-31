import re

# Allowed parameters
LEFT_ALLOWED    = {15, 30, 45, 90}
RIGHT_ALLOWED   = {15, 30, 45, 90}
FORWARD_ALLOWED = {1, 4, 7}

def verify_movement_logic(code: str) -> bool:
    """
    Parse every `left`, `lt`, `right`, `rt`, `forward`, `fd` in the code and
    ensure that:
      - every left/lt argument is one of 15,30,45,90
      - every right/rt argument is one of 15,30,45,90
      - every forward/fd argument is one of 1,4,7

    Returns True iff no invalid parameters are found.
    """
    cleaned = clean_code(strip_final_block(code))
    commands = extract_commands(cleaned)

    for direction, value in commands:
        if direction == 'left' and value not in LEFT_ALLOWED:
            print(f"Invalid left angle: {value}")
            return False
        if direction == 'right' and value not in RIGHT_ALLOWED:
            print(f"Invalid right angle: {value}")
            return False
        if direction == 'forward' and value not in FORWARD_ALLOWED:
            print(f"Invalid forward step: {value}")
            return False

    return True


def clean_code(code: str) -> str:
    """Strip NetLogo comments and collapse whitespace."""
    lines = []
    for line in code.split('\n'):
        if ';' in line:
            line = line[:line.index(';')]
        lines.append(line.strip())
    joined = ' '.join(lines)
    return re.sub(r'\s+', ' ', joined).strip()


def extract_commands(cleaned: str) -> list[tuple[str,int]]:
    """
    Find all (lt|left|rt|right|fd|forward) <N> pairs,
    reject zero-padded N, and normalize to (direction, int(N)).
    """
    pattern = r'\b(lt|left|rt|right|fd|forward)\s+(\d+)\b'
    matches = re.findall(pattern, cleaned, flags=re.IGNORECASE)
    result = []

    for tok, numstr in matches:
        # skip zero-padded like "015"
        if len(numstr) > 1 and numstr.startswith('0'):
            continue
        n = int(numstr)
        t = tok.lower()
        if t in ('lt', 'left'):
            result.append(('left', n))
        elif t in ('rt', 'right'):
            result.append(('right', n))
        elif t in ('fd', 'forward'):
            result.append(('forward', n))

    return result

def strip_final_block(code: str) -> str:
    """
    Remove the very last bracketed block [...]
    so none of its commands will be extracted.
    """

    start = code.rfind('[')
    if start == -1:
        return code
    
    depth = 0
    for i in range(start, len(code)):
        if code[i] == '[':
            depth += 1
        elif code[i] == ']':
            depth -= 1
            if depth == 0:
                return code[:start] + code[i+1:]
    return code
