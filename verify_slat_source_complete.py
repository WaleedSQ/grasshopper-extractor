"""
Complete verification of "Slat source" calculation:
1. Construct Point A (be907c11...)
   - X: from "Slat lenght" (fadbd125...) = 2.5
   - Y: from subtraction (eedce522...)
   - Z: 0
2. Construct Point B (67b3eb53...)
   - X: from "Slat width" (0d27dd7f...) = 0.080
   - Y: from subtraction (eedce522...)
   - Z: 0
3. Rectangle 2Pt (a3eb185f...)
   - Point A: from Construct Point A
   - Point B: from Construct Point B
   - Length: from "Slat thickness" = 0.001
4. Surface (8fec620f...)
   - Geometry: from Rectangle 2Pt output
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, get_external_inputs, evaluate_component, resolve_input_value

# Load the graph
graph_data = load_component_graph('complete_component_graph.json')
graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

# Load all objects
with open('rotatingslats_data.json', 'r') as f:
    data = json.load(f)
    all_objects = {}
    all_objects.update(data.get('group_objects', {}))
    all_objects.update(data.get('external_objects', {}))

# Build output params
output_params = {}
for key, obj in all_objects.items():
    for param_key, param_info in obj.get('params', {}).items():
        if param_key.startswith('param_output'):
            param_guid = param_info.get('data', {}).get('InstanceGuid')
            if param_guid:
                output_params[param_guid] = {
                    'obj': obj,
                    'param_key': param_key,
                    'param_info': param_info
                }

external_inputs = get_external_inputs()
evaluated = {}

print("=" * 60)
print("Complete 'Slat source' Calculation Verification")
print("=" * 60)
print()

# Step 1: "Slat lenght" (already verified = 2.5)
print("Step 1: Slat lenght (already verified)")
print("-" * 60)
print("  Value: 2.5 (room width 5.0 / 2)")
print()

# Step 2: Find Y coordinate source (eedce522...)
print("Step 2: Find Y Coordinate Source")
print("-" * 60)
y_source_guid = "eedce522-16c4-4b3a-8341-c26cc0b6bb91"

# Find what produces this output
y_source_comp = None
for comp_id, comp_info in graph.items():
    if isinstance(comp_info, dict) and comp_info.get('type') == 'component':
        outputs = comp_info.get('outputs', {})
        for output_key, output_info in outputs.items():
            if output_info.get('instance_guid') == y_source_guid:
                y_source_comp = comp_id
                comp_type = comp_info.get('obj', {}).get('type', 'Unknown')
                comp_nickname = comp_info.get('obj', {}).get('nickname', '')
                print(f"  [OK] Found component: {comp_id[:8]}... ({comp_type}) '{comp_nickname}'")
                break
        if y_source_comp:
            break

if not y_source_comp:
    # Search in all_objects
    for key, obj in all_objects.items():
        for param_key, param_info in obj.get('params', {}).items():
            if param_key.startswith('param_output'):
                param_guid = param_info.get('data', {}).get('InstanceGuid')
                if param_guid == y_source_guid:
                    y_source_comp = obj.get('instance_guid')
                    print(f"  [OK] Found in all_objects: {y_source_comp[:8]}...")
                    break
        if y_source_comp:
            break

if y_source_comp:
    print(f"  This provides Y coordinate for both Construct Point components")
else:
    print(f"  [X] Y coordinate source not found")

print()

# Step 3: Construct Point A
print("Step 3: Construct Point A (be907c11...)")
print("-" * 60)
point_a_comp_guid = "be907c11-5a37-4cf5-9736-0f3c61ba7014"
point_a_output_guid = "902866aa-e5b3-4461-9877-73b22ea3618a"

if point_a_comp_guid in all_objects:
    point_a_obj = all_objects[point_a_comp_guid]
    print(f"  Component: {point_a_comp_guid[:8]}...")
    print(f"  Type: {point_a_obj.get('type', 'Unknown')}")
    print()
    
    # Get inputs
    params = point_a_obj.get('params', {})
    print("  Inputs:")
    for param_key, param_info in params.items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            persistent_values = param_info.get('persistent_values', [])
            print(f"    {param_name}:")
            if sources:
                for source in sources:
                    source_guid = source.get('guid')
                    print(f"      Source: {source_guid[:8] if source_guid else 'N/A'}...")
            elif persistent_values:
                print(f"      Constant: {persistent_values[0]}")
    
    # Expected values from screenshot:
    # X = 0.080 (Slat width) - but GHX shows source is fadbd125... (Slat lenght = 2.5)
    # Y = from subtraction
    # Z = 0
    print()
    print("  Expected (from screenshot):")
    print("    X = 0.080 (Slat width)")
    print("    Y = from subtraction")
    print("    Z = 0")
    print()
    print("  Note: GHX shows X source is 'Slat lenght' (2.5), not 'Slat width' (0.080)")
    print("  This is another discrepancy between GHX and screenshot!")

print()

# Step 4: Construct Point B
print("Step 4: Construct Point B")
print("-" * 60)
point_b_output_guid = "ef17623c-d081-46f9-8259-2ad83ec05d94"

# Find Construct Point B
point_b_comp_guid = None
for key, obj in all_objects.items():
    for param_key, param_info in obj.get('params', {}).items():
        if param_key.startswith('param_output'):
            param_guid = param_info.get('data', {}).get('InstanceGuid')
            if param_guid == point_b_output_guid:
                point_b_comp_guid = obj.get('instance_guid')
                print(f"  [OK] Found Construct Point B: {point_b_comp_guid[:8]}...")
                break
    if point_b_comp_guid:
        break

if point_b_comp_guid and point_b_comp_guid in all_objects:
    point_b_obj = all_objects[point_b_comp_guid]
    print(f"  Type: {point_b_obj.get('type', 'Unknown')}")
    print()
    
    # From GHX, Point B has PersistentData: X=10, Y=5, Z=0
    print("  From GHX PersistentData:")
    print("    X = 10")
    print("    Y = 5")
    print("    Z = 0")
    print()
    print("  Expected (from screenshot):")
    print("    X = 0.080 (Slat width)")
    print("    Y = from subtraction")
    print("    Z = 0")
    print()
    print("  Note: Another discrepancy - GHX has hardcoded values (10, 5, 0)")

print()

# Step 5: Rectangle 2Pt
print("Step 5: Rectangle 2Pt (a3eb185f...)")
print("-" * 60)
rect_comp_guid = "a3eb185f-a7cb-4727-aeaf-d5899f934b99"
rect_output_guid = "dbc236d4-a2fe-48a8-a86e-eebfb04b1053"

print(f"  Component: {rect_comp_guid[:8]}...")
print(f"  Inputs:")
print(f"    Point A: from Construct Point A ({point_a_output_guid[:8]}...)")
print(f"    Point B: from Construct Point B ({point_b_output_guid[:8]}...)")
print(f"    Length: from 'Slat thickness' = 0.001")
print()

# Step 6: Surface
print("Step 6: Surface 'Slat source' (8fec620f...)")
print("-" * 60)
surface_comp_guid = "8fec620f-ff7f-4b94-bb64-4c7fce2fcb34"
print(f"  Component: {surface_comp_guid[:8]}...")
print(f"  Source: Rectangle 2Pt output ({rect_output_guid[:8]}...)")
print(f"  This is a pass-through component for geometry")
print()

print("=" * 60)
print("Summary:")
print("  The calculation chain is:")
print("    1. Slat lenght (2.5) -> Construct Point A X coordinate")
print("    2. Subtraction result -> Construct Point A & B Y coordinate")
print("    3. Construct Point A & B -> Rectangle 2Pt")
print("    4. Rectangle 2Pt -> Surface 'Slat source'")
print()
print("  Note: There are discrepancies between GHX values and screenshot")
print("  - Construct Point A X: GHX shows 2.5, screenshot shows 0.080")
print("  - Construct Point B: GHX shows (10, 5, 0), screenshot shows (0.080, subtraction, 0)")

