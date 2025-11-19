"""
Verify the actual calculation for Move "Targets" component.
Check what the screenshot shows and compare with our calculation.
"""

import json

print("=" * 80)
print("VERIFYING MOVE 'Targets' CALCULATION")
print("=" * 80)

# Load evaluation results to see what we're actually getting
try:
    with open('evaluation_results.md', 'r') as f:
        content = f.read()
    
    # Extract the relevant component outputs
    print("\nFrom evaluation_results.md:")
    print("-" * 80)
    
    # Find Amplitude output
    if 'd0668a07' in content:
        print("Amplitude (d0668a07...): [11.327429598006665, -27.346834162334087, 0.0]")
        motion = [11.327429598006665, -27.346834162334087, 0.0]
    else:
        print("Amplitude output not found in results")
        motion = None
    
    # Find Polar Array output
    if 'e7683176' in content and 'Polar Array' in content:
        print("Polar Array (e7683176...): [[[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]]")
        polar_array_output = [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0]]
    else:
        print("Polar Array output not found")
        polar_array_output = None
    
    # Find List Item output
    if 'c0f3d527' in content:
        print("List Item (c0f3d527...): None [This is the problem!]")
        list_item_output = None
    elif 'f03b9ab7' in content:
        print("List Item (f03b9ab7...): [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]")
        list_item_output = [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0]]
    else:
        list_item_output = None
    
    # Find Move "Targets" output
    if '80fd9f48' in content or 'b38a38f1' in content:
        print("Move 'Targets' (80fd9f48/b38a38f1...): [[11.327429598006665, -31.846834162334087, 14.0], ...]")
        move_output = [11.327429598006665, -31.846834162334087, 14.0]
    else:
        move_output = None
    
    print("\n" + "=" * 80)
    print("CALCULATION VERIFICATION:")
    print("=" * 80)
    
    if list_item_output and motion:
        geometry_point = list_item_output[0]  # First point
        print(f"\nGeometry (first point from List Item): {geometry_point}")
        print(f"Motion (from Amplitude): {motion}")
        
        expected_result = [
            geometry_point[0] + motion[0],
            geometry_point[1] + motion[1],
            geometry_point[2] + motion[2]
        ]
        print(f"\nExpected result: {expected_result}")
        
        if move_output:
            print(f"Actual result: {move_output}")
            print(f"\nComparison:")
            print(f"  X: Expected {expected_result[0]:.15f}, Got {move_output[0]:.15f} - {'MATCH' if abs(expected_result[0] - move_output[0]) < 0.0001 else 'MISMATCH'}")
            print(f"  Y: Expected {expected_result[1]:.15f}, Got {move_output[1]:.15f} - {'MATCH' if abs(expected_result[1] - move_output[1]) < 0.0001 else 'MISMATCH'}")
            print(f"  Z: Expected {expected_result[2]:.15f}, Got {move_output[2]:.15f} - {'MATCH' if abs(expected_result[2] - move_output[2]) < 0.0001 else 'MISMATCH'}")
            
            if abs(expected_result[1] - move_output[1]) > 0.0001:
                print(f"\nY COORDINATE MISMATCH!")
                print(f"  Difference: {abs(expected_result[1] - move_output[1]):.15f}")
                print(f"\nPossible causes:")
                print("  1. Geometry input is different than expected")
                print("  2. Motion vector is different than expected")
                print("  3. There's an additional transformation being applied")
                print("  4. The List Item is getting the wrong item from the list")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Check what the screenshot actually shows for the expected Y value")
    print("2. Verify the List Item (c0f3d527...) is correctly extracting from Polar Array")
    print("3. Check if the geometry input to Move is actually the List Item output")
    print("4. Verify the Amplitude calculation is correct")
    print("5. Check if there are any additional transformations in the Move component")

except FileNotFoundError:
    print("Could not find evaluation_results.md")

