from verify_movement_params import verify_movement_logic

test_cases = [
    # 0: all full commands with valid params → True
    ("left 15 right 30 forward 7", True),

    # 1: all abbreviations with valid params → True
    ("lt 45 rt 90 fd 4", True),

    # 2: invalid left angle (20 not allowed) → False
    ("left 20", False),

    # 3: invalid right angle (100 not allowed) → False
    ("rt 100", False),

    # 4: invalid forward step (2 not allowed) → False
    ("forward 2", False),

    # 5: mix valid & invalid (forward 9 invalid) → False
    ("lt 30 fd 1 right 45 forward 9", False),

    # 6: no movement commands → True
    ("", True),

    # 7: only commented‐out invalid commands → True
    ("; left 20\n; forward 2", True),

    # 8: zero‐padded commands are skipped → True
    ("left 015 rt 030 fd 007", True),

    # 9: commands inside punctuation, all valid → True
    ("(left 15) [rt 90] {fd 4}", True),

    ("""; Strategic movement based on energy sensing at multiple distances
    (ifelse
    ; Prioritize high positive energy patches
    (energy-ahead-close > 0 and energy-ahead-close >= energy-left-close and energy-ahead-close >= energy-right-close)
    [ fd 1 ]
    ; If ahead is not optimal, check left side for positive energy
    (energy-left-close > 0 and energy-left-close >= energy-right-close)
    [ lt 90 fd 1 ]
    ; If right side has best energy, move right
    (energy-right-close > 0)
    [ rt 90 fd 1 ]
    ; Medium distance energy sensing as fallback
    (energy-ahead-medium > 0)
    [ fd 4 ]
    ; Far distance energy sensing as last resort
    (energy-ahead-far > 0)
    [ fd 7 ]
    ; If no positive energy detected, add some randomness to exploration
    [
        lt random 45
        rt random 45
        fd 1
    ]
    )""", True), 

    ("""; Advanced energy-seeking movement strategy with multi-level sensing and adaptive decision-making
    (ifelse
    (energy-ahead-close > 0 and energy-ahead-close >= energy-left-close and energy-ahead-close >= energy-right-close)
    [ fd 1 ]
    (energy-left-close > 0 and energy-left-close > energy-ahead-close and energy-left-close > energy-right-close)
    [ lt 90 fd 1 ]
    (energy-right-close > 0 and energy-right-close > energy-ahead-close and energy-right-close > energy-left-close)
    [ rt 90 fd 1 ]
    (energy-ahead-medium > energy-left-medium and energy-ahead-medium > energy-right-medium)
    [ ifelse energy-ahead-medium > 2 [ fd 4 ] [ fd 2 ] ]
    (energy-left-medium > energy-ahead-medium and energy-left-medium > energy-right-medium)
    [ lt 90 ifelse energy-left-medium > 2 [ fd 4 ] [ fd 2 ] ]
    (energy-right-medium > energy-ahead-medium and energy-right-medium > energy-left-medium)
    [ rt 90 ifelse energy-right-medium > 2 [ fd 4 ] [ fd 2 ] ]
    (energy-ahead-far > 0 and energy-ahead-far >= energy-left-far and energy-ahead-far >= energy-right-far)
    [ ifelse energy-ahead-far > 5 [ fd 7 ] [ fd 3 ] ]
    (energy-left-far > 0 and energy-left-far > energy-ahead-far and energy-left-far > energy-right-far)
    [ lt 90 ifelse energy-left-far > 5 [ fd 7 ] [ fd 3 ] ]
    (energy-right-far > 0 and energy-right-far > energy-ahead-far and energy-right-far > energy-left-far)
    [ rt 90 ifelse energy-right-far > 5 [ fd 7 ] [ fd 3 ] ]
    [ rt (random 90 - 45) fd 1 ]
    )""", False)


]

def run_tests():
    """Run tests for verify_movement_logic parameter validation."""
    print("Comprehensive Test Suite for Movement Parameter Validation")
    print("=" * 80)
    
    all_passed = True
    for i, (code, expected) in enumerate(test_cases):
        result = verify_movement_logic(code)
        passed = (result == expected)
        status = "✓ PASS" if passed else "✗ FAIL"
        
        print(f"Test {i:2}: {status} | Expected: {expected} | Got: {result}")
        if not passed:
            snippet = code.replace("\n", " ")
            print(f"        Snippet: {snippet[:60]}...")
            all_passed = False
        print()
    
    print("=" * 80)
    if all_passed:
        print("🎉 All tests PASSED!")
    else:
        print("❌ Some tests FAILED.")
    return all_passed

if __name__ == "__main__":
    run_tests()
