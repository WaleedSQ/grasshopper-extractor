"""
Verify all List Item (LI) components in the Rotatingslats chain.
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, evaluate_graph, get_external_inputs
from gh_data_tree import DataTree, is_tree

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

# Find all List Item components
li_components = {}
for comp_id, comp_info in graph.items():
    if isinstance(comp_info, dict) and comp_info.get('type') == 'component':
        comp_type = comp_info.get('obj', {}).get('type', '')
        if comp_type == 'List Item':
            instance_guid = comp_info.get('obj', {}).get('instance_guid', comp_id)
            li_components[instance_guid] = {
                'comp_id': comp_id,
                'comp_info': comp_info,
                'nickname': comp_info.get('obj', {}).get('nickname', ''),
            }

print("=" * 80)
print("ALL LIST ITEM COMPONENTS VERIFICATION")
print("=" * 80)
print(f"\nFound {len(li_components)} List Item components\n")

# Evaluate graph
print("Evaluating graph...")
evaluated = evaluate_graph(graph_data if isinstance(graph_data, dict) and 'components' in graph_data else graph, 
                          all_objects, output_params)

# Rotatingslats chain LI GUID
rotatingslats_li_guid = '27933633-dbab-4dc0-a4a2-cfa309c03c45'

# Verify each List Item
for li_guid, li_info in sorted(li_components.items()):
    comp_id = li_info['comp_id']
    comp_info = li_info['comp_info']
    nickname = li_info['nickname']
    
    print(f"\n{'='*80}")
    print(f"List Item: {nickname} ({li_guid[:8]}...)")
    print(f"{'='*80}")
    
    # Get inputs from graph
    inputs_info = comp_info.get('inputs', {})
    list_input = inputs_info.get('param_input_0', {})
    index_input = inputs_info.get('param_input_1', {})
    wrap_input = inputs_info.get('param_input_2', {})
    
    print("\nInputs:")
    # List source
    list_sources = list_input.get('sources', [])
    if list_sources:
        list_source = list_sources[0]
        print(f"  List: from {list_source.get('source_obj_name', 'Unknown')} ({list_source.get('source_obj_guid', '')[:8] if list_source.get('source_obj_guid') else 'N/A'}...)")
        print(f"    Source GUID: {list_source.get('source_guid', 'N/A')[:8] if list_source.get('source_guid') else 'N/A'}...")
    else:
        print(f"  List: No source (persistent_values: {list_input.get('persistent_values', [])})")
    
    # Index source
    index_sources = index_input.get('sources', [])
    index_persistent = index_input.get('persistent_values', [])
    if index_sources:
        index_source = index_sources[0]
        print(f"  Index: from {index_source.get('source_obj_name', 'Unknown')} ({index_source.get('source_guid', '')[:8] if index_source.get('source_guid') else 'N/A'}...)")
    elif index_persistent:
        print(f"  Index: {index_persistent[0]} (persistent)")
    else:
        print(f"  Index: {index_input.get('values', ['N/A'])[0]}")
    
    # Wrap
    wrap_value = wrap_input.get('values', ['false'])[0] if wrap_input.get('values') else 'false'
    if isinstance(wrap_value, str):
        wrap_bool = wrap_value.lower() == 'true'
    else:
        wrap_bool = bool(wrap_value)
    print(f"  Wrap: {wrap_bool}")
    
    # Check evaluation result
    print("\nEvaluation Result:")
    if li_guid in evaluated:
        result = evaluated[li_guid]
        if isinstance(result, dict):
            item = result.get('Item')
            print(f"  Item type: {type(item).__name__}")
            print(f"  Is DataTree: {is_tree(item)}")
            
            if is_tree(item):
                paths = item.paths()
                print(f"  Number of branches: {len(paths)}")
                print(f"  Branch details (first 3):")
                for i, path in enumerate(sorted(paths)[:3]):
                    branch_items = item.get_branch(path)
                    print(f"    Path {path}: {len(branch_items)} items")
                    if branch_items:
                        first_item = branch_items[0]
                        print(f"      First item type: {type(first_item).__name__}")
                        if isinstance(first_item, list) and len(first_item) > 0:
                            print(f"      First item content: {str(first_item[0])[:60]}...")
            elif isinstance(item, list):
                print(f"  List length: {len(item)}")
                if item:
                    print(f"  First item type: {type(item[0]).__name__}")
                    print(f"  First item: {str(item[0])[:60]}...")
            else:
                print(f"  Item value: {str(item)[:100]}...")
        else:
            print(f"  Result: {str(result)[:100]}...")
    else:
        print("  NOT EVALUATED")
    
    # Special check for Rotatingslats chain LI
    if li_guid == rotatingslats_li_guid:
        print("\n  [ROTATINGSLATS CHAIN] This is the main List Item in the chain")
        print("  Expected: DataTree with 10 branches, each with 1 rectangle (selected from Polar Array)")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print(f"Total List Item components: {len(li_components)}")
print(f"Evaluated: {sum(1 for li_guid in li_components.keys() if li_guid in evaluated)}")
print(f"Not evaluated: {sum(1 for li_guid in li_components.keys() if li_guid not in evaluated)}")

