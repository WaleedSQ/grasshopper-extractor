"""
Trace the complete chain for Targets Move component to find the Y coordinate mismatch.
Expected from screenshot: Y ≈ -22.846834
Actual from evaluation: Y = -31.846834162334087
Difference: ~9.0
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
print("COMPLETE TARGETS CHAIN TRACE")
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
                print(f"   Expected: [0.0, -4.5, 4.0] for first point")
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
    comp_info = graph[polar_array_guid]
    
    # Check all inputs
    print("\n   Inputs:")
    try:
        geometry_input = resolve_input_value(polar_array_guid, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
        plane_input = resolve_input_value(polar_array_guid, 'param_input_1', comp_info, evaluated, all_objects, output_params, graph=graph)
        count_input = resolve_input_value(polar_array_guid, 'param_input_2', comp_info, evaluated, all_objects, output_params, graph=graph)
        angle_input = resolve_input_value(polar_array_guid, 'param_input_3', comp_info, evaluated, all_objects, output_params, graph=graph)
        
        print(f"     Geometry: {type(geometry_input).__name__}, first point: {geometry_input[0] if isinstance(geometry_input, list) and len(geometry_input) > 0 else 'N/A'}")
        print(f"     Plane: {plane_input}")
        print(f"     Count: {count_input}")
        print(f"     Angle: {angle_input} radians ({angle_input * 180 / 3.14159 if isinstance(angle_input, (int, float)) else 'N/A'} degrees)")
        
        result = evaluate_component(polar_array_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[polar_array_guid] = result
        if isinstance(result, dict) and 'Geometry' in result:
            geom = result['Geometry']
            print(f"\n   Output:")
            print(f"     Type: {type(geom).__name__}")
            if isinstance(geom, list):
                print(f"     Length: {len(geom)} (should be {count_input})")
                if len(geom) > 0:
                    print(f"     First element type: {type(geom[0]).__name__}")
                    if isinstance(geom[0], list) and len(geom[0]) > 0:
                        print(f"     First element length: {len(geom[0])}")
                        print(f"     First point in first element: {geom[0][0]}")
                        print(f"     Expected: [0.0, -4.5, 4.0] (same as input, no rotation yet)")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

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
    comp_info = graph[list_item_guid]
    
    # Check inputs
    print("\n   Inputs:")
    try:
        list_input = resolve_input_value(list_item_guid, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
        index_input = resolve_input_value(list_item_guid, 'param_input_1', comp_info, evaluated, all_objects, output_params, graph=graph)
        wrap_input = resolve_input_value(list_item_guid, 'param_input_2', comp_info, evaluated, all_objects, output_params, graph=graph)
        
        print(f"     List: {type(list_input).__name__}, length: {len(list_input) if isinstance(list_input, list) else 'N/A'}")
        if isinstance(list_input, list) and len(list_input) > 0:
            print(f"       First element: {list_input[0][0] if isinstance(list_input[0], list) and len(list_input[0]) > 0 else 'N/A'}")
        print(f"     Index: {index_input}")
        print(f"     Wrap: {wrap_input}")
        
        result = evaluate_component(list_item_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[list_item_guid] = result
        if isinstance(result, dict) and 'Item' in result:
            item = result['Item']
            print(f"\n   Output:")
            print(f"     Type: {type(item).__name__}")
            if isinstance(item, list) and len(item) > 0:
                print(f"     Length: {len(item)}")
                print(f"     First point: {item[0]}")
                print(f"     Expected: [0.0, -4.5, 4.0] (extracted from Polar Array index {index_input})")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

# Step 4: Amplitude (d0668a07...)
print("\n4. AMPLITUDE (d0668a07-838c-481c-88eb-191574362cc2):")
amplitude_output_guid = 'd0668a07-838c-481c-88eb-191574362cc2'
if amplitude_output_guid in output_params:
    source_info = output_params[amplitude_output_guid]
    source_obj_guid = source_info['obj'].get('instance_guid')
    if source_obj_guid in evaluated:
        amp_result = evaluated.get(source_obj_guid, {})
        if isinstance(amp_result, dict) and 'Vector' in amp_result:
            motion = amp_result['Vector']
            print(f"   Motion vector: {motion}")
            print(f"   Expected: [11.327429598006665, -27.346834162334087, 0.0]")

# Step 5: Second Move "Targets" (b38a38f1...)
print("\n5. SECOND MOVE 'Targets' (b38a38f1-ced5-4600-a687-4ebc4d73e6ff):")
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
        
        print(f"\n   Inputs:")
        print(f"     Geometry: {type(geometry_input).__name__}")
        if isinstance(geometry_input, list) and len(geometry_input) > 0:
            print(f"       First point: {geometry_input[0]}")
        print(f"     Motion: {motion_input}")
        
        print(f"\n   Calculation:")
        if isinstance(geometry_input, list) and len(geometry_input) > 0 and isinstance(motion_input, list) and len(motion_input) == 3:
            first_point = geometry_input[0]
            if isinstance(first_point, list) and len(first_point) >= 3:
                calculated = [
                    first_point[0] + motion_input[0],
                    first_point[1] + motion_input[1],
                    first_point[2] + motion_input[2]
                ]
                print(f"       Input point: {first_point}")
                print(f"       Motion: {motion_input}")
                print(f"       Calculated: {calculated}")
                print(f"       Expected from screenshot: [11.32743, -22.846834, 4]")
                print(f"       Actual: [11.327429598006665, -31.846834162334087, 4.0]")
                print(f"       Y difference: {calculated[1] - (-22.846834)}")
        
        result = evaluate_component(second_move_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[second_move_guid] = result
        if isinstance(result, dict) and 'Geometry' in result:
            geom = result['Geometry']
            if isinstance(geom, list) and len(geom) > 0:
                print(f"\n   Output:")
                print(f"     First point: {geom[0]}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("ANALYSIS:")
print("=" * 80)
print("If the screenshot shows Y = -22.846834 but we calculate Y = -31.846834,")
print("the difference is 9.0. This suggests:")
print("1. The input geometry Y might be different (should be 4.5 instead of -4.5?)")
print("2. The Polar Array might be rotating the geometry")
print("3. The List Item might be extracting a different index")
print("4. There might be an additional transformation we're missing")

