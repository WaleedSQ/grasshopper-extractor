"""
Test Degrees component Radians input resolution.
"""

import json
from evaluate_rotatingslats import (
    load_component_graph, resolve_input_value, 
    get_external_inputs, topological_sort, evaluate_component
)

# Load graph
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

# Find Degrees component
degrees_guid = 'fa0ba5a6-7dd9-43f4-a82a-cf02841d0f58'
degrees_key = None
for k, v in graph.items():
    if isinstance(v, dict) and v.get('obj', {}).get('instance_guid') == degrees_guid:
        degrees_key = k
        break

print("=" * 80)
print("TESTING DEGREES COMPONENT")
print("=" * 80)

if degrees_key:
    print(f"\nDegrees component found: {degrees_key[:20]}...")
    comp_info = graph[degrees_key]
    
    # Check Radians input (param_input_0)
    print(f"\nRadians Input (param_input_0):")
    param_info = comp_info['obj'].get('params', {}).get('param_input_0', {})
    sources = param_info.get('sources', [])
    print(f"  Sources: {len(sources)}")
    for src in sources:
        source_guid = src.get('guid')
        print(f"    Source GUID: {source_guid}")
        if source_guid == '23900bd5-6845-4b37-a9ba-bc8342e17168':
            print(f"      [OK] This is Angle output parameter")
            if source_guid in output_params:
                angle_info = output_params[source_guid]
                angle_parent_guid = angle_info['obj'].get('instance_guid')
                angle_parent_type = angle_info['obj'].get('type')
                angle_param_name = angle_info['param_info'].get('data', {}).get('NickName', 'N/A')
                print(f"      Parent: {angle_parent_guid} ({angle_parent_type})")
                print(f"      Output param name: {angle_param_name}")
    
    # Get topological sort - need to pass graph with 'components' key
    graph_for_sort = {'components': graph}
    sorted_components = topological_sort(graph_for_sort, all_objects, output_params)
    
    # Evaluate dependencies first
    evaluated = {}
    for comp_id in sorted_components:
        if comp_id == degrees_key:
            break
        if comp_id in graph:
            try:
                result = evaluate_component(comp_id, graph[comp_id], evaluated, all_objects, output_params, graph=graph)
                print(f"  Evaluated {comp_id[:8]}... ({graph[comp_id].get('obj', {}).get('type', 'Unknown')})")
            except Exception as e:
                print(f"  Error evaluating {comp_id[:8]}...: {e}")
    
    # Check if Angle component is evaluated
    angle_parent_guid = '0d695e6b-3696-4337-bc80-d14104f8a59e'
    if angle_parent_guid in evaluated:
        print(f"\nAngle component ({angle_parent_guid[:8]}...) is evaluated:")
        angle_output = evaluated[angle_parent_guid]
        print(f"  Output type: {type(angle_output).__name__}")
        if isinstance(angle_output, dict):
            print(f"  Output keys: {list(angle_output.keys())}")
            print(f"  Angle value: {angle_output.get('Angle', 'N/A')}")
    else:
        print(f"\n[ERROR] Angle component ({angle_parent_guid[:8]}...) is NOT evaluated")
    
    # Try to resolve Radians input
    print(f"\nResolving Radians input...")
    try:
        radians_value = resolve_input_value(
            degrees_key, 'param_input_0', comp_info, 
            evaluated, all_objects, output_params, graph=graph
        )
        print(f"  [OK] Radians value resolved: {radians_value}")
        print(f"  Type: {type(radians_value).__name__}")
    except Exception as e:
        print(f"  [ERROR] Failed to resolve: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n[ERROR] Degrees component NOT found")

