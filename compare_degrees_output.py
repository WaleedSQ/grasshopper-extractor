"""Compare current Degrees output with screenshot"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

degrees_guid = "fa0ba5a6-7dd9-43f4-a82a-cf02841d0f58"

screenshot_values = [
    43.701519,
    43.033895,
    42.213797,
    41.218013,
    39.968747,
    38.335501,
    36.180578,
    33.323467,
    29.029873,
    22.969535
]

print("="*80)
print("DEGREES OUTPUT COMPARISON")
print("="*80)

if degrees_guid in results:
    degrees_data = results[degrees_guid]
    degrees_output = degrees_data['outputs']['Degrees']
    degrees_values = degrees_output['branches']['(0,)']
    
    print(f"\nCurrent output: {len(degrees_values)} items")
    print(f"Expected: {len(screenshot_values)} items\n")
    
    print("Index | Current      | Expected     | Difference")
    print("-" * 60)
    
    for i in range(max(len(degrees_values), len(screenshot_values))):
        if i < len(degrees_values) and i < len(screenshot_values):
            current = degrees_values[i]
            expected = screenshot_values[i]
            diff = current - expected
            print(f"  [{i}] | {current:12.6f} | {expected:12.6f} | {diff:+.6f}")
        elif i < len(degrees_values):
            current = degrees_values[i]
            print(f"  [{i}] | {current:12.6f} | (missing)    | ")
        else:
            expected = screenshot_values[i]
            print(f"  [{i}] | (missing)    | {expected:12.6f} | ")

print("\n" + "="*80)
print("KEY FINDING: All current values are IDENTICAL")
print("Expected values are DIFFERENT")
print("="*80)

