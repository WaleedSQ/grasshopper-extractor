"""
Test how "Targets" Move component resolves Amplitude output parameter GUID.
Compare with "Slats original" Move to ensure same resolution logic.
"""

import json
from evaluate_rotatingslats import load_component_graph

# Load graph
graph_data = load_component_graph('complete_component_graph.json')
graph = graph_data.get('components', graph_data)

# Find "Targets" Move component
targets_move_guid = 'b38a38f1-ced5-4600-a687-4ebc4d73e6ff'
targets_move = None
for k, v in graph.items():
    if isinstance(v, dict):
        obj = v.get('obj', {})
        if obj.get('instance_guid') == targets_move_guid:
            targets_move = {'key': k, 'data': v}
            break

print("=" * 80)
print("TARGETS MOVE COMPONENT - AMPLITUDE RESOLUTION")
print("=" * 80)

if targets_move:
    print(f"\nTargets Move found: {targets_move['key'][:20]}...")
    motion_param = targets_move['data']['obj'].get('params', {}).get('param_input_1', {})
    sources = motion_param.get('sources', [])
    print(f"\nMotion input sources: {len(sources)}")
    for i, s in enumerate(sources):
        source_guid = s.get('source_guid') or s.get('guid')
        source_obj_guid = s.get('source_obj_guid')
        print(f"  Source {i}:")
        print(f"    source_guid: {source_guid}")
        print(f"    source_obj_guid: {source_obj_guid}")
        if source_guid == 'd0668a07-838c-481c-88eb-191574362cc2':
            print(f"    [OK] This is Amplitude output parameter GUID")
    
    # Check if Amplitude output param is in output_params
    print("\nChecking output_params for Amplitude output parameter GUID:")
    # Build output_params
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
    
    amplitude_output_guid = 'd0668a07-838c-481c-88eb-191574362cc2'
    if amplitude_output_guid in output_params:
        print(f"  [OK] Amplitude output param found in output_params")
        info = output_params[amplitude_output_guid]
        parent_guid = info['obj'].get('instance_guid')
        parent_type = info['obj'].get('type')
        print(f"  Parent component instance_guid: {parent_guid}")
        print(f"  Parent component type: {parent_type}")
        print(f"  Output param name: {info['param_info'].get('data', {}).get('NickName', 'N/A')}")
    else:
        print(f"  [ERROR] Amplitude output param NOT found in output_params")

# Find "Slats original" Move component
slats_original_guid = '0532cbdf-875b-4db9-8c88-352e21051436'
slats_original = None
for k, v in graph.items():
    if isinstance(v, dict):
        obj = v.get('obj', {})
        if obj.get('instance_guid') == slats_original_guid:
            slats_original = {'key': k, 'data': v}
            break

print("\n" + "=" * 80)
print("SLATS ORIGINAL MOVE COMPONENT - AMPLITUDE RESOLUTION")
print("=" * 80)

if slats_original:
    print(f"\nSlats original Move found: {slats_original['key'][:20]}...")
    motion_param = slats_original['data']['obj'].get('params', {}).get('param_input_1', {})
    sources = motion_param.get('sources', [])
    print(f"\nMotion input sources: {len(sources)}")
    for i, s in enumerate(sources):
        source_guid = s.get('source_guid') or s.get('guid')
        source_obj_guid = s.get('source_obj_guid')
        print(f"  Source {i}:")
        print(f"    source_guid: {source_guid}")
        print(f"    source_obj_guid: {source_obj_guid}")
        if source_guid == 'd0668a07-838c-481c-88eb-191574362cc2':
            print(f"    [OK] This is Amplitude output parameter GUID")
        elif source_obj_guid == 'f54babb4-b955-42d1-aeb1-3b2192468fed':
            print(f"    [OK] This is Amplitude component instance_guid")
else:
    print("\n[ERROR] Slats original Move NOT found")

print("\n" + "=" * 80)
print("COMPARISON")
print("=" * 80)
print("\nBoth Move components should resolve Amplitude the same way:")
print("  1. Check if source_guid == 'd0668a07-838c-481c-88eb-191574362cc2' (Amplitude output param GUID)")
print("  2. If found in output_params, get parent component instance_guid")
print("  3. Evaluate parent component if not already evaluated")
print("  4. Extract 'Vector' output from evaluated result")


