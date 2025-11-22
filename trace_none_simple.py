"""Simple script to trace None values from evaluation results."""
import json
import re

print("=" * 80)
print("TRACING NONE VALUES")
print("=" * 80)
print()

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

# Parse evaluation results - find components with None
none_components = []
with open('evaluation_results.md', 'r') as f:
    content = f.read()
    lines = content.split('\n')
    
    current_comp_id = None
    current_nickname = None
    current_type = None
    
    for i, line in enumerate(lines):
        if line.startswith('## Component '):
            comp_id_short = line.split('Component ')[1].split('...')[0]
            # Find full GUID
            current_comp_id = None
            for comp_key, comp_data in graph.items():
                if isinstance(comp_data, dict):
                    instance_guid = comp_data.get('obj', {}).get('instance_guid', '')
                    if instance_guid and instance_guid.startswith(comp_id_short):
                        current_comp_id = instance_guid
                        break
            if not current_comp_id:
                for obj_key, obj in all_objects.items():
                    instance_guid = obj.get('instance_guid', '')
                    if instance_guid and instance_guid.startswith(comp_id_short):
                        current_comp_id = instance_guid
                        break
        elif line.startswith('**Nickname:**'):
            current_nickname = line.split('**Nickname:**')[1].strip()
        elif line.startswith('**Type:**'):
            current_type = line.split('**Type:**')[1].strip()
        elif line.startswith('- ') and ': None' in line:
            key = line.split(':')[0].replace('- ', '').strip()
            none_components.append({
                'comp_id': current_comp_id,
                'comp_id_short': comp_id_short if 'comp_id_short' in locals() else 'unknown',
                'nickname': current_nickname,
                'type': current_type,
                'output_key': key
            })

print(f"Found {len(none_components)} components with None outputs\n")

# Trace each
for i, none_comp in enumerate(none_components, 1):
    comp_id = none_comp['comp_id']
    if not comp_id:
        print(f"{i}. Component {none_comp['comp_id_short']}... - Could not find full GUID")
        continue
        
    print("=" * 80)
    print(f"{i}. Component: {comp_id[:8]}...")
    print(f"   Type: {none_comp['type']}")
    print(f"   Nickname: {none_comp['nickname']}")
    print(f"   None output: {none_comp['output_key']}")
    print()
    
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
                                print(f"         From component: {source_comp_guid[:8]}...")
                                print(f"         Component type: {source_obj.get('type', 'Unknown')}")
                                print(f"         Component nickname: {source_obj.get('nickname', '')}")
                                
                                # Check if this component is in evaluation results
                                found_in_results = False
                                with open('evaluation_results.md', 'r') as f2:
                                    results_content = f2.read()
                                    if source_comp_guid[:8] in results_content:
                                        found_in_results = True
                                        # Extract its outputs
                                        pattern = f'## Component {source_comp_guid[:8]}\\.\\.\\.(.*?)(?=\n## Component |\Z)'
                                        match = re.search(pattern, results_content, re.DOTALL)
                                        if match:
                                            outputs_text = match.group(1)
                                            print(f"         [IN RESULTS] Outputs found in evaluation_results.md")
                                            for output_line in outputs_text.split('\n'):
                                                if output_line.startswith('- ') and ':' in output_line:
                                                    print(f"           {output_line.strip()}")
                                    else:
                                        print(f"         [NOT IN RESULTS] Component not found in evaluation_results.md")
                            else:
                                print(f"         [NOT OUTPUT PARAM] GUID not in output_params")
                else:
                    persistent_values = param_info.get('persistent_values', [])
                    if persistent_values:
                        print(f"       Persistent values: {persistent_values}")
                    else:
                        print(f"       [NO SOURCE] No sources or persistent values")
                print()
    else:
        print("   [NOT FOUND] Component not found in graph or all_objects")
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total None outputs: {len(none_components)}")

