"""
Simple test to verify Amplitude resolution fix works.
Tests the resolve_input_value function directly.
"""

import json
from evaluate_rotatingslats import load_component_graph, resolve_input_value, get_external_inputs

# Load graph
graph_data = load_component_graph('complete_component_graph.json')
graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

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

# Find "Targets" Move component
targets_move_guid = 'b38a38f1-ced5-4600-a687-4ebc4d73e6ff'
targets_move_key = None
for k, v in graph.items():
    if isinstance(v, dict) and v.get('obj', {}).get('instance_guid') == targets_move_guid:
        targets_move_key = k
        break

print("=" * 80)
print("TESTING AMPLITUDE RESOLUTION FIX")
print("=" * 80)

if targets_move_key:
    print(f"\nTargets Move found: {targets_move_key[:20]}...")
    comp_info = graph[targets_move_key]
    evaluated = {}
    
    # Try to resolve Motion input
    print(f"\nResolving Motion input (param_input_1)...")
    try:
        motion_value = resolve_input_value(
            targets_move_key, 'param_input_1', comp_info, 
            evaluated, all_objects, output_params, graph=graph
        )
        print(f"  [OK] Motion value resolved: {motion_value}")
        if isinstance(motion_value, list) and len(motion_value) == 3:
            print(f"  Expected: [11.32743, -27.346834, 0.0] (from Amplitude)")
            print(f"  Got: {motion_value}")
            if abs(motion_value[0] - 11.32743) < 0.1 and abs(motion_value[1] - (-27.346834)) < 0.1:
                print(f"  [SUCCESS] Amplitude resolved correctly!")
            else:
                print(f"  [WARNING] Values don't match expected Amplitude output")
    except Exception as e:
        print(f"  [ERROR] Failed to resolve: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n[ERROR] Targets Move NOT found")

print("\n" + "=" * 80)
print("The fix should now resolve Amplitude through output parameter GUID")
print("'d0668a07-838c-481c-88eb-191574362cc2' for both Move components.")
print("=" * 80)


