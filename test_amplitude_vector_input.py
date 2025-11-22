#!/usr/bin/env python3
"""Test if Amplitude component's Vector input is being resolved correctly."""

import json
from evaluate_rotatingslats import load_component_graph, resolve_input_value, evaluate_component, get_external_inputs

# Load graph
graph_data = load_component_graph('complete_component_graph.json')
graph = graph_data.get('components', graph_data)

all_objects = {}
for comp_id, comp_data in graph.items():
    if isinstance(comp_data, dict) and 'obj' in comp_data:
        all_objects[comp_id] = comp_data['obj']

# Build output_params
output_params = {}
for comp_id, comp_data in graph.items():
    if isinstance(comp_data, dict) and 'obj' in comp_data:
        obj = comp_data['obj']
        params = obj.get('params', {})
        for param_key, param_info in params.items():
            if param_key.startswith('param_output'):
                param_guid = param_info.get('data', {}).get('InstanceGuid')
                if param_guid:
                    output_params[param_guid] = {
                        'obj': obj,
                        'param_key': param_key,
                        'param_info': param_info
                    }

evaluated = {}

print("=" * 80)
print("TESTING AMPLITUDE COMPONENT VECTOR INPUT RESOLUTION")
print("=" * 80)

# Find Amplitude component
amplitude_guid = None
for comp_id, comp_data in graph.items():
    if isinstance(comp_data, dict):
        obj = comp_data.get('obj', {})
        if obj.get('instance_guid') == 'f54babb4-b955-42d1-aeb1-3b2192468fed':
            amplitude_guid = comp_id
            break

if amplitude_guid:
    print(f"\nAmplitude component found: {amplitude_guid[:8]}...")
    comp_info = graph[amplitude_guid]
    
    # Resolve Vector input
    print("\nResolving Vector input (param_input_0):")
    try:
        vector_value = resolve_input_value(amplitude_guid, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"  Vector value: {vector_value}")
        print(f"  Type: {type(vector_value).__name__}")
        if isinstance(vector_value, list) and len(vector_value) > 0:
            print(f"  Length: {len(vector_value)}")
            if len(vector_value) == 3:
                print(f"  Expected: [11.32743, -27.346834, 0.0]")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Resolve Amplitude input
    print("\nResolving Amplitude input (param_input_1):")
    try:
        amplitude_value = resolve_input_value(amplitude_guid, 'param_input_1', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"  Amplitude value: {amplitude_value}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Evaluate Amplitude component
    print("\nEvaluating Amplitude component:")
    try:
        result = evaluate_component(amplitude_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"  Result: {result}")
        if isinstance(result, dict):
            vector_output = result.get('Vector')
            print(f"  Vector output: {vector_output}")
            print(f"  Expected: [11.32743, -27.346834, 0.0]")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Amplitude component not found!")



