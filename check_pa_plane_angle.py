"""
Check the locally defined (PersistentData) values for Plane and Angle inputs in Polar Array.
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

print("=" * 80)
print("CHECKING POLAR ARRAY PLANE AND ANGLE INPUTS")
print("=" * 80)

# Find Polar Array component
polar_array_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == 'b4a4862a-3bba-4868-943f-cf86bdc99cf3':
            polar_array_guid = comp_id
            break

if polar_array_guid:
    print(f"\nPolar Array component ID: {polar_array_guid[:8]}...")
    comp_info = graph[polar_array_guid]
    
    # Check Plane input (param_input_1)
    print("\n1. PLANE INPUT (param_input_1):")
    param_info = comp_info['obj'].get('params', {}).get('param_input_1', {})
    sources = param_info.get('sources', [])
    persistent_values = param_info.get('persistent_values', [])
    values = param_info.get('values', [])
    print(f"  Sources: {len(sources)}")
    print(f"  Persistent values: {persistent_values}")
    print(f"  Values: {values}")
    
    # Check what's in the raw GHX data
    print("\n  From GHX file (core-only_trimmed2.ghx):")
    print("  PersistentData contains:")
    print("    - plane type: gh_plane")
    print("    - Origin: (0, 0, 0)")
    print("    - X-axis: (1, 0, 0)")
    print("    - Y-axis: (0, 1, 0)")
    print("    - Z-axis: (0, 0, 1) [implied]")
    
    # Try to resolve the Plane input
    try:
        plane_value = resolve_input_value(polar_array_guid, 'param_input_1', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"\n  Resolved Plane value: {plane_value}")
        print(f"  Type: {type(plane_value).__name__}")
        if isinstance(plane_value, dict):
            print(f"  Keys: {list(plane_value.keys())}")
            if 'origin' in plane_value:
                print(f"  Origin: {plane_value['origin']}")
    except Exception as e:
        print(f"  Error resolving Plane: {e}")
    
    # Check Angle input (param_input_3)
    print("\n2. ANGLE INPUT (param_input_3):")
    param_info = comp_info['obj'].get('params', {}).get('param_input_3', {})
    sources = param_info.get('sources', [])
    persistent_values = param_info.get('persistent_values', [])
    values = param_info.get('values', [])
    print(f"  Sources: {len(sources)}")
    print(f"  Persistent values: {persistent_values}")
    print(f"  Values: {values}")
    
    # Check what's in the raw GHX data
    print("\n  From GHX file (core-only_trimmed2.ghx):")
    print("  PersistentData contains:")
    print("    - number type: gh_double")
    print("    - Value: 6.283185307179586")
    print("    - This is 2*pi radians = 360 degrees (full circle)")
    
    # Try to resolve the Angle input
    try:
        angle_value = resolve_input_value(polar_array_guid, 'param_input_3', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"\n  Resolved Angle value: {angle_value}")
        print(f"  Type: {type(angle_value).__name__}")
        if isinstance(angle_value, (int, float)):
            import math
            print(f"  In degrees: {math.degrees(angle_value)}")
    except Exception as e:
        print(f"  Error resolving Angle: {e}")
    
    # Check if these values are being used correctly in evaluation
    print("\n3. CHECKING IF VALUES ARE USED IN EVALUATION:")
    print("  The Polar Array component should:")
    print("    - Use Plane from PersistentData (no sources)")
    print("    - Use Angle from PersistentData (no sources)")
    print("    - Use Count from source (8.0 from Number of orientations)")
    
    # Check the actual evaluation
    try:
        geometry_input = resolve_input_value(polar_array_guid, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
        plane_input = resolve_input_value(polar_array_guid, 'param_input_1', comp_info, evaluated, all_objects, output_params, graph=graph)
        count_input = resolve_input_value(polar_array_guid, 'param_input_2', comp_info, evaluated, all_objects, output_params, graph=graph)
        angle_input = resolve_input_value(polar_array_guid, 'param_input_3', comp_info, evaluated, all_objects, output_params, graph=graph)
        
        print(f"\n  Resolved inputs:")
        print(f"    Geometry: {type(geometry_input).__name__}")
        print(f"    Plane: {plane_input}")
        print(f"    Count: {count_input}")
        print(f"    Angle: {angle_input}")
        
        if isinstance(angle_input, (int, float)):
            import math
            print(f"    Angle (degrees): {math.degrees(angle_input)}")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

