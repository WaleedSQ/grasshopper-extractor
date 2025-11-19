"""
Debug the Motion input to second Move "Slats original" (0532cbdf...) in full evaluation context.
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, get_external_inputs, topological_sort, evaluate_component, resolve_input_value

# Load everything
graph_data = load_component_graph('complete_component_graph.json')
graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

with open('rotatingslats_data.json', 'r') as f:
    data = json.load(f)
    all_objects = {}
    all_objects.update(data.get('group_objects', {}))
    all_objects.update(data.get('external_objects', {}))

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

# Get topological sort
sorted_components = topological_sort(graph_data, all_objects, output_params)

print("=" * 80)
print("DEBUGGING SECOND MOVE 'Slats original' MOTION INPUT")
print("=" * 80)

# Find second Move component (instance_guid: 0532cbdf-875b-4db9-8c88-352e21051436)
second_move_instance_guid = '0532cbdf-875b-4db9-8c88-352e21051436'
second_move_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == second_move_instance_guid:
            second_move_guid = comp_id  # This is the component ID in the graph
            break

if not second_move_guid:
    print("ERROR: Could not find second Move component")
    # Try to find by searching all_objects
    for obj_key, obj in all_objects.items():
        if obj.get('instance_guid') == second_move_instance_guid:
            print(f"Found in all_objects: {obj_key[:8]}...")
            break
    sys.exit(1)

# Find Amplitude component (instance_guid: f54babb4-b955-42d1-aeb1-3b2192468fed)
amplitude_guid = None
amplitude_output_guid = 'd0668a07-838c-481c-88eb-191574362cc2'
amplitude_instance_guid = 'f54babb4-b955-42d1-aeb1-3b2192468fed'
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == amplitude_instance_guid:
            amplitude_guid = amplitude_instance_guid  # Use instance_guid, not comp_id
            break

print(f"\nSecond Move component ID: {second_move_guid[:8]}...")
print(f"Amplitude component ID: {amplitude_guid[:8] if amplitude_guid else 'N/A'}...")

# Evaluate components in order up to Amplitude
print("\nEvaluating components in topological order...")
for comp_id in sorted_components:
    if comp_id == amplitude_guid:
            print(f"\nEvaluating Amplitude ({comp_id[:8]}...):")
            comp_info = graph[comp_id]
            try:
                result = evaluate_component(comp_id, comp_info, evaluated, all_objects, output_params, graph=graph)
                evaluated[amplitude_instance_guid] = result
                evaluated[comp_id] = result
                if isinstance(result, dict):
                    amp_vector = result.get('Vector')
                    print(f"  Amplitude Vector output: {amp_vector}")
                    # Also store by output GUID
                    if amplitude_output_guid in output_params:
                        evaluated[amplitude_output_guid] = result
            except Exception as e:
                print(f"  Error: {e}")
    
    # Check if this is the second Move component
    comp_info_check2 = graph.get(comp_id, {})
    if isinstance(comp_info_check2, dict):
        obj_check2 = comp_info_check2.get('obj', {})
        if obj_check2.get('instance_guid') == second_move_instance_guid:
            print(f"\nEvaluating second Move ({comp_id[:8]}...):")
            comp_info = graph[comp_id]
            
            # Check Motion input before evaluation
            print("  Resolving Motion input:")
            try:
                motion_value = resolve_input_value(comp_id, 'param_input_1', comp_info, evaluated, all_objects, output_params, graph=graph)
                print(f"    Motion value: {motion_value}")
                print(f"    Type: {type(motion_value).__name__}")
                if isinstance(motion_value, list):
                    if len(motion_value) == 3:
                        print(f"    Single vector: {motion_value}")
                        print(f"    Expected: [11.32743, -27.346834, 0.0]")
                    elif len(motion_value) > 0 and isinstance(motion_value[0], list):
                        print(f"    List of vectors, length: {len(motion_value)}")
                        print(f"    First: {motion_value[0]}")
            except Exception as e:
                print(f"    Error resolving Motion: {e}")
            
            # Evaluate Move component
            try:
                result = evaluate_component(comp_id, comp_info, evaluated, all_objects, output_params, graph=graph)
                evaluated[second_move_instance_guid] = result
                evaluated[comp_id] = result
                if isinstance(result, dict) and 'Geometry' in result:
                    geom = result['Geometry']
                    print(f"  Move output: {len(geom) if isinstance(geom, list) else 'single'} geometry/geometries")
            except Exception as e:
                print(f"  Error evaluating Move: {e}")
                import traceback
                traceback.print_exc()
            break

print("\n" + "=" * 80)

