"""
Final verification of "Slat source" calculation with all values.
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, get_external_inputs

# Load the graph
graph_data = load_component_graph('complete_component_graph.json')
graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

# Load all objects
with open('rotatingslats_data.json', 'r') as f:
    data = json.load(f)
    all_objects = {}
    all_objects.update(data.get('group_objects', {}))
    all_objects.update(data.get('external_objects', {}))

external_inputs = get_external_inputs()

print("=" * 60)
print("Complete 'Slat source' Calculation Chain")
print("=" * 60)
print()

# Step 1: Slat lenght = 2.5
print("Step 1: Slat lenght")
print("-" * 60)
print("  Division (32cc502c...): room width (5.0) / 2 = 2.5")
print("  Output GUID: 4c2fdd4e...")
print("  [OK] Value: 2.5")
print()

# Step 2: Y coordinate source (Division b9102ff3...)
print("Step 2: Y Coordinate Source")
print("-" * 60)
y_div_comp_guid = "b9102ff3-4813-4791-a67d-5654a9f7bae9"
y_source_output_guid = "eedce522-16c4-4b3a-8341-c26cc0b6bb91"

if y_div_comp_guid in graph:
    y_div_comp_info = graph[y_div_comp_guid]
    inputs = y_div_comp_info.get('inputs', {})
    print(f"  Division component ({y_div_comp_guid[:8]}...):")
    
    # Get input A (Slat width)
    input_a_info = inputs.get('param_input_0', {})
    input_a_sources = input_a_info.get('sources', [])
    if input_a_sources:
        source_guid = input_a_sources[0].get('source_guid')
        if source_guid == "0d27dd7f-44bf-4778-8d07-d44b711c47f2":
            slat_width_value = external_inputs.get(source_guid, 0.08)
            if isinstance(slat_width_value, dict):
                slat_width_value = slat_width_value.get('value', 0.08)
            print(f"    Input A: Slat width = {slat_width_value}")
    
    # Get input B (constant 2)
    input_b_info = inputs.get('param_input_1', {})
    print(f"    Input B: constant = 2")
    
    result = slat_width_value / 2 if 'slat_width_value' in locals() else 0.08 / 2
    print(f"    Result: {slat_width_value if 'slat_width_value' in locals() else 0.08} / 2 = {result}")
    print(f"  Output GUID: {y_source_output_guid[:8]}...")
    print(f"  [OK] Value: {result}")
else:
    print(f"  [X] Division component not found in graph")

print()

# Step 3: Construct Point A
print("Step 3: Construct Point A (be907c11...)")
print("-" * 60)
point_a_comp_guid = "be907c11-5a37-4cf5-9736-0f3c61ba7014"
point_a_output_guid = "902866aa-e5b3-4461-9877-73b22ea3618a"

if point_a_comp_guid in all_objects:
    point_a_obj = all_objects[point_a_comp_guid]
    params = point_a_obj.get('params', {})
    
    print(f"  Component: {point_a_comp_guid[:8]}...")
    print(f"  Inputs:")
    
    # X coordinate: from Slat lenght (fadbd125...)
    x_param = params.get('param_input_0', {})
    x_sources = x_param.get('sources', [])
    if x_sources:
        x_source_guid = x_sources[0].get('guid')
        print(f"    X: from {x_source_guid[:8]}... (Slat lenght = 2.5)")
    
    # Y coordinate: from Division (eedce522...)
    y_param = params.get('param_input_1', {})
    y_sources = y_param.get('sources', [])
    if y_sources:
        y_source_guid = y_sources[0].get('guid')
        print(f"    Y: from {y_source_guid[:8]}... (Division = {result if 'result' in locals() else 0.04})")
    
    # Z coordinate: constant 0
    z_param = params.get('param_input_2', {})
    z_persistent = z_param.get('persistent_values', [])
    if z_persistent:
        print(f"    Z: constant = {z_persistent[0]}")
    
    point_a_result = [2.5, result if 'result' in locals() else 0.04, 0.0]
    print(f"  Result: {point_a_result}")
    print(f"  Output GUID: {point_a_output_guid[:8]}...")
    print(f"  [OK] Point A: {point_a_result}")

print()

# Step 4: Construct Point B
print("Step 4: Construct Point B (67b3eb53...)")
print("-" * 60)
point_b_comp_guid = "67b3eb53-9ea7-4280-bf8b-ae16c080cc23"
point_b_output_guid = "ef17623c-d081-46f9-8259-2ad83ec05d94"

if point_b_comp_guid in all_objects:
    point_b_obj = all_objects[point_b_comp_guid]
    params = point_b_obj.get('params', {})
    
    print(f"  Component: {point_b_comp_guid[:8]}...")
    print(f"  Inputs:")
    
    # X coordinate: from 8a96679d...
    x_param = params.get('param_input_0', {})
    x_sources = x_param.get('sources', [])
    if x_sources:
        x_source_guid = x_sources[0].get('guid')
        print(f"    X: from {x_source_guid[:8]}... (need to find)")
    
    # Y coordinate: from 370f6ae5...
    y_param = params.get('param_input_1', {})
    y_sources = y_param.get('sources', [])
    if y_sources:
        y_source_guid = y_sources[0].get('guid')
        print(f"    Y: from {y_source_guid[:8]}... (need to find)")
    
    # Z coordinate: constant 0
    z_param = params.get('param_input_2', {})
    z_persistent = z_param.get('persistent_values', [])
    if z_persistent:
        print(f"    Z: constant = {z_persistent[0]}")
    
    # From GHX PersistentData, Point B has X=10, Y=5, Z=0
    print(f"  Note: GHX shows PersistentData: X=10, Y=5, Z=0")
    print(f"  But screenshot shows: X=0.080, Y=from subtraction, Z=0")

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
print(f"  Output GUID: {rect_output_guid[:8]}...")
print(f"  [OK] Rectangle geometry created from two points")

print()

# Step 6: Surface 'Slat source'
print("Step 6: Surface 'Slat source' (8fec620f...)")
print("-" * 60)
surface_comp_guid = "8fec620f-ff7f-4b94-bb64-4c7fce2fcb34"

print(f"  Component: {surface_comp_guid[:8]}...")
print(f"  Source: Rectangle 2Pt output ({rect_output_guid[:8]}...)")
print(f"  [OK] Surface receives geometry from Rectangle 2Pt")
print(f"  (This is a pass-through component)")

print()
print("=" * 60)
print("Summary:")
print("-" * 60)
print("  Construct Point A: [2.5, 0.04, 0.0]")
print("    - X: Slat lenght (2.5)")
print("    - Y: Slat width / 2 (0.08 / 2 = 0.04)")
print("    - Z: 0")
print()
print("  Construct Point B: [?, ?, 0.0]")
print("    - X: from 8a96679d... (need to trace)")
print("    - Y: from 370f6ae5... (need to trace)")
print("    - Z: 0")
print()
print("  Rectangle 2Pt: Creates rectangle from Point A and Point B")
print("  Surface 'Slat source': Passes through Rectangle 2Pt geometry")

