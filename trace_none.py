"""Trace None values - writes to file for Windows compatibility."""
import json
import re

output_lines = []

def log(msg):
    output_lines.append(msg)
    print(msg)

log("=" * 80)
log("TRACING NONE VALUES")
log("=" * 80)
log("")

# Load graph
with open('complete_component_graph.json', 'r', encoding='utf-8') as f:
    graph_data = json.load(f)
    graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

# Load all objects
with open('rotatingslats_data.json', 'r', encoding='utf-8') as f:
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
with open('evaluation_results.md', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')
    
    current_comp_id = None
    current_nickname = None
    current_type = None
    comp_id_short = None
    
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
            if current_comp_id:
                none_components.append({
                    'comp_id': current_comp_id,
                    'comp_id_short': comp_id_short,
                    'nickname': current_nickname,
                    'type': current_type,
                    'output_key': key
                })

log(f"Found {len(none_components)} components with None outputs")
log("")

# Trace each
for i, none_comp in enumerate(none_components, 1):
    comp_id = none_comp['comp_id']
    if not comp_id:
        log(f"{i}. Component {none_comp['comp_id_short']}... - Could not find full GUID")
        continue
        
    log("=" * 80)
    log(f"{i}. Component: {comp_id[:8]}...")
    log(f"   Type: {none_comp['type']}")
    log(f"   Nickname: {none_comp['nickname']}")
    log(f"   None output: {none_comp['output_key']}")
    log("")
    
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
        log("   Inputs:")
        obj_params = comp_info.get('obj', {}).get('params', {})
        for param_key, param_info in obj_params.items():
            if param_key.startswith('param_input'):
                param_name = param_info.get('data', {}).get('NickName', '') or param_info.get('data', {}).get('Name', '')
                sources = param_info.get('sources', [])
                
                log(f"     {param_name}:")
                
                if sources:
                    for source in sources:
                        source_guid = source.get('guid') or source.get('source_guid')
                        if source_guid:
                            log(f"       Source GUID: {source_guid[:8]}...")
                            
                            # Check output params
                            if source_guid in output_params:
                                source_info = output_params[source_guid]
                                source_obj = source_info['obj']
                                source_comp_guid = source_obj.get('instance_guid')
                                log(f"         From component: {source_comp_guid[:8]}...")
                                log(f"         Component type: {source_obj.get('type', 'Unknown')}")
                                log(f"         Component nickname: {source_obj.get('nickname', '')}")
                                
                                # Check if this component is in evaluation results
                                with open('evaluation_results.md', 'r', encoding='utf-8') as f2:
                                    results_content = f2.read()
                                    if source_comp_guid[:8] in results_content:
                                        # Extract its outputs
                                        pattern = f'## Component {source_comp_guid[:8]}\\.\\.\\.(.*?)(?=\n## Component |\Z)'
                                        match = re.search(pattern, results_content, re.DOTALL)
                                        if match:
                                            outputs_text = match.group(1)
                                            log(f"         [IN RESULTS] Outputs found:")
                                            for output_line in outputs_text.split('\n'):
                                                if output_line.startswith('- ') and ':' in output_line:
                                                    log(f"           {output_line.strip()}")
                                    else:
                                        log(f"         [NOT IN RESULTS] Component not found in evaluation_results.md")
                            else:
                                log(f"         [NOT OUTPUT PARAM] GUID not in output_params")
                else:
                    persistent_values = param_info.get('persistent_values', [])
                    if persistent_values:
                        log(f"       Persistent values: {persistent_values}")
                    else:
                        log(f"       [NO SOURCE] No sources or persistent values")
                log("")
    else:
        log("   [NOT FOUND] Component not found in graph or all_objects")
    log("")

log("=" * 80)
log("SUMMARY")
log("=" * 80)
log(f"Total None outputs: {len(none_components)}")

# Write to file
with open('none_trace.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"\nTrace written to none_trace.txt")

