"""
Verify Area component that receives input from Mirror.
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

# Component GUIDs
area_guid = '16022012-569d-4c58-a081-6d57649a1720'
mirror_guid = '47650d42-5fa9-44b3-b970-9f28b94bb031'

print("=" * 80)
print("AREA COMPONENT VERIFICATION (After Mirror)")
print("=" * 80)
print()

# Get component info
area_comp = graph.get(area_guid, {})
if not area_comp:
    print(f"Area component {area_guid[:8]}... NOT FOUND")
    sys.exit(1)

print("Component Info:")
print(f"  GUID: {area_guid}")
print(f"  Type: {area_comp.get('obj', {}).get('type', 'Unknown')}")
print(f"  NickName: {area_comp.get('obj', {}).get('nickname', 'Unknown')}")
print()

# Get inputs
inputs_info = area_comp.get('inputs', {})
geom_input = inputs_info.get('param_input_0', {})

print("Inputs:")
# Geometry source
geom_sources = geom_input.get('sources', [])
if geom_sources:
    geom_source = geom_sources[0]
    print(f"  Geometry: from {geom_source.get('source_obj_name', 'Unknown')} ({geom_source.get('source_obj_guid', '')[:8] if geom_source.get('source_obj_guid') else 'N/A'}...)")
    print(f"    Source GUID: {geom_source.get('source_guid', 'N/A')[:8] if geom_source.get('source_guid') else 'N/A'}...")
    print(f"    Expected: Mirror Geometry output (db399c50...)")
else:
    print(f"  Geometry: No source")
print()

print("Expected Output:")
print("  - Area: numeric value or DataTree")
print("  - Centroid: [x, y, z] point or DataTree")
print()

# Evaluate
print("Evaluating graph...")
evaluated = evaluate_graph(graph_data if isinstance(graph_data, dict) and 'components' in graph_data else graph, 
                          all_objects, output_params)

# Check Mirror output first
print("\n" + "=" * 80)
print("MIRROR OUTPUT (Input to Area)")
print("=" * 80)
print()

if mirror_guid in evaluated:
    mirror_result = evaluated[mirror_guid]
    print(f"Mirror ({mirror_guid[:8]}...) found in evaluated results")
    if isinstance(mirror_result, dict):
        mirror_geom = mirror_result.get('Geometry')
        print(f"  Geometry type: {type(mirror_geom).__name__}")
        print(f"  Is DataTree: {is_tree(mirror_geom)}")
        if isinstance(mirror_geom, dict):
            print(f"  Geometry keys: {list(mirror_geom.keys())}")
            if 'vertices' in mirror_geom:
                vertices = mirror_geom['vertices']
                print(f"  Number of vertices: {len(vertices)}")
                if vertices:
                    print(f"  First vertex: {vertices[0]}")
        elif is_tree(mirror_geom):
            paths = mirror_geom.paths()
            print(f"  Number of branches: {len(paths)}")
else:
    print(f"Mirror ({mirror_guid[:8]}...) NOT found in evaluated results")

# Check Area result
print("\n" + "=" * 80)
print("AREA OUTPUT")
print("=" * 80)
print()

if area_guid in evaluated:
    result = evaluated[area_guid]
    print(f"Area ({area_guid[:8]}...) found in evaluated results")
    print(f"  Result type: {type(result).__name__}")
    
    if isinstance(result, dict):
        area = result.get('Area')
        centroid = result.get('Centroid')
        
        print(f"\n  Area output:")
        print(f"    Type: {type(area).__name__}")
        print(f"    Is DataTree: {is_tree(area)}")
        if is_tree(area):
            paths = area.paths()
            print(f"    Number of branches: {len(paths)}")
            if paths:
                first_path = sorted(paths)[0]
                first_area = area.get_branch(first_path)
                print(f"    First branch area: {first_area[0] if first_area else 'N/A'}")
        elif isinstance(area, (int, float)):
            print(f"    Value: {area}")
        elif isinstance(area, list):
            print(f"    List length: {len(area)}")
            if area:
                print(f"    First value: {area[0]}")
        
        print(f"\n  Centroid output:")
        print(f"    Type: {type(centroid).__name__}")
        print(f"    Is DataTree: {is_tree(centroid)}")
        if is_tree(centroid):
            paths = centroid.paths()
            print(f"    Number of branches: {len(paths)}")
            if paths:
                first_path = sorted(paths)[0]
                first_centroid = centroid.get_branch(first_path)
                if first_centroid and len(first_centroid) > 0:
                    cent = first_centroid[0]
                    print(f"    First branch centroid: {cent}")
                    if isinstance(cent, list) and len(cent) >= 3:
                        print(f"      X: {cent[0]}, Y: {cent[1]}, Z: {cent[2]}")
        elif isinstance(centroid, list):
            print(f"    List length: {len(centroid)}")
            if centroid:
                cent = centroid[0] if isinstance(centroid[0], list) else centroid
                print(f"    First centroid: {cent}")
                if isinstance(cent, list) and len(cent) >= 3:
                    print(f"      X: {cent[0]}, Y: {cent[1]}, Z: {cent[2]}")
    else:
        print(f"  Result: {str(result)[:100]}...")
else:
    print(f"Area ({area_guid[:8]}...) NOT found in evaluated results")

