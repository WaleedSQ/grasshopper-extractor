"""
Trace the complete chain for Targets Move component to find Y coordinate issue.
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
print("TRACING TARGETS MOVE CHAIN")
print("=" * 80)

# Step 1: First Move "Targets" (2587762a...)
print("\n1. FIRST MOVE 'Targets' (2587762a-e6a9-4ba9-8724-f347436a5953):")
first_move_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == '2587762a-e6a9-4ba9-8724-f347436a5953':
            first_move_guid = comp_id
            break

if first_move_guid:
    print(f"   Component ID: {first_move_guid[:8]}...")
    try:
        result = evaluate_component(first_move_guid, graph[first_move_guid], evaluated, all_objects, output_params, graph=graph)
        evaluated[first_move_guid] = result
        if isinstance(result, dict) and 'Geometry' in result:
            geom = result['Geometry']
            if isinstance(geom, list) and len(geom) > 0:
                print(f"   Output: First point = {geom[0]}")
                print(f"   Total points: {len(geom)}")
    except Exception as e:
        print(f"   Error: {e}")

# Step 2: Polar Array (b4a4862a...)
print("\n2. POLAR ARRAY (b4a4862a-3bba-4868-943f-cf86bdc99cf3):")
polar_array_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == 'b4a4862a-3bba-4868-943f-cf86bdc99cf3':
            polar_array_guid = comp_id
            break

if polar_array_guid:
    print(f"   Component ID: {polar_array_guid[:8]}...")
    try:
        result = evaluate_component(polar_array_guid, graph[polar_array_guid], evaluated, all_objects, output_params, graph=graph)
        evaluated[polar_array_guid] = result
        if isinstance(result, dict) and 'Geometry' in result:
            geom = result['Geometry']
            print(f"   Output type: {type(geom).__name__}")
            if isinstance(geom, list):
                print(f"   Output length: {len(geom)}")
                if len(geom) > 0:
                    print(f"   First element type: {type(geom[0]).__name__}")
                    if isinstance(geom[0], list) and len(geom[0]) > 0:
                        print(f"   First element length: {len(geom[0])}")
                        print(f"   First point in first element: {geom[0][0]}")
    except Exception as e:
        print(f"   Error: {e}")

# Step 3: List Item (f03b9ab7...)
print("\n3. LIST ITEM (f03b9ab7-3e3f-417e-97be-813257e5f7de):")
list_item_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == 'f03b9ab7-3e3f-417e-97be-813257e5f7de':
            list_item_guid = comp_id
            break

if list_item_guid:
    print(f"   Component ID: {list_item_guid[:8]}...")
    # Check what List input resolves to
    comp_info = graph[list_item_guid]
    try:
        list_input = resolve_input_value(list_item_guid, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"   List input type: {type(list_input).__name__}")
        print(f"   List input value (first 100 chars): {str(list_input)[:100]}")
        if isinstance(list_input, list):
            print(f"   List input length: {len(list_input)}")
            if len(list_input) > 0:
                print(f"   First element type: {type(list_input[0]).__name__}")
                if isinstance(list_input[0], list) and len(list_input[0]) > 0:
                    print(f"   First point in first element: {list_input[0][0]}")
        
        result = evaluate_component(list_item_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[list_item_guid] = result
        if isinstance(result, dict) and 'Item' in result:
            item = result['Item']
            print(f"   Output type: {type(item).__name__}")
            if isinstance(item, list) and len(item) > 0:
                print(f"   Output length: {len(item)}")
                print(f"   First point: {item[0]}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

# Step 4: Second Move "Targets" (b38a38f1...)
print("\n4. SECOND MOVE 'Targets' (b38a38f1-ced5-4600-a687-4ebc4d73e6ff):")
second_move_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == 'b38a38f1-ced5-4600-a687-4ebc4d73e6ff':
            second_move_guid = comp_id
            break

if second_move_guid:
    print(f"   Component ID: {second_move_guid[:8]}...")
    comp_info = graph[second_move_guid]
    try:
        geometry_input = resolve_input_value(second_move_guid, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
        motion_input = resolve_input_value(second_move_guid, 'param_input_1', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"   Geometry input type: {type(geometry_input).__name__}")
        if isinstance(geometry_input, list) and len(geometry_input) > 0:
            print(f"   Geometry input first point: {geometry_input[0]}")
        print(f"   Motion input: {motion_input}")
        
        result = evaluate_component(second_move_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[second_move_guid] = result
        if isinstance(result, dict) and 'Geometry' in result:
            geom = result['Geometry']
            if isinstance(geom, list) and len(geom) > 0:
                print(f"   Output first point: {geom[0]}")
                print(f"   Expected from screenshot: Y approximately -22.846834")
                if isinstance(geom[0], list) and len(geom[0]) >= 2:
                    print(f"   Actual Y: {geom[0][1]}")
                    print(f"   Difference: {geom[0][1] - (-22.846834)}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

