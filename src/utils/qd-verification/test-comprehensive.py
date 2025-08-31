from verification_framework import create_verification_framework
import os

# All test cases from the user's test suite
test_cases = [
    # Test 0 - canonical nested ifelse (should be True)
    '''ifelse energy-ahead-close > 0
[ fd 1 ]
[
  ifelse energy-left-close > 0
  [ lt 90 fd 1 ]
  [
    ifelse energy-right-close > 0
    [ rt 90 fd 1 ]
    [
      ifelse energy-ahead-medium > 0
      [ fd 4 ]
      [
        ifelse energy-left-medium > 0
        [ lt 90 fd 4 ]
        [
          ifelse energy-right-medium > 0
          [ rt 90 fd 4 ]
          [
            ifelse energy-ahead-far > 0
            [ fd 7 ]
            [
              ifelse energy-left-far > 0
              [ lt 90 fd 7 ]
              [
                ifelse energy-right-far > 0
                [ rt 90 fd 7 ]
                [
                  rt random-float 45
                  lt random-float 45
                  fd 1
                ]
              ]
            ]
          ]
        ]
      ]
    ]
  ]
]''',

    # Test 1 - incomplete switch style (should be False - missing medium and far left/right)
    '''; Strategic movement based on energy sensing at multiple distances
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
)''',

    # Test 2 - complete switch style (should be True)
    '''; Intelligent energy-seeking movement strategy with multi-level sensing and adaptive behavior
(ifelse
  ; Prioritize close-range high-energy positive patches with multi-directional sensing
  energy-ahead-close > 0 and energy-ahead-close >= energy-left-close and energy-ahead-close >= energy-right-close
  [ fd 1 ]

  energy-left-close > 0 and energy-left-close > energy-ahead-close and energy-left-close > energy-right-close
  [ lt 90 fd 1 ]

  energy-right-close > 0 and energy-right-close > energy-ahead-close and energy-right-close > energy-left-close
  [ rt 90 fd 1 ]

  ; Secondary priority: medium-range energy detection with longer movement
  energy-ahead-medium > 0 and energy-ahead-medium >= energy-left-medium and energy-ahead-medium >= energy-right-medium
  [ fd 4 ]

  energy-left-medium > 0 and energy-left-medium > energy-ahead-medium and energy-left-medium > energy-right-medium
  [ lt 90 fd 4 ]

  energy-right-medium > 0 and energy-right-medium > energy-ahead-medium and energy-right-medium > energy-left-medium
  [ rt 90 fd 4 ]

  ; Tertiary priority: far-range energy exploration
  energy-ahead-far > 0 and energy-ahead-far >= energy-left-far and energy-ahead-far >= energy-right-far
  [ fd 7 ]

  energy-left-far > 0 and energy-left-far > energy-ahead-far and energy-left-far > energy-right-far
  [ lt 90 fd 7 ]

  energy-right-far > 0 and energy-right-far > energy-ahead-far and energy-right-far > energy-left-far
  [ rt 90 fd 7 ]

  ; Fallback random exploration to prevent stagnation
  [
    ; Weighted random turn to maintain some directional consistency
    rt random-float 90
    fd 1
  ]
)''',

    # Test 3 - missing far variables (should be False)
    '''ifelse
  energy-ahead-close > 0 and energy-ahead-close > energy-left-close and energy-ahead-close > energy-right-close
  [ fd 1 ]

  [ ifelse
    energy-left-close > 0 and energy-left-close > energy-ahead-close and energy-left-close > energy-right-close
    [ lt 90 fd 1 ]

    [ ifelse
      energy-right-close > 0 and energy-right-close > energy-ahead-close and energy-right-close > energy-left-close
      [ rt 90 fd 1 ]

      [ ifelse
        energy-ahead-medium > 0 and energy-ahead-medium > energy-left-medium and energy-ahead-medium > energy-right-medium
        [ fd 4 ]

        [ ifelse
          energy-left-medium > 0 and energy-left-medium > energy-ahead-medium and energy-left-medium > energy-right-medium
          [ lt 90 fd 4 ]

          [ ifelse
            energy-right-medium > 0 and energy-right-medium > energy-ahead-medium and energy-right-medium > energy-left-medium
            [ rt 90 fd 4 ]

            [ rt random 20 lt random 20 fd 1 ]
          ]
        ]
      ]
    ]
  ]''',

    # Test 4 - only close variables (should be False)
    '''(ifelse
  energy-ahead-close > 0 and energy-ahead-close >= energy-left-close and energy-ahead-close >= energy-right-close
  [ fd 1 ]

  energy-left-close > 0 and energy-left-close > energy-ahead-close and energy-left-close > energy-right-close
  [ lt 90 fd 1 ]

  energy-right-close > 0 and energy-right-close > energy-ahead-close and energy-right-close > energy-left-close
  [ rt 90 fd 1 ]

  [
    rt (random-float 90 - random-float 90)
    fd 3
  ]
)''',

    # Test 5 - has invalid > 2 comparisons (should be False)
    '''; Advanced energy-seeking movement strategy with multi-level sensing and adaptive decision-making
(ifelse
  ; High-priority: Maximize positive energy collection with intelligent directional selection
  (energy-ahead-close > 0 and energy-ahead-close >= energy-left-close and energy-ahead-close >= energy-right-close)
  [ fd 1 ]

  (energy-left-close > 0 and energy-left-close > energy-ahead-close and energy-left-close > energy-right-close)
  [ lt 90 fd 1 ]

  (energy-right-close > 0 and energy-right-close > energy-ahead-close and energy-right-close > energy-left-close)
  [ rt 90 fd 1 ]

  ; Secondary priority: Medium-range energy exploration with weighted movement
  (energy-ahead-medium > energy-left-medium and energy-ahead-medium > energy-right-medium)
  [ ifelse energy-ahead-medium > 2 [ fd 4 ] [ fd 2 ] ]

  (energy-left-medium > energy-ahead-medium and energy-left-medium > energy-right-medium)
  [ lt 90 ifelse energy-left-medium > 2 [ fd 4 ] [ fd 2 ] ]

  (energy-right-medium > energy-ahead-medium and energy-right-medium > energy-left-medium)
  [ rt 90 ifelse energy-right-medium > 2 [ fd 4 ] [ fd 2 ] ]

  ; Tertiary priority: Long-range energy detection with risk-aware movement
  (energy-ahead-far > 0 and energy-ahead-far >= energy-left-far and energy-ahead-far >= energy-right-far)
  [ ifelse energy-ahead-far > 5 [ fd 7 ] [ fd 3 ] ]

  (energy-left-far > 0 and energy-left-far > energy-ahead-far and energy-left-far > energy-right-far)
  [ lt 90 ifelse energy-left-far > 5 [ fd 7 ] [ fd 3 ] ]

  (energy-right-far > 0 and energy-right-far > energy-ahead-far and energy-right-far > energy-left-far)
  [ rt 90 ifelse energy-right-far > 5 [ fd 7 ] [ fd 3 ] ]

  ; Fallback: Intelligent random exploration with minimal energy loss
  [ rt (random 90 - 45) fd 1 ]
)''',

    # Additional test from RASTRIGIN suite 
    # Test 6 - should be false, missing variables
    '''ifelse energy-ahead-close > 0 [
  fd 1
] [
  ifelse energy-left-close > 0 [
    lt 90 fd 1
  ] [
    ifelse energy-right-close > 0 [
      rt 90 fd 1
    ] [
      ifelse energy-ahead-medium > 0 [
        fd 4
      ] [
        ifelse energy-left-medium > 0 [
          lt 90 fd 4
        ] [
          ifelse energy-right-medium > 0 [
            rt 90 fd 4
          ] [
            rt random-float 45 - random-float 45
            fd 2
          ]
        ]
      ]
    ]
  ]
]''',

    # Test 7 - complete nested with all 9 (should be True)
    '''ifelse energy-ahead-close > 0 [
  fd 1
] [
  ifelse energy-left-close > 0 [
    lt 45 fd 1
  ] [
    ifelse energy-right-close > 0 [
      rt 45 fd 1
    ] [
      ifelse energy-ahead-medium > 0 [
        fd 2
      ] [
        ifelse energy-left-medium > 0 [
          lt 45 fd 2
        ] [
          ifelse energy-right-medium > 0 [
            rt 45 fd 2
          ] [
            ifelse energy-ahead-far > 0 [
              fd 3
            ] [
              ifelse energy-left-far > 0 [
                lt 45 fd 3
              ] [
                ifelse energy-right-far > 0 [
                  rt 45 fd 3
                ] [
                  rt random 90
                  fd 2
                ]
              ]
            ]
          ]
        ]
      ]
    ]
  ]
]''',

    # Test 8 - complete switch with all 9 (should be True) 
    '''(ifelse
  energy-ahead-close > 0 [ forward 1 ]
  energy-left-close > 0 [ left 90 forward 1 ]
  energy-right-close > 0 [ right 90 forward 1 ]

  energy-ahead-medium > 0 [ forward 2 ]
  energy-left-medium > 0 [ left 90 forward 2 ]
  energy-right-medium > 0 [ right 90 forward 2 ]

  energy-ahead-far > 0 [ forward 3 ]
  energy-left-far > 0 [ left 90 forward 3 ]
  energy-right-far > 0 [ right 90 forward 3 ]

  [ right random 45 left random 45 forward 1 ]
)''',

    # Test 9 - imcomplete > 0
    '''ifelse energy-ahead-close > energy-left-close and energy-ahead-close > energy-right-close [
  fd 1
] [
  ifelse energy-ahead-medium > energy-left-medium and energy-ahead-medium > energy-right-medium [
    fd 4
  ] [
    ifelse energy-left-close > energy-right-close and energy-left-close > energy-ahead-close [
      lt 90 fd 1
    ] [
      ifelse energy-right-close > energy-left-close and energy-right-close > energy-ahead-close [
        rt 90 fd 1
      ] [
        ifelse energy-ahead-far > energy-left-far and energy-ahead-far > energy-right-far [
          fd 7
        ] [
          ifelse energy-left-far > energy-right-far [
            lt 90 fd 7
          ] [
            ifelse energy-right-far > energy-left-far [
              rt 90 fd 7
            ] [
              lt random 20 rt random 20 fd 1
            ]
          ]
        ]
      ]
    ]
  ]
]'''
]

