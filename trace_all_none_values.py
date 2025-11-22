"""
Trace all None values from first inputs to last outputs.
"""
import json
from collections import defaultdict

# Load data
with open('complete_component_graph.json', 'r') as f:
    graph_data = json.load(f)
    graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

with open('rotatingslats_data.json', 'r') as f:
    data = json.load(f)
    all_objects = {}
    all_objects.update(data.get('group_objects', {}))
    all_objects.update(data.get('external_objects', {}))

# Load evaluation results
with open('evaluation_results.md', 'r') as f:
    results_content = f.read()

# Parse evaluation results
evaluated = {}
current_comp_id = None
for line in results_content.split('\n'):
    if line.startswith('## Component '):
        # Extract full GUID (8 chars + ...)
        comp_id_part = line.split('Component ')[1].strip()
        # Try to find full GUID in graph
        current_comp_id = None
        for comp_key, comp_data in graph.items():
            if isinstance(comp_data, dict):
                instance_guid = comp_data.get('obj', {}).get('instance_guid', '')
                if instance_guid and instance_guid.startswith(comp_id_part[:8]):
                    current_comp_id = instance_guid
                    break
        if not current_comp_id:
            # Try all_objects
            for obj_key, obj in all_objects.items():
                instance_guid = obj.get('instance_guid', '')
                if instance_guid and instance_guid.startswith(comp_id_part[:8]):
                    current_comp_id = instance_guid
                    break
        if current_comp_id and current_comp_id not in evaluated:
            evaluated[current_comp_id] = {}
    elif line.startswith('- ') and ':' in line and current_comp_id:
        key, value_str = line[2:].split(':', 1)
        key = key.strip()
        value_str = value_str.strip()
        if value_str == 'None':
            evaluated[current_comp_id][key] = None
        elif value_str.startswith('[') or value_str.startswith('{'):
            try:
                evaluated[current_comp_id][key] = eval(value_str)
            except:
                evaluated[current_comp_id][key] = value_str
        else:
            try:
                evaluated[current_comp_id][key] = float(value_str)
            except:
                evaluated[current_comp_id][key] = value_str

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

# Find all components with None outputs
none_components = []
for comp_id, result in evaluated.items():
    if isinstance(result, dict):
        for key, value in result.items():
            if value is None:
                none_components.append((comp_id, key, result))
    elif result is None:
        none_components.append((comp_id, 'Result', None))

print("=" * 80)
print("TRACING ALL NONE VALUES")
print("=" * 80)
print(f"\nTotal evaluated components: {len(evaluated)}")
print(f"Found {len(none_components)} components with None outputs\n")

if len(none_components) == 0:
    print("No None values found. Checking all evaluated components...")
    for comp_id, result in list(evaluated.items())[:10]:
        print(f"  {comp_id[:8]}...: {result}")
    print()

# Trace each None value
for comp_id, output_key, result in none_components:
    print("=" * 80)
    print(f"Component: {comp_id[:8]}...")
    
    # Find component info
    comp_info = None
    for comp_key, comp_data in graph.items():
        if isinstance(comp_data, dict):
            instance_guid = comp_data.get('obj', {}).get('instance_guid')
            if instance_guid == comp_id:
                comp_info = comp_data
                break
    
    if not comp_info:
        for obj_key, obj in all_objects.items():
            if obj.get('instance_guid') == comp_id:
                comp_info = {'obj': obj}
                break
    
    if comp_info:
        comp_type = comp_info.get('obj', {}).get('type', 'Unknown')
        comp_nickname = comp_info.get('obj', {}).get('nickname', '')
        print(f"Type: {comp_type}")
        print(f"Nickname: {comp_nickname}")
        print(f"None output: {output_key}")
        print()
        
        # Trace inputs
        print("  Tracing inputs:")
        obj_params = comp_info.get('obj', {}).get('params', {})
        for param_key, param_info in obj_params.items():
            if param_key.startswith('param_input'):
                param_name = param_info.get('data', {}).get('NickName', '') or param_info.get('data', {}).get('Name', '')
                sources = param_info.get('sources', [])
                persistent_values = param_info.get('persistent_values', [])
                
                print(f"    {param_name}:")
                
                # Check sources
                if sources:
                    for source in sources:
                        source_guid = source.get('guid') or source.get('source_guid')
                        if source_guid:
                            print(f"      Source GUID: {source_guid[:8]}...")
                            
                            # Check if it's an output param
                            if source_guid in output_params:
                                source_info = output_params[source_guid]
                                source_obj = source_info['obj']
                                source_comp_guid = source_obj.get('instance_guid')
                                print(f"        Output param from component: {source_comp_guid[:8]}...")
                                
                                # Check if source component is evaluated
                                if source_comp_guid in evaluated:
                                    source_result = evaluated[source_comp_guid]
                                    print(f"        Source component evaluated: {source_result}")
                                    
                                    # Extract value
                                    if isinstance(source_result, dict):
                                        for key in ['Result', 'Value', 'Output', 'Geometry', 'Rectangle', 'Vector', 'Point', 'Plane']:
                                            if key in source_result:
                                                print(f"        Found value in '{key}': {source_result[key]}")
                                                break
                                else:
                                    print(f"        [MISSING] Source component NOT evaluated")
                                    print(f"        Source component type: {source_obj.get('type', 'Unknown')}")
                                    print(f"        Source component nickname: {source_obj.get('nickname', '')}")
                            else:
                                # Check if source_guid is directly in evaluated
                                if source_guid in evaluated:
                                    print(f"        Direct evaluation: {evaluated[source_guid]}")
                                else:
                                    print(f"        [MISSING] Source GUID not found in evaluated")
                                    
                                    # Try to find component by GUID
                                    found_comp = None
                                    for comp_key, comp_data in graph.items():
                                        if isinstance(comp_data, dict):
                                            instance_guid = comp_data.get('obj', {}).get('instance_guid')
                                            if instance_guid == source_guid:
                                                found_comp = comp_data
                                                break
                                    
                                    if found_comp:
                                        print(f"        Found component: {found_comp.get('obj', {}).get('type', 'Unknown')}")
                                        print(f"        Component evaluated: {found_comp.get('obj', {}).get('instance_guid') in evaluated}")
                                    else:
                                        print(f"        [NOT FOUND] Component not found in graph")
                
                # Check persistent values
                if persistent_values and not sources:
                    print(f"      Persistent values: {persistent_values}")
                
                # Check external inputs
                try:
                    with open('external_inputs.json', 'r') as f:
                        external_inputs = json.load(f)
                        param_guid = param_info.get('data', {}).get('InstanceGuid')
                        if param_guid and param_guid in external_inputs:
                            print(f"      External input: {external_inputs[param_guid]}")
                except:
                    pass
                
                print()
    else:
        print(f"[NOT FOUND] Component not found in graph or all_objects")
    
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total components with None outputs: {len(none_components)}")
print("\nComponents by type:")
type_counts = defaultdict(int)
for comp_id, output_key, result in none_components:
    comp_info = None
    for comp_key, comp_data in graph.items():
        if isinstance(comp_data, dict):
            instance_guid = comp_data.get('obj', {}).get('instance_guid')
            if instance_guid == comp_id:
                comp_info = comp_data
                break
    if not comp_info:
        for obj_key, obj in all_objects.items():
            if obj.get('instance_guid') == comp_id:
                comp_info = {'obj': obj}
                break
    if comp_info:
        comp_type = comp_info.get('obj', {}).get('type', 'Unknown')
        type_counts[comp_type] += 1

for comp_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  {comp_type}: {count}")

