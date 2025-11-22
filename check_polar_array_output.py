"""
Check Polar Array component output structure.
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

# Evaluate
print("Evaluating graph...")
evaluated = evaluate_graph(graph_data if isinstance(graph_data, dict) and 'components' in graph_data else graph, 
                          all_objects, output_params)

# Check Polar Array
pa_guid = '7ad636cc-e506-4f77-bb82-4a86ba2a3fea'
print(f"\n{'='*80}")
print("POLAR ARRAY OUTPUT VERIFICATION")
print(f"{'='*80}\n")

if pa_guid in evaluated:
    pa_result = evaluated[pa_guid]
    print(f"Polar Array ({pa_guid[:8]}...) found in evaluated results")
    print(f"Result type: {type(pa_result).__name__}")
    
    if isinstance(pa_result, dict):
        geom = pa_result.get('Geometry')
        print(f"\nGeometry output:")
        print(f"  Type: {type(geom).__name__}")
        print(f"  Is DataTree: {is_tree(geom)}")
        
        if is_tree(geom):
            paths = geom.paths()
            print(f"  Number of branches: {len(paths)}")
            print(f"\n  Branch details (first 5):")
            for i, path in enumerate(sorted(paths)[:5]):
                branch_items = geom.get_branch(path)
                print(f"    Path {path}: {len(branch_items)} items")
                if branch_items:
                    first_item = branch_items[0]
                    print(f"      First item type: {type(first_item).__name__}")
                    if isinstance(first_item, dict):
                        print(f"      First item keys: {list(first_item.keys())[:5]}")
        elif isinstance(geom, list):
            print(f"  Number of items: {len(geom)}")
            if geom:
                print(f"  First item type: {type(geom[0]).__name__}")
    else:
        print(f"Result: {pa_result}")
else:
    print(f"Polar Array ({pa_guid[:8]}...) NOT found in evaluated results")

# Check input (Move component output)
move_guid = 'ddb9e6ae-7d3e-41ae-8c75-fc726c984724'
print(f"\n{'='*80}")
print("FIRST MOVE OUTPUT (Polar Array Input)")
print(f"{'='*80}\n")

if move_guid in evaluated:
    move_result = evaluated[move_guid]
    print(f"Move ({move_guid[:8]}...) found in evaluated results")
    
    if isinstance(move_result, dict):
        move_geom = move_result.get('Geometry')
        print(f"  Geometry type: {type(move_geom).__name__}")
        print(f"  Is DataTree: {is_tree(move_geom)}")
        
        if is_tree(move_geom):
            paths = move_geom.paths()
            print(f"  Number of branches: {len(paths)}")
            for i, path in enumerate(sorted(paths)[:3]):
                branch_items = move_geom.get_branch(path)
                print(f"    Path {path}: {len(branch_items)} items")
else:
    print(f"Move ({move_guid[:8]}...) NOT found in evaluated results")

