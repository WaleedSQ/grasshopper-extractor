"""
Debug why Polygon and Rotate are not in topological sort.
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import topological_sort, load_component_graph

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

# Component GUIDs
polygon_guid = 'a2151ddb-9077-4065-90f3-e337cd983593'
rotate_guid = '5a77f108-b5a1-429b-9d22-0a14d7945abd'

print("=" * 80)
print("TOPOLOGICAL SORT DEBUG - POLYGON AND ROTATE")
print("=" * 80)
print()

# Check if components are in graph
print("Component Check:")
print(f"  Polygon in graph: {polygon_guid in graph}")
print(f"  Rotate in graph: {rotate_guid in graph}")
print()

if polygon_guid in graph:
    polygon_comp = graph[polygon_guid]
    print("Polygon Component:")
    print(f"  Type: {polygon_comp.get('type', 'N/A')}")
    print(f"  Has inputs: {'inputs' in polygon_comp}")
    if 'inputs' in polygon_comp:
        inputs = polygon_comp['inputs']
        print(f"  Number of inputs: {len(inputs)}")
        for param_key, input_info in inputs.items():
            sources = input_info.get('sources', [])
            print(f"    {input_info.get('name', 'N/A')}: {len(sources)} sources")
            for source in sources:
                source_guid = source.get('source_guid') or source.get('guid')
                print(f"      Source GUID: {source_guid[:8] if source_guid else 'N/A'}...")
    print()

if rotate_guid in graph:
    rotate_comp = graph[rotate_guid]
    print("Rotate Component:")
    print(f"  Type: {rotate_comp.get('type', 'N/A')}")
    print(f"  Has inputs: {'inputs' in rotate_comp}")
    if 'inputs' in rotate_comp:
        inputs = rotate_comp['inputs']
        print(f"  Number of inputs: {len(inputs)}")
        for param_key, input_info in inputs.items():
            sources = input_info.get('sources', [])
            print(f"    {input_info.get('name', 'N/A')}: {len(sources)} sources")
            for source in sources:
                source_guid = source.get('source_guid') or source.get('guid')
                print(f"      Source GUID: {source_guid[:8] if source_guid else 'N/A'}...")
    print()

# Run topological sort
print("Running topological sort...")
sorted_components = topological_sort(graph_data if isinstance(graph_data, dict) and 'components' in graph_data else graph, 
                                     all_objects, output_params)

print(f"\nTopological Sort Results:")
print(f"  Total components in sort: {len(sorted_components)}")
print(f"  Polygon in sort: {polygon_guid in sorted_components}")
print(f"  Rotate in sort: {rotate_guid in sorted_components}")

if polygon_guid in sorted_components:
    print(f"  Polygon position: {sorted_components.index(polygon_guid)}")
if rotate_guid in sorted_components:
    print(f"  Rotate position: {sorted_components.index(rotate_guid)}")

# Check dependencies
print(f"\nDependency Check:")
components_dict = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

# Build dependencies manually to see what's happening
dependencies = {}
all_comp_ids = set()

for comp_id, comp_info in components_dict.items():
    if isinstance(comp_info, dict) and comp_info.get('type') == 'component':
        all_comp_ids.add(comp_id)

print(f"  Total components found: {len(all_comp_ids)}")
print(f"  Polygon in all_comp_ids: {polygon_guid in all_comp_ids}")
print(f"  Rotate in all_comp_ids: {rotate_guid in all_comp_ids}")

# Check Polygon dependencies
if polygon_guid in all_comp_ids:
    polygon_comp = components_dict[polygon_guid]
    inputs = polygon_comp.get('inputs', {})
    if not inputs and 'obj' in polygon_comp:
        obj_params = polygon_comp['obj'].get('params', {})
        inputs = {}
        for param_key, param_data in obj_params.items():
            if param_key.startswith('param_input'):
                param_name = param_data.get('data', {}).get('NickName', '') or param_data.get('data', {}).get('Name', '')
                if param_name:
                    inputs[param_key] = {
                        'name': param_name,
                        'sources': param_data.get('sources', [])
                    }
    
    deps = set()
    for input_key, input_info in inputs.items():
        sources = input_info.get('sources', [])
        for source in sources:
            source_guid = source.get('source_guid') or source.get('guid')
            if source_guid:
                # Find component with this output
                for other_comp_id, other_comp_info in components_dict.items():
                    if isinstance(other_comp_info, dict) and other_comp_info.get('type') == 'component':
                        other_obj = other_comp_info.get('obj', {})
                        other_params = other_obj.get('params', {})
                        for param_key, param_data in other_params.items():
                            if param_key.startswith('param_output'):
                                param_guid = param_data.get('data', {}).get('InstanceGuid')
                                if param_guid == source_guid:
                                    deps.add(other_comp_id)
    
    print(f"\n  Polygon dependencies: {len(deps)}")
    for dep in deps:
        print(f"    {dep[:8]}...")

