"""
Debug why Move "Targets" output doesn't match expected values.
"""

# Expected: Geometry input from List Item should be a list of points
# Motion input from Amplitude: [11.327429598006665, -27.346834162334087, 0.0]

# From evaluation results:
# Component 8: Polar Array outputs: [[[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]]
# Component 61: List Item should extract index 0: [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]
# Component 47: Amplitude outputs: [11.327429598006665, -27.346834162334087, 0.0]
# Component 38: Move "Targets" outputs: [[11.327429598006665, -31.846834162334087, 14.0], ...]

print("=" * 80)
print("DEBUGGING MOVE 'Targets' OUTPUT")
print("=" * 80)

# Expected calculation:
print("\nExpected calculation:")
print("  Geometry point 0: [0.0, -4.5, 4.0]")
print("  Motion vector: [11.327429598006665, -27.346834162334087, 0.0]")
print("  Expected result: [0.0 + 11.327429598006665, -4.5 + (-27.346834162334087), 4.0 + 0.0]")
expected = [0.0 + 11.327429598006665, -4.5 + (-27.346834162334087), 4.0 + 0.0]
print(f"  = {expected}")

# Actual output:
print("\nActual output (from evaluation_results.md):")
print("  [11.327429598006665, -31.846834162334087, 14.0]")

# Check if X and Y match:
print("\nComparison:")
print(f"  X: Expected {expected[0]}, Got 11.327429598006665 - {'MATCH' if abs(expected[0] - 11.327429598006665) < 0.001 else 'MISMATCH'}")
print(f"  Y: Expected {expected[1]}, Got -31.846834162334087 - {'MATCH' if abs(expected[1] - (-31.846834162334087)) < 0.001 else 'MISMATCH'}")
print(f"  Z: Expected {expected[2]}, Got 14.0 - {'MATCH' if abs(expected[2] - 14.0) < 0.001 else 'MISMATCH'}")

# The Z value is wrong! It should be 4.0, not 14.0
print("\n" + "=" * 80)
print("ISSUE FOUND:")
print("=" * 80)
print("Z coordinate is 14.0 instead of 4.0")
print("This suggests the geometry input might be wrong, or there's an offset being added.")

# Check what the List Item should output
print("\nChecking List Item output:")
print("  List Item should extract index 0 from Polar Array output")
print("  Polar Array output: [[[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]]")
print("  List Item index 0 should give: [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]")
print("  But if List Item is getting the wrong list or wrong index, it might be getting a different point")

# Check if there's another source of the Z=14.0 value
print("\nPossible causes:")
print("  1. List Item is getting the wrong item from the list")
print("  2. Geometry input is coming from a different source than expected")
print("  3. There's an additional transformation being applied")
print("  4. The Polar Array output structure is different than expected")

