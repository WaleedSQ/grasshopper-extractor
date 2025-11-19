"""
Evaluate just the "Slat lenght" calculation to verify the output.
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, get_external_inputs, evaluate_graph
import json

# Load the graph
graph_data = load_component_graph('complete_component_graph.json')
# Graph structure: {'components': {...}, 'sorted_order': [...]}
graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

# Load all objects from rotatingslats_data.json
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

# Find the Division component
division_comp_guid = "32cc502c-07b0-4d58-aef1-8acf8b2f4015"
output_guid = "4c2fdd4e-7313-4735-8688-1dbdf5aeaee0"

print("=" * 60)
print("Evaluating 'Slat lenght' Calculation")
print("=" * 60)
print()

# Check if component is in graph (might be nested)
comp_found = None
for key, value in graph.items():
    if key == division_comp_guid:
        comp_found = value
        break
    elif isinstance(value, dict) and value.get('instance_guid') == division_comp_guid:
        comp_found = value
        break

if comp_found:
    comp_info = comp_found
    # comp_info already set above
    print(f"Division Component ({division_comp_guid[:8]}...):")
    print("-" * 60)
    print(f"  Type: {comp_info.get('obj', {}).get('type', 'Unknown')}")
    print(f"  Nickname: {comp_info.get('obj', {}).get('nickname', '')}")
    print()
    
    # Get inputs
    inputs = comp_info.get('inputs', {})
    print("  Inputs:")
    for input_key, input_info in inputs.items():
        input_name = input_info.get('name', 'Unknown')
        sources = input_info.get('sources', [])
        print(f"    {input_name}:")
        for source in sources:
            source_guid = source.get('source_guid')
            source_type = source.get('type', 'unknown')
            source_name = source.get('source_obj_name', '')
            print(f"      Source: {source_guid[:8] if source_guid else 'N/A'}... ({source_type}) {source_name}")
    
    # Check for constant in input B
    if 'param_input_1' in inputs:
        param_b = inputs['param_input_1']
        persistent_values = param_b.get('persistent_values', [])
        if persistent_values:
            print(f"    Input B constant: {persistent_values[0]}")
    
    print()
    print("  Expected Calculation:")
    print(f"    room width (5.0) / 2 = 2.5")
    print()
    
    # Evaluate the component
    print("  Evaluating component...")
    try:
        from evaluate_rotatingslats import evaluate_component, resolve_input_value, get_external_inputs
        from collections import defaultdict
        
        external_inputs = get_external_inputs()
        evaluated = {}
        
        # Resolve inputs
        resolved_inputs = {}
        for input_key, input_info in inputs.items():
            input_name = input_info.get('name', 'Unknown')
            value = resolve_input_value(
                division_comp_guid, 
                input_key, 
                comp_info,
                evaluated,
                all_objects,
                output_params,
                input_info
            )
            resolved_inputs[input_name] = value
            print(f"    {input_name} = {value}")
        
        # Evaluate
        result = evaluate_component(
            division_comp_guid,
            comp_info,
            evaluated,
            all_objects,
            output_params
        )
        
        print()
        print("  Result:")
        print(f"    {result}")
        
        # Check output parameter
        if output_guid in output_params:
            print()
            print(f"  Output parameter ({output_guid[:8]}...):")
            print(f"    This feeds into 'Slat lenght' Number component")
            if isinstance(result, dict):
                result_value = result.get('Result') or list(result.values())[0] if result else None
                print(f"    Value: {result_value}")
        else:
            print()
            print(f"  [WARNING] Output parameter {output_guid[:8]}... not found in output_params")
            
    except Exception as e:
        print(f"  [ERROR] Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"[X] Division component {division_comp_guid[:8]}... not found in graph")

print()
print("=" * 60)

