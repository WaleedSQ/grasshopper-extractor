"""
Trace None values during evaluation - run evaluation and trace each None.
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import (
    load_component_graph, get_external_inputs, resolve_input_value,
    evaluate_component, topological_sort, evaluate_graph
)

# Load data
graph_data = load_component_graph('complete_component_graph.json')
graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

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

# Track None values
none_trace = []

def trace_none_value(comp_id, comp_info, result, evaluated):
    """Check if result contains None and trace why."""
    if result is None:
        none_trace.append({
            'comp_id': comp_id,
            'comp_info': comp_info,
            'result': None,
            'reason': 'Result is None'
        })
        return
    
    if isinstance(result, dict):
        for key, value in result.items():
            if value is None:
                none_trace.append({
                    'comp_id': comp_id,
                    'comp_info': comp_info,
                    'output_key': key,
                    'result': result,
                    'reason': f'Output {key} is None'
                })

# Evaluate graph with tracing
evaluated = {}
sorted_components = topological_sort(graph, all_objects, output_params)

import sys
sys.stdout.reconfigure(line_buffering=True)

print("=" * 80, flush=True)
print("TRACING NONE VALUES DURING EVALUATION", flush=True)
print("=" * 80, flush=True)
print(flush=True)

for comp_id in sorted_components:
    comp_info = graph.get('components', graph).get(comp_id)
    if not comp_info or comp_info.get('type') != 'component':
        continue
    
    try:
        result = evaluate_component(comp_id, comp_info, evaluated, all_objects, output_params, graph=graph)
        instance_guid = comp_info.get('obj', {}).get('instance_guid') or comp_id
        evaluated[instance_guid] = result
        
        # Trace None values
        trace_none_value(instance_guid, comp_info, result, evaluated)
        
    except Exception as e:
        instance_guid = comp_info.get('obj', {}).get('instance_guid') or comp_id
        evaluated[instance_guid] = None
        trace_none_value(instance_guid, comp_info, None, evaluated)

# Print trace results
print(f"Found {len(none_trace)} None values\n")

for i, trace in enumerate(none_trace, 1):
    comp_id = trace['comp_id']
    comp_info = trace['comp_info']
    comp_type = comp_info.get('obj', {}).get('type', 'Unknown')
    comp_nickname = comp_info.get('obj', {}).get('nickname', '')
    output_key = trace.get('output_key', 'Result')
    
    print("=" * 80)
    print(f"{i}. Component: {comp_id[:8]}...")
    print(f"   Type: {comp_type}")
    print(f"   Nickname: {comp_nickname}")
    print(f"   None output: {output_key}")
    print(f"   Reason: {trace['reason']}")
    print()
    
    # Trace inputs
    print("   Inputs:")
    obj_params = comp_info.get('obj', {}).get('params', {})
    for param_key, param_info in obj_params.items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('NickName', '') or param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            
            print(f"     {param_name}:")
            
            # Check sources
            if sources:
                for source in sources:
                    source_guid = source.get('guid') or source.get('source_guid')
                    if source_guid:
                        print(f"       Source: {source_guid[:8]}...")
                        
                        # Check if it's an output param
                        if source_guid in output_params:
                            source_info = output_params[source_guid]
                            source_obj = source_info['obj']
                            source_comp_guid = source_obj.get('instance_guid')
                            print(f"         Output param from: {source_comp_guid[:8]}...")
                            
                            # Check if evaluated
                            if source_comp_guid in evaluated:
                                source_result = evaluated[source_comp_guid]
                                if isinstance(source_result, dict):
                                    # Extract value
                                    found_value = None
                                    for key in ['Result', 'Value', 'Output', 'Geometry', 'Rectangle', 'Vector', 'Point', 'Plane']:
                                        if key in source_result:
                                            found_value = source_result[key]
                                            break
                                    if found_value is None:
                                        print(f"         [NONE] Source output is None or empty")
                                    else:
                                        print(f"         [OK] Source output: {type(found_value).__name__}")
                                else:
                                    print(f"         [OK] Source output: {source_result}")
                            else:
                                print(f"         [MISSING] Source component NOT evaluated")
                                print(f"         Source type: {source_obj.get('type', 'Unknown')}")
                                print(f"         Source nickname: {source_obj.get('nickname', '')}")
                        else:
                            # Check if directly evaluated
                            if source_guid in evaluated:
                                print(f"         [OK] Direct evaluation: {evaluated[source_guid]}")
                            else:
                                print(f"         [MISSING] Source GUID not in evaluated")
            else:
                # Check persistent values
                persistent_values = param_info.get('persistent_values', [])
                if persistent_values:
                    print(f"       Persistent values: {persistent_values}")
                else:
                    print(f"       [NO SOURCE] No sources or persistent values")
            print()
    
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total None values: {len(none_trace)}")
print("\nBy component type:")
type_counts = {}
for trace in none_trace:
    comp_type = trace['comp_info'].get('obj', {}).get('type', 'Unknown')
    type_counts[comp_type] = type_counts.get(comp_type, 0) + 1

for comp_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  {comp_type}: {count}")

