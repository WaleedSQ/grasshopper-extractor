"""
Debug the exact geometry flow from first Move -> Polar Array -> List Item -> second Move
"""

import json

# Load evaluation results
with open('evaluation_results.md', 'r') as f:
    content = f.read()

# Component GUIDs
FIRST_MOVE_OUTPUT = '47af807c-369d-4bd2-bbbb-d53a4605f8e6'
POLAR_ARRAY_OUTPUT = '1a00d7ad-1003-4dfa-a933-6a7a60dfb0b1'
LIST_ITEM_OUTPUT = 'a72418c4-eb29-4226-9dea-f076720da34f'
SECOND_MOVE_OUTPUT = '4218a4e5-b5a7-477b-b7e2-dfc59ff7b896'

print("=" * 80)
print("GEOMETRY FLOW INVESTIGATION")
print("=" * 80)
print()

# Find first Move output
print("1. FIRST MOVE OUTPUT (47af807c...):")
print("-" * 80)
if FIRST_MOVE_OUTPUT in content:
    # Extract the line
    lines = content.split('\n')
    for line in lines:
        if FIRST_MOVE_OUTPUT in line and 'Move' in line and 'Slats original' in line:
            print(f"   {line}")
            # Try to extract geometry info
            if 'rectangle' in line.lower():
                print("   Type: rectangle")
                if 'corners' in line.lower() or 'plane' in line.lower():
                    print("   Contains corners/plane data")
            break
print()

# Find Polar Array output
print("2. POLAR ARRAY OUTPUT (1a00d7ad...):")
print("-" * 80)
if POLAR_ARRAY_OUTPUT in content:
    lines = content.split('\n')
    for line in lines:
        if POLAR_ARRAY_OUTPUT in line and 'Polar Array' in line:
            print(f"   {line}")
            # Check if it's a nested list
            if '[[' in line:
                print("   Type: nested list (list of lists)")
                print("   Structure: [[{rectangles}]]")
            elif '[' in line:
                print("   Type: flat list")
                print("   Structure: [{rectangles}]")
            break
print()

# Find List Item output
print("3. LIST ITEM OUTPUT (a72418c4...):")
print("-" * 80)
if LIST_ITEM_OUTPUT in content:
    lines = content.split('\n')
    for line in lines:
        if LIST_ITEM_OUTPUT in line and 'List Item' in line:
            print(f"   {line}")
            break
else:
    print("   Not found in evaluation results")
print()

# Find second Move output
print("4. SECOND MOVE OUTPUT (4218a4e5...):")
print("-" * 80)
if SECOND_MOVE_OUTPUT in content:
    lines = content.split('\n')
    for line in lines:
        if SECOND_MOVE_OUTPUT in line and 'Move' in line and 'Slats original' in line:
            print(f"   {line}")
            break
print()

print("=" * 80)
print("KEY QUESTIONS:")
print("=" * 80)
print("1. What does List Item with Index=0 extract from Polar Array output?")
print("   - If Polar Array outputs [[{rectangles}]], List Item Index=0 should return [{rectangles}]")
print("   - But does it return a single rectangle or a list of rectangles?")
print()
print("2. What is the Y coordinate of the geometry input to second Move?")
print("   - Expected: Y=0.0 (based on expected centroid Y=-27.416834)")
print("   - Actual: Y=0.11 (from debug output)")
print()
print("3. Does the first Move output have Y=0.11 or Y=0.0?")
print("   - This will determine if Polar Array or List Item is changing the Y coordinate")

