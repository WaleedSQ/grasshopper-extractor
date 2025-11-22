"""Check why Rectangle 2Pt is not being evaluated."""
import json

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

rect_guid = 'a3eb185f-a7cb-4727-aeaf-d5899f934b99'

output = []
def log(msg):
    output.append(msg)
    print(msg)

log("=" * 80)
log("CHECKING RECTANGLE 2PT COMPONENT")
log("=" * 80)
log("")

# Check if in graph
log("1. Is Rectangle 2Pt in graph?")
if rect_guid in graph:
    log(f"   [YES] Found in graph")
    comp_info = graph[rect_guid]
    log(f"   Type: {comp_info.get('type', 'Unknown')}")
    log(f"   Object type: {comp_info.get('obj', {}).get('type', 'Unknown')}")
    log(f"   Nickname: {comp_info.get('obj', {}).get('nickname', '')}")
else:
    log(f"   [NO] Not found in graph")
    # Check all_objects
    if rect_guid in all_objects:
        log(f"   [FOUND] In all_objects instead")
    else:
        log(f"   [NOT FOUND] Not in graph or all_objects")

log("")

# Check if in topological sort
log("2. Checking topological sort...")
from evaluate_rotatingslats import topological_sort

try:
    sorted_components = topological_sort(graph, all_objects, output_params)
    log(f"   Total components in sort: {len(sorted_components)}")
    
    if rect_guid in sorted_components:
        index = sorted_components.index(rect_guid)
        log(f"   [YES] Rectangle 2Pt is in sort at position {index}")
    else:
        log(f"   [NO] Rectangle 2Pt is NOT in topological sort")
        log(f"   Checking similar GUIDs...")
        for comp_id in sorted_components:
            if comp_id.startswith('a3eb185f'):
                log(f"     Found: {comp_id}")
except Exception as e:
    log(f"   [ERROR] Failed to run topological sort: {e}")
    import traceback
    traceback.print_exc()

print()

# Check dependencies
log("3. Checking Rectangle 2Pt dependencies...")
if rect_guid in graph:
    comp_info = graph[rect_guid]
    obj_params = comp_info.get('obj', {}).get('params', {})
    
    log("   Inputs:")
    for param_key, param_info in obj_params.items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('NickName', '') or param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            persistent_values = param_info.get('persistent_values', [])
            
            log(f"     {param_name}:")
            if sources:
                for source in sources:
                    source_guid = source.get('guid') or source.get('source_guid')
                    log(f"       Source: {source_guid[:8]}...")
                    if source_guid in output_params:
                        source_info = output_params[source_guid]
                        source_obj = source_info['obj']
                        source_comp_guid = source_obj.get('instance_guid')
                        log(f"         From component: {source_comp_guid[:8]}... ({source_obj.get('type', 'Unknown')})")
                    else:
                        log(f"         [NOT OUTPUT PARAM]")
            elif persistent_values:
                log(f"       Persistent values: {persistent_values}")
            else:
                log(f"       [NO SOURCE]")
else:
    log("   [SKIP] Component not in graph")

log("")

# Check if evaluated
log("4. Checking if Rectangle 2Pt was evaluated...")
with open('evaluation_results.md', 'r', encoding='utf-8') as f:
    results_content = f.read()
    if rect_guid[:8] in results_content:
        log(f"   [YES] Found in evaluation results")
        # Extract section
        import re
        pattern = f'## Component {rect_guid[:8]}\\.\\.\\.(.*?)(?=\n## Component |\Z)'
        match = re.search(pattern, results_content, re.DOTALL)
        if match:
            section = match.group(1)
            log(f"   Results:")
            for line in section.split('\n')[:10]:
                if line.strip():
                    log(f"     {line}")
    else:
        log(f"   [NO] Not in evaluation results")

log("")
log("=" * 80)

# Write to file
with open('rectangle2pt_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print("\nOutput written to rectangle2pt_check.txt")

