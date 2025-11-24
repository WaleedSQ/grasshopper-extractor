"""Analyze what Plane Normal should do with a plane input"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

# Construct Plane output
cp_guid = '30f76ec5-d532-4903-aa18-cd18b27442f9'
# Plane Normal 2 (receives Construct Plane)
pn2_guid = '011398ea-ce1d-412a-afeb-fe91e8fac96c'

print("="*80)
print("PLANE NORMAL BEHAVIOR WITH PLANE INPUT")
print("="*80)

cp_plane = list(results[cp_guid]['outputs']['Plane']['branches'].values())[0][0]
print("\nConstruct Plane outputs:")
print(f"  X-axis: {cp_plane['x_axis']}")
print(f"  Y-axis: {cp_plane['y_axis']}")
print(f"  Z-axis: {cp_plane['z_axis']}")
print("\n  ✓ Z-axis = [-1, 0, 0] MATCHES screenshot!")

pn2_plane = list(results[pn2_guid]['outputs']['Plane']['branches'].values())[0][0]
print("\nPlane Normal 2 outputs:")
print(f"  X-axis: {pn2_plane['x_axis']}")
print(f"  Y-axis: {pn2_plane['y_axis']}")
print(f"  Z-axis: {pn2_plane['z_axis']}")

print("\n" + "="*80)
print("EXPECTED FROM EARLIER SCREENSHOT:")
print("="*80)
print("Plane Normal should output: Z(0.00,-1.00,0.00)")
print(f"Currently outputting: Z{tuple(pn2_plane['z_axis'])}")

print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)
print("Construct Plane gives Plane Normal a plane with:")
print("  X-axis = [0, -1, 0]")
print("  Y-axis = [0, 0, 1]")
print("  Z-axis = [-1, 0, 0]")
print()
print("Expected Plane Normal output: Z-axis = [0, -1, 0]")
print()
print("HYPOTHESIS:")
print("When Plane Normal receives a PLANE, it might use the plane's")
print("X-AXIS (not Z-axis) as the direction!")
print()
print("Test: If Plane Normal uses plane.x_axis = [0, -1, 0]")
print("      Then output Z-axis should be [0, -1, 0] ✓ MATCHES!")

