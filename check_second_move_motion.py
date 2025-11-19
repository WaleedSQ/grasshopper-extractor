"""
Check if the second Move "Slats original" (0532cbdf...) is receiving correct Motion input from Amplitude.
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
print("CHECKING SECOND MOVE 'Slats original' (0532cbdf...) MOTION INPUT")
print("=" * 80)

# Find the second Move component
second_move_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == '0532cbdf-875b-4db9-8c88-352e21051436':
            second_move_guid = comp_id
            break

if not second_move_guid:
    print("ERROR: Could not find second Move 'Slats original' component")
    sys.exit(1)

print(f"\nComponent ID: {second_move_guid[:8]}...")
comp_info = graph[second_move_guid]

# Check Amplitude output (d0668a07...)
print("\n1. AMPLITUDE OUTPUT (d0668a07-838c-481c-88eb-191574362cc2):")
amplitude_output_guid = 'd0668a07-838c-481c-88eb-191574362cc2'
if amplitude_output_guid in output_params:
    amp_info = output_params[amplitude_output_guid]
    amp_comp_guid = amp_info['obj'].get('instance_guid')
    print(f"   Amplitude component GUID: {amp_comp_guid[:8] if amp_comp_guid else 'N/A'}...")
    
    # Find and evaluate Amplitude component
    amp_comp = None
    for comp_id, comp in graph.items():
        if isinstance(comp, dict) and comp.get('obj', {}).get('instance_guid') == amp_comp_guid:
            amp_comp = comp
            break
    
    if amp_comp:
        try:
            amp_result = evaluate_component(amp_comp_guid, amp_comp, evaluated, all_objects, output_params, graph=graph)
            evaluated[amp_comp_guid] = amp_result
            if isinstance(amp_result, dict):
                amp_vector = amp_result.get('Vector')
                print(f"   Amplitude Vector output: {amp_vector}")
                print(f"   Expected: [11.32743, -27.346834, 0.0]")
            else:
                print(f"   Amplitude result: {amp_result}")
        except Exception as e:
            print(f"   Error evaluating Amplitude: {e}")
    else:
        print(f"   Could not find Amplitude component")
else:
    print(f"   Could not find Amplitude output parameter")

# Check Motion input resolution
print("\n2. MOTION INPUT RESOLUTION:")
try:
    motion_value = resolve_input_value(second_move_guid, 'param_input_1', comp_info, evaluated, all_objects, output_params, graph=graph)
    print(f"   Resolved Motion value: {motion_value}")
    print(f"   Type: {type(motion_value).__name__}")
    if isinstance(motion_value, list):
        if len(motion_value) > 0:
            if isinstance(motion_value[0], list):
                print(f"   List of vectors, length: {len(motion_value)}")
                print(f"   First vector: {motion_value[0]}")
                print(f"   Expected first: [11.32743, -27.346834, 3.8]")
            elif len(motion_value) == 3:
                print(f"   Single vector: {motion_value}")
                print(f"   Expected: [11.32743, -27.346834, 0.0] (from Amplitude)")
except Exception as e:
    print(f"   Error resolving Motion: {e}")
    import traceback
    traceback.print_exc()

# Check Geometry input
print("\n3. GEOMETRY INPUT:")
try:
    geometry_value = resolve_input_value(second_move_guid, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
    print(f"   Geometry type: {type(geometry_value).__name__}")
    if isinstance(geometry_value, dict):
        print(f"   Geometry keys: {list(geometry_value.keys())[:5]}")
    elif isinstance(geometry_value, list):
        print(f"   Geometry list length: {len(geometry_value)}")
except Exception as e:
    print(f"   Error resolving Geometry: {e}")

# Evaluate the Move component
print("\n4. MOVE COMPONENT EVALUATION:")
try:
    result = evaluate_component(second_move_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
    evaluated[second_move_guid] = result
    if isinstance(result, dict) and 'Geometry' in result:
        geom = result['Geometry']
        print(f"   Output Geometry type: {type(geom).__name__}")
        if isinstance(geom, list) and len(geom) > 0:
            print(f"   Number of geometries: {len(geom)}")
            if isinstance(geom[0], dict):
                # Check first geometry's corners or points
                first_geom = geom[0]
                if 'corners' in first_geom:
                    corners = first_geom['corners']
                    if corners and len(corners) > 0:
                        print(f"   First geometry first corner: {corners[0]}")
                        print(f"   Expected: should be moved by Motion vector")
except Exception as e:
    print(f"   Error evaluating Move: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print("The Move component should receive Motion = Amplitude [11.32743, -27.346834, 0.0]")
print("When combined with Unit Z [[0.0, 0.0, 3.8], ...], it should create:")
print("  [[11.32743, -27.346834, 3.8], [11.32743, -27.346834, 3.722222], ...]")
print("\nThe centroids should then be: [11.32743, -27.416834, 3.8], ...")