# Expected results for each test case
expected_results = [
    True,   # 0: Complete nested (all 9)
    False,  # 1: Incomplete switch (missing left/right medium/far)
    True,   # 2: Complete switch (all 9)
    False,  # 3: Missing far variables
    False,  # 4: Only close variables
    False,  # 5: Has invalid > 2 comparisons
    False,  # 6: Missing far variables (only 6 levels)
    True,   # 7: Complete nested (all 9)
    True,   # 8: Complete switch (all 9)
    False,  # 9: Missing > 0 checks (no explicit > 0)
]

def run_comprehensive_test():
    """Run comprehensive tests using the verification framework."""
    print("Comprehensive Test Suite for NetLogo Code Verification")
    print("=" * 80)
    
    # Create verification framework
    framework = create_verification_framework(".")
    
    # Display discovered verifiers
    verifiers = framework.get_verifier_names()
    verifier_info = framework.get_verifier_info()
    
    print(f"Discovered {len(verifiers)} verifier(s):")
    for name in sorted(verifiers):
        info = verifier_info[name]
        print(f"  - {name} (from {info['file']})")
    print()
    
    if not verifiers:
        print("❌ No verifiers found! Please ensure verify-*.py files are present.")
        return False
    
    # Run tests
    all_passed = True
    detailed_results = []
    
    for i, (test_case, expected) in enumerate(zip(test_cases, expected_results)):
        # Run all verifiers on this test case
        overall_pass, individual_results = framework.verify_code(test_case)
        
        # Test passes only if it meets the expected result
        test_passed = (overall_pass == expected)
        status = "✓ PASS" if test_passed else "✗ FAIL"
        
        print(f"Test {i:2}: {status} | Expected: {str(expected):5} | Got: {str(overall_pass):5}")
        
        # Show individual verifier results
        for verifier_name in sorted(individual_results.keys()):
            result = individual_results[verifier_name]
            icon = "✓" if result else "✗"
            print(f"        {verifier_name}: {icon} {result}")
        
        if not test_passed:
            all_passed = False
            print(f"         Code snippet: {test_case[:80].replace(chr(10), ' ')}...")
        
        detailed_results.append({
            'test_index': i,
            'expected': expected,
            'overall_result': overall_pass,
            'individual_results': individual_results,
            'passed': test_passed
        })
        print()
    
    # Summary
    print("=" * 80)
    passed_count = sum(1 for r in detailed_results if r['passed'])
    total_count = len(detailed_results)
    
    print(f"Test Results: {passed_count}/{total_count} tests passed")
    
    if all_passed:
        print("🎉 Overall result: All tests PASSED!")
    else:
        failed_tests = [r['test_index'] for r in detailed_results if not r['passed']]
        print(f"❌ Overall result: Tests FAILED! Failed tests: {failed_tests}")
    
    return all_passed

if __name__ == "__main__":
    run_comprehensive_test() 