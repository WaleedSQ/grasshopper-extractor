"""Simple script to trace None values from evaluation results."""
import json
import re

# Load graph
with open('complete_component_graph.json', 'r') as f:
    graph_data = json.load(f)
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

# Parse evaluation results
evaluated = {}
with open('evaluation_results.md', 'r') as f:
    content = f.read()
    
    # Find all component sections
    pattern = r'## Component ([a-f0-9]{8})\.\.\.\n\*\*Nickname:\*\* ([^\n]+)\n\*\*Type:\*\* ([^\n]+)\n\n(.*?)(?=\n## Component |\Z)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        comp_id_short = match.group(1)
        nickname = match.group(2)
        comp_type = match.group(3)
        results_text = match.group(4)
        
        # Find full GUID
        full_guid = None
        for comp_key, comp_data in graph.items():
            if isinstance(comp_data, dict):
                instance_guid = comp_data.get('obj', {}).get('instance_guid', '')
                if instance_guid and instance_guid.startswith(comp_id_short):
                    full_guid = instance_guid
                    break
        if not full_guid:
            for obj_key, obj in all_objects.items():
                instance_guid = obj.get('instance_guid', '')
                if instance_guid and instance_guid.startswith(comp_id_short):
                    full_guid = instance_guid
                    break
        
        if full_guid:
            evaluated[full_guid] = {
                'nickname': nickname,
                'type': comp_type,
                'outputs': {}
            }
            
            # Parse outputs
            for line in results_text.split('\n'):
                if line.startswith('- ') and ':' in line:
                    key, value_str = line[2:].split(':', 1)
                    key = key.strip()
                    value_str = value_str.strip()
                    if value_str == 'None':
                        evaluated[full_guid]['outputs'][key] = None

# Find all None values
none_components = []
for comp_id, comp_data in evaluated.items():
    for key, value in comp_data.get('outputs', {}).items():
        if value is None:
            none_components.append((comp_id, key, comp_data))

print("=" * 80)
print("TRACING ALL NONE VALUES")
print("=" * 80)
print(f"\nFound {len(none_components)} None outputs\n")

# Trace each
for i, (comp_id, output_key, comp_data) in enumerate(none_components, 1):
    print("=" * 80)
    print(f"{i}. Component: {comp_id[:8]}...")
    print(f"   Type: {comp_data['type']}")
    print(f"   Nickname: {comp_data['nickname']}")
    print(f"   None output: {output_key}")
    print()
    
    # Find component info
    comp_info = None
    for comp_key, comp_data_graph in graph.items():
        if isinstance(comp_data_graph, dict):
            instance_guid = comp_data_graph.get('obj', {}).get('instance_guid')
            if instance_guid == comp_id:
                comp_info = comp_data_graph
                break
    
    if not comp_info:
        for obj_key, obj in all_objects.items():
            if obj.get('instance_guid') == comp_id:
                comp_info = {'obj': obj}
                break
    
    if comp_info:
        print("   Inputs:")
        obj_params = comp_info.get('obj', {}).get('params', {})
        for param_key, param_info in obj_params.items():
            if param_key.startswith('param_input'):
                param_name = param_info.get('data', {}).get('NickName', '') or param_info.get('data', {}).get('Name', '')
                sources = param_info.get('sources', [])
                
                print(f"     {param_name}:")
                
                if sources:
                    for source in sources:
                        source_guid = source.get('guid') or source.get('source_guid')
                        if source_guid:
                            print(f"       Source GUID: {source_guid[:8]}...")
                            
                            # Check output params
                            if source_guid in output_params:
                                source_info = output_params[source_guid]
                                source_obj = source_info['obj']
                                source_comp_guid = source_obj.get('instance_guid')
                                print(f"         From component: {source_comp_guid[:8]}... ({source_obj.get('type', 'Unknown')}, {source_obj.get('nickname', '')})")
                                
                                # Check if evaluated
                                if source_comp_guid in evaluated:
                                    source_outputs = evaluated[source_comp_guid].get('outputs', {})
                                    print(f"         [EVALUATED] Outputs: {list(source_outputs.keys())}")
                                    for key, val in source_outputs.items():
                                        if val is None:
                                            print(f"           {key}: None")
                                        else:
                                            val_str = str(val)[:50]
                                            print(f"           {key}: {val_str}")
                                else:
                                    print(f"         [NOT EVALUATED] Component not in results")
                            else:
                                if source_guid in evaluated:
                                    print(f"         [EVALUATED] Direct: {evaluated[source_guid]}")
                                else:
                                    print(f"         [NOT FOUND] GUID not in evaluated or output_params")
                else:
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
print(f"Total None outputs: {len(none_components)}")

