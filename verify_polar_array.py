"""
Verify Polar Array component in Rotatingslats chain.
"""
import json
from gh_data_tree import DataTree, is_tree

# Load evaluation results
with open('evaluation_results.md', 'r') as f:
    content = f.read()

# Load graph to get component info
with open('complete_component_graph.json', 'r') as f:
    graph = json.load(f)

# Polar Array component GUID
pa_guid = '7ad636cc-e506-4f77-bb82-4a86ba2a3fea'
pa_comp = graph['components'][pa_guid]

print("=" * 80)
print("POLAR ARRAY VERIFICATION")
print("=" * 80)
print()

print("Component Info:")
print(f"  GUID: {pa_guid}")
print(f"  Type: {pa_comp['obj']['type']}")
print(f"  NickName: {pa_comp['obj']['nickname']}")
print()

print("Inputs:")
print("  1. Geometry:")
geom_source = pa_comp['inputs']['param_input_0']['sources'][0]
print(f"     Source: {geom_source['source_obj_name']} ({geom_source['source_obj_guid'][:8]}...)")
print(f"     Output GUID: {geom_source['source_guid']}")
print()

print("  2. Plane:")
plane_persistent = pa_comp['inputs']['param_input_1'].get('persistent_values', [])
if plane_persistent:
    import json
    plane = json.loads(plane_persistent[0])
    print(f"     Origin: {plane['origin']}")
    print(f"     Z-axis: {plane['z_axis']}")
print()

print("  3. Count:")
count_source = pa_comp['inputs']['param_input_2']['sources'][0]
print(f"     Source: {count_source['source_obj_name']} ({count_source['source_guid'][:8]}...)")
# Get value from external_inputs
with open('external_inputs.json', 'r') as f:
    ext_inputs = json.load(f)
count_value = ext_inputs.get(count_source['source_guid'], {}).get('value', 'N/A')
print(f"     Value: {count_value}")
print()

print("  4. Angle:")
angle_persistent = pa_comp['inputs']['param_input_3'].get('persistent_values', [])
if angle_persistent:
    angle = float(angle_persistent[0])
    print(f"     Value: {angle} radians ({angle * 180 / 3.14159:.1f} degrees)")
print()

print("Expected Behavior:")
print("  - Input: DataTree with 10 branches (one rectangle per branch)")
print("  - Count: 8 rotations per branch")
print("  - Angle: 2*pi radians (full circle)")
print("  - Output: DataTree with 10 branches, each containing 8 rotated rectangles")
print()

print("Verification:")
print("  Check evaluation output for:")
print("    - [ROTATINGSLATS] Polar Array: output 10 branches")
print("    - Each branch should have 8 items (rotations)")
print()

