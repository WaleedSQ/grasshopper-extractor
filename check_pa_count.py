"""
Check if Polar Array Count input is being resolved correctly.
It should use the source value (8.0 from Number of orientations) not PersistentData (10).
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, get_external_inputs, evaluate_component, resolve_input_value

# Load the graph
graph_data = load_component_graph('complete_component_graph.json')
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

external_inputs = get_external_inputs()
evaluated = {}

print("=" * 80)
print("CHECKING POLAR ARRAY COUNT INPUT")
print("=" * 80)

# Find Polar Array component
polar_array_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == 'b4a4862a-3bba-4868-943f-cf86bdc99cf3':
            polar_array_guid = comp_id
            break

if polar_array_guid:
    print(f"\nPolar Array component ID: {polar_array_guid[:8]}...")
    comp_info = graph[polar_array_guid]
    
    # Check Count input (param_input_2)
    print("\nChecking Count input (param_input_2):")
    count_value = resolve_input_value(polar_array_guid, 'param_input_2', comp_info, evaluated, all_objects, output_params, graph=graph)
    print(f"  Resolved Count value: {count_value}")
    print(f"  Type: {type(count_value).__name__}")
    
    # Check what the source should be
    param_info = comp_info['obj'].get('params', {}).get('param_input_2', {})
    sources = param_info.get('sources', [])
    persistent_values = param_info.get('persistent_values', [])
    print(f"  Sources: {len(sources)}")
    if sources:
        source_guid = sources[0].get('guid')
        print(f"  Source GUID: {source_guid}")
        # Check if source is evaluated
        if source_guid in output_params:
            source_info = output_params[source_guid]
            source_obj_guid = source_info['obj'].get('instance_guid')
            print(f"  Source is output param, parent: {source_obj_guid}")
            # Try to evaluate the source
            if source_obj_guid:
                for comp_id2, comp2 in graph.items():
                    if isinstance(comp2, dict) and comp2.get('obj', {}).get('instance_guid') == source_obj_guid:
                        try:
                            result = evaluate_component(comp_id2, comp2, evaluated, all_objects, output_params, graph=graph)
                            evaluated[comp_id2] = result
                            print(f"  Source component evaluated: {result}")
                            if isinstance(result, dict) and 'Value' in result:
                                print(f"  Source value: {result['Value']}")
                        except Exception as e:
                            print(f"  Error evaluating source: {e}")
    print(f"  Persistent values: {persistent_values}")
    
    # Now try to evaluate Polar Array to see what Count it uses
    print("\nEvaluating Polar Array component:")
    try:
        # First evaluate dependencies
        geometry_input = resolve_input_value(polar_array_guid, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"  Geometry input resolved: {type(geometry_input).__name__}")
        
        count_input = resolve_input_value(polar_array_guid, 'param_input_2', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"  Count input resolved: {count_input}")
        
        result = evaluate_component(polar_array_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        if isinstance(result, dict) and 'Geometry' in result:
            geom = result['Geometry']
            if isinstance(geom, list):
                print(f"  Polar Array output length: {len(geom)}")
                print(f"  Expected: 8 (from Number of orientations)")
                print(f"  Actual: {len(geom)}")
                if len(geom) != 8:
                    print(f"  [ERROR] Count mismatch! Should be 8, got {len(geom)}")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

