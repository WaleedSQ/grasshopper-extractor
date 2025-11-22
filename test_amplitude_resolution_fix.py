"""
Test if Amplitude resolution fix works for both Move components.
"""

import json
from evaluate_rotatingslats import (
    load_component_graph, resolve_input_value, 
    get_external_inputs, topological_sort, evaluate_component
)

# Load graph and external inputs
graph_data = load_component_graph('complete_component_graph.json')
graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data
external_inputs = get_external_inputs()

# Build all_objects and output_params
all_objects = {}
for k, v in graph.items():
    if isinstance(v, dict) and 'obj' in v:
        all_objects[k] = v['obj']

output_params = {}
for comp_id, comp_data in graph.items():
    if isinstance(comp_data, dict) and 'obj' in comp_data:
        obj = comp_data['obj']
        params = obj.get('params', {})
        for param_key, param_info in params.items():
            if param_key.startswith('param_output'):
                param_data = param_info.get('data', {})
                param_guid = param_data.get('InstanceGuid')
                if param_guid:
                    output_params[param_guid] = {
                        'obj': obj,
                        'param_key': param_key,
                        'param_info': param_info
                    }

# Get topological sort
sorted_components = topological_sort(graph, all_objects, output_params)

# Test "Targets" Move component
targets_move_guid = 'b38a38f1-ced5-4600-a687-4ebc4d73e6ff'
targets_move_key = None
for k, v in graph.items():
    if isinstance(v, dict) and v.get('obj', {}).get('instance_guid') == targets_move_guid:
        targets_move_key = k
        break

print("=" * 80)
print("TESTING AMPLITUDE RESOLUTION FOR TARGETS MOVE")
print("=" * 80)

if targets_move_key:
    evaluated = {}
    comp_info = graph[targets_move_key]
    
    # Evaluate dependencies first
    for comp_id in sorted_components:
        if comp_id == targets_move_key:
            break
        if comp_id in graph:
            try:
                evaluate_component(comp_id, graph[comp_id], evaluated, all_objects, output_params, graph=graph)
            except Exception as e:
                pass
    
    # Try to resolve Motion input
    print(f"\nResolving Motion input for Targets Move...")
    try:
        motion_value = resolve_input_value(
            targets_move_key, 'param_input_1', comp_info, 
            evaluated, all_objects, output_params, graph=graph
        )
        print(f"  [OK] Motion value resolved: {motion_value}")
        if isinstance(motion_value, list) and len(motion_value) == 3:
            print(f"  Expected: [11.32743, -27.346834, 0.0] (from Amplitude)")
            print(f"  Got: {motion_value}")
    except Exception as e:
        print(f"  [ERROR] Failed to resolve: {e}")
        import traceback
        traceback.print_exc()

# Test "Slats original" Move component
slats_original_guid = '0532cbdf-875b-4db9-8c88-352e21051436'
slats_original_key = None
for k, v in graph.items():
    if isinstance(v, dict) and v.get('obj', {}).get('instance_guid') == slats_original_guid:
        slats_original_key = k
        break

print("\n" + "=" * 80)
print("TESTING AMPLITUDE RESOLUTION FOR SLATS ORIGINAL MOVE")
print("=" * 80)

if slats_original_key:
    evaluated = {}
    comp_info = graph[slats_original_key]
    
    # Evaluate dependencies first
    for comp_id in sorted_components:
        if comp_id == slats_original_key:
            break
        if comp_id in graph:
            try:
                evaluate_component(comp_id, graph[comp_id], evaluated, all_objects, output_params, graph=graph)
            except Exception as e:
                pass
    
    # Try to resolve Motion input
    print(f"\nResolving Motion input for Slats original Move...")
    try:
        motion_value = resolve_input_value(
            slats_original_key, 'param_input_1', comp_info, 
            evaluated, all_objects, output_params, graph=graph
        )
        print(f"  [OK] Motion value resolved: {motion_value}")
        if isinstance(motion_value, list):
            if len(motion_value) > 0 and isinstance(motion_value[0], list):
                print(f"  List of vectors, length: {len(motion_value)}")
                print(f"  First vector: {motion_value[0]}")
                print(f"  Expected first: [11.32743, -27.416834, 3.8] (Amplitude + Vector 2Pt)")
            elif len(motion_value) == 3:
                print(f"  Single vector: {motion_value}")
    except Exception as e:
        print(f"  [ERROR] Failed to resolve: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nBoth Move components should now resolve Amplitude correctly through")
print("the output parameter GUID 'd0668a07-838c-481c-88eb-191574362cc2'.")

