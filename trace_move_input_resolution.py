"""
Trace why Move components are receiving None inputs.
"""
import json
from evaluate_rotatingslats import load_component_graph, get_external_inputs, resolve_input_value, evaluate_component

# Load graph
graph_data = load_component_graph('complete_component_graph.json')
graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

# Load all_objects and build output_params (same way as main script)
with open('rotatingslats_data.json', 'r') as f:
    data = json.load(f)
    all_objects = {}
    all_objects.update(data.get('group_objects', {}))
    all_objects.update(data.get('external_objects', {}))

# Build output params (same way as main script)
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

# Find Move1 component
move1_guid = 'ddb9e6ae-7d3e-41ae-8c75-fc726c984724'
move1 = graph.get(move1_guid, {})

print("=" * 80)
print("TRACING MOVE1 INPUT RESOLUTION")
print("=" * 80)

if not move1:
    print(f"Move1 component {move1_guid[:8]}... not found in graph")
else:
    print(f"\nMove1 component: {move1_guid[:8]}...")
    print(f"  Nickname: {move1.get('obj', {}).get('nickname', 'N/A')}")
    
    # Check inputs
    inputs = move1.get('inputs', {})
    print(f"\nInputs structure: {list(inputs.keys())}")
    
    # Check Geometry input
    geom_input = inputs.get('param_input_0', {})
    if geom_input:
        print(f"\nGeometry input (param_input_0):")
        print(f"  Name: {geom_input.get('name', 'N/A')}")
        sources = geom_input.get('sources', [])
        print(f"  Sources: {sources}")
        
        if sources:
            source = sources[0]
            source_guid = source.get('source_guid') or source.get('guid')
            print(f"\n  Source GUID: {source_guid}")
            
            # Check if source is in output_params
            if source_guid in output_params:
                print(f"  [OK] Source found in output_params")
                source_info = output_params[source_guid]
                source_obj_guid = source_info['obj'].get('instance_guid')
                print(f"  Source component GUID: {source_obj_guid}")
                print(f"  Source param name: {source_info['param_info'].get('data', {}).get('NickName', 'N/A')}")
                
                # Check if source component is evaluated
                evaluated = {}
                # Try to evaluate Rectangle2Pt if it's the source
                if 'Rectangle' in source_info.get('obj', {}).get('type', ''):
                    print(f"\n  Attempting to evaluate Rectangle2Pt component...")
                    rect_comp_guid = source_obj_guid
                    rect_comp = graph.get(rect_comp_guid, {})
                    if rect_comp:
                        try:
                            result = evaluate_component(rect_comp_guid, rect_comp, evaluated, all_objects, output_params, graph=graph)
                            evaluated[rect_comp_guid] = result
                            print(f"  Rectangle2Pt result: {result}")
                            
                            # Now try to resolve Move1 Geometry input
                            print(f"\n  Resolving Move1 Geometry input...")
                            param_info = move1['obj'].get('params', {}).get('param_input_0', {})
                            param_info.update(geom_input)
                            value = resolve_input_value(move1_guid, 'param_input_0', move1, evaluated, all_objects, output_params, param_info=param_info, graph=graph)
                            print(f"  Resolved Geometry value: {value}")
                            print(f"  Value type: {type(value).__name__}")
                            if isinstance(value, dict):
                                print(f"  Value keys: {list(value.keys())}")
                        except Exception as e:
                            print(f"  Error evaluating Rectangle2Pt: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"  Rectangle2Pt component {rect_comp_guid[:8]}... not found in graph")
                else:
                    print(f"  Source is not Rectangle2Pt, type: {source_info.get('obj', {}).get('type', 'N/A')}")
            else:
                print(f"  [ERROR] Source GUID not found in output_params")
                print(f"  Available output_params keys (first 10): {list(output_params.keys())[:10]}")
        else:
            print(f"  No sources found for Geometry input")
    
    # Check Motion input
    motion_input = inputs.get('param_input_1', {})
    if motion_input:
        print(f"\nMotion input (param_input_1):")
        print(f"  Name: {motion_input.get('name', 'N/A')}")
        sources = motion_input.get('sources', [])
        print(f"  Sources: {sources}")

print("\n" + "=" * 80)

