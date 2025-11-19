"""
Trace the Slats original geometry chain to understand why it's outputting strings instead of geometry dicts.
Chain: Rectangle 2Pt -> First Move "Slats original" -> Polar Array -> List Item -> Second Move "Slats original" -> Area
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, get_external_inputs, topological_sort, evaluate_component, resolve_input_value

# Load everything
graph_data = load_component_graph('complete_component_graph.json')
graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

with open('rotatingslats_data.json', 'r') as f:
    data = json.load(f)
    all_objects = {}
    all_objects.update(data.get('group_objects', {}))
    all_objects.update(data.get('external_objects', {}))

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

# Get topological sort
sorted_components = topological_sort(graph_data, all_objects, output_params)

print("=" * 80)
print("TRACING SLATS ORIGINAL GEOMETRY CHAIN")
print("=" * 80)

# Component GUIDs in the chain
rectangle_2pt_guid = 'a3eb185f-a7cb-4727-aeaf-d5899f934b99'  # Rectangle 2Pt
first_move_guid = 'ddb9e6ae-7d3e-41ae-8c75-fc726c984724'  # First Move "Slats original"
polar_array_guid = '7ad636cc-e506-4f77-bb82-4a86ba2a3fea'  # Polar Array
list_item_guid = '27933633-dbab-4dc0-a4a2-cfa309c03c45'  # List Item
second_move_guid = '0532cbdf-875b-4db9-8c88-352e21051436'  # Second Move "Slats original"
area_guid = '3bd2c1d3-149d-49fb-952c-8db272035f9e'  # Area

# Find component IDs in graph
comp_ids = {}
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        instance_guid = obj.get('instance_guid')
        if instance_guid == rectangle_2pt_guid:
            comp_ids['rectangle_2pt'] = comp_id
        elif instance_guid == first_move_guid:
            comp_ids['first_move'] = comp_id
        elif instance_guid == polar_array_guid:
            comp_ids['polar_array'] = comp_id
        elif instance_guid == list_item_guid:
            comp_ids['list_item'] = comp_id
        elif instance_guid == second_move_guid:
            comp_ids['second_move'] = comp_id
        elif instance_guid == area_guid:
            comp_ids['area'] = comp_id

print("\nComponent IDs found:")
for name, comp_id in comp_ids.items():
    print(f"  {name}: {comp_id[:8]}...")

# Evaluate components in order
print("\n" + "=" * 80)
print("EVALUATING COMPONENTS IN ORDER")
print("=" * 80)

for comp_id in sorted_components:
    comp_info = graph.get(comp_id, {})
    if not isinstance(comp_info, dict):
        continue
    
    obj = comp_info.get('obj', {})
    instance_guid = obj.get('instance_guid')
    comp_type = obj.get('type', '')
    nickname = obj.get('nickname', '')
    
    # Check if this is one of our chain components
    chain_step = None
    if instance_guid == rectangle_2pt_guid:
        chain_step = "1. Rectangle 2Pt"
    elif instance_guid == first_move_guid:
        chain_step = "2. First Move 'Slats original'"
    elif instance_guid == polar_array_guid:
        chain_step = "3. Polar Array"
    elif instance_guid == list_item_guid:
        chain_step = "4. List Item"
    elif instance_guid == second_move_guid:
        chain_step = "5. Second Move 'Slats original'"
    elif instance_guid == area_guid:
        chain_step = "6. Area"
    
    if chain_step:
        print(f"\n{chain_step} ({comp_id[:8]}...):")
        print(f"  Type: {comp_type}, Nickname: {nickname}")
        
        # Check inputs before evaluation
        if chain_step == "2. First Move 'Slats original'":
            print("  Checking Geometry input:")
            print("    Source GUID: dbc236d4-a2fe-48a8-a86e-eebfb04b1053")
            # Check what's in output_params
            source_guid = 'dbc236d4-a2fe-48a8-a86e-eebfb04b1053'
            if source_guid in output_params:
                source_info = output_params[source_guid]
                print(f"    Output param found, NickName: {source_info['param_info'].get('data', {}).get('NickName', 'N/A')}")
                source_obj_guid = source_info['obj'].get('instance_guid')
                print(f"    Parent component GUID: {source_obj_guid}")
                if source_obj_guid in evaluated:
                    comp_outputs = evaluated.get(source_obj_guid, {})
                    print(f"    Parent component output type: {type(comp_outputs).__name__}")
                    if isinstance(comp_outputs, dict):
                        print(f"    Parent component output keys: {list(comp_outputs.keys())}")
                        for key, value in comp_outputs.items():
                            print(f"      {key}: {type(value).__name__}")
                            if isinstance(value, dict):
                                print(f"        Dict keys: {list(value.keys())[:5]}")
                                if 'type' in value:
                                    print(f"        type field: {value.get('type')}")
            try:
                geometry = resolve_input_value(comp_id, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
                print(f"    Resolved Geometry type: {type(geometry).__name__}")
                if isinstance(geometry, dict):
                    print(f"    Geometry keys: {list(geometry.keys())[:5]}")
                    if 'type' in geometry:
                        print(f"    Geometry type field: {geometry.get('type')}")
                    if 'corners' in geometry:
                        corners = geometry.get('corners')
                        print(f"    Corners: {len(corners) if corners else 0} corners")
                        if corners and len(corners) > 0:
                            print(f"    First corner: {corners[0]}")
                elif isinstance(geometry, str):
                    print(f"    Geometry is a STRING: '{geometry}'")
                else:
                    print(f"    Geometry value: {geometry}")
            except Exception as e:
                print(f"    Error resolving Geometry: {e}")
                import traceback
                traceback.print_exc()
        
        # Evaluate component
        try:
            result = evaluate_component(comp_id, comp_info, evaluated, all_objects, output_params, graph=graph)
            evaluated[instance_guid] = result
            evaluated[comp_id] = result
            
            # Store output params
            if isinstance(result, dict):
                for param_key, param_info in obj.get('params', {}).items():
                    if param_key.startswith('param_output'):
                        param_guid = param_info.get('data', {}).get('InstanceGuid')
                        if param_guid:
                            output_params[param_guid] = {
                                'obj': obj,
                                'param_key': param_key,
                                'param_info': param_info
                            }
                            # Store the output value
                            param_name = param_info.get('data', {}).get('NickName', '')
                            if param_name in result:
                                evaluated[param_guid] = result[param_name]
            
            # Print output
            if isinstance(result, dict):
                print(f"  Output keys: {list(result.keys())}")
                for key, value in result.items():
                    if key == 'Geometry':
                        if isinstance(value, list):
                            print(f"  {key}: list with {len(value)} items")
                            if len(value) > 0:
                                print(f"    First item type: {type(value[0]).__name__}")
                                if isinstance(value[0], dict):
                                    print(f"    First item keys: {list(value[0].keys())[:5]}")
                                elif isinstance(value[0], str):
                                    print(f"    First item is STRING: '{value[0]}'")
                        elif isinstance(value, str):
                            print(f"  {key}: STRING '{value}'")
                        elif isinstance(value, dict):
                            print(f"  {key}: dict with keys {list(value.keys())[:5]}")
                        else:
                            print(f"  {key}: {type(value).__name__}")
                    else:
                        print(f"  {key}: {type(value).__name__}")
            else:
                print(f"  Result type: {type(result).__name__}")
                print(f"  Result: {result}")
        except Exception as e:
            print(f"  Error evaluating: {e}")
            import traceback
            traceback.print_exc()

print("\n" + "=" * 80)
print("TRACE COMPLETE")
print("=" * 80)

