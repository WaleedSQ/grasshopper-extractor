"""
Check why the Y coordinate -31.846834162334087 doesn't match the screenshot.
"""

print("=" * 80)
print("CHECKING Y COORDINATE CALCULATION")
print("=" * 80)

# Current calculation:
print("\nCurrent calculation:")
print("  Geometry point: [0.0, -4.5, 4.0]")
print("  Motion vector: [11.327429598006665, -27.346834162334087, 0.0]")
print("  Result: [11.327429598006665, -31.846834162334087, 4.0]")
print("  Y = -4.5 + (-27.346834162334087) = -31.846834162334087")

# Let's check if the geometry input might be different
print("\n" + "=" * 80)
print("POSSIBLE ISSUES:")
print("=" * 80)
print("1. The geometry input might not be [0.0, -4.5, 4.0]")
print("   - List Item might be getting a different index")
print("   - Polar Array output structure might be different")
print("   - The first point in the list might be different")

print("\n2. The motion vector might be different")
print("   - Amplitude output might be calculated differently")
print("   - There might be additional transformations")

print("\n3. The calculation might need to be done differently")
print("   - Maybe it's not a simple addition")
print("   - Maybe there's a coordinate system transformation")

# Let's check what the Polar Array actually outputs
print("\n" + "=" * 80)
print("CHECKING POLAR ARRAY OUTPUT:")
print("=" * 80)
print("From evaluation_results.md:")
print("  Component 8: Polar Array PA.Geometry")
print("  Output: [[[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]]")
print("  This is a list of lists of points")

print("\nList Item should extract index 0:")
print("  Result: [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]")
print("  This is a list of points")

print("\nMove component should move each point by the motion vector:")
print("  Point 0: [0.0, -4.5, 4.0] + [11.327429598006665, -27.346834162334087, 0.0]")
print("         = [11.327429598006665, -31.846834162334087, 4.0]")

# But wait - maybe the issue is that we need to check what the actual first point is
# Or maybe the List Item is getting a different item from the list
print("\n" + "=" * 80)
print("NEED TO VERIFY:")
print("=" * 80)
print("1. What does the screenshot show as the expected Y value?")
print("2. What is the actual geometry input to the Move component?")
print("3. What is the actual motion vector being used?")

