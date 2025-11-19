"""
Trace the complete chain for Slats original Move component and verify Centroid output.
Screenshot shows Centroid: [11.32743, -27.416834, 3.8], [11.32743, -27.416834, 3.722222], etc.
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
print("SLATS ORIGINAL CHAIN TRACE")
print("=" * 80)

# Find components by instance_guid
# First Move "Slats original": ddb9e6ae-7d3e-41ae-8c75-fc726c984724
# Polar Array: 7ad636cc-e506-4f77-bb82-4a86ba2a3fea
# List Item: 27933633-dbab-4dc0-a4a2-cfa309c03c45
# Second Move "Slats original": 0532cbdf-875b-4db9-8c88-352e21051436
# Area: 3bd2c1d3-149d-49fb-952c-8db272035f9e
# Centroid output: 01fd4f89-2b73-4e61-a51f-9c3df0c876fa

print("\n1. FIRST MOVE 'Slats original' (ddb9e6ae-7d3e-41ae-8c75-fc726c984724):")
first_move_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == 'ddb9e6ae-7d3e-41ae-8c75-fc726c984724':
            first_move_guid = comp_id
            break

if first_move_guid:
    print(f"   Component ID: {first_move_guid[:8]}...")
    try:
        result = evaluate_component(first_move_guid, graph[first_move_guid], evaluated, all_objects, output_params, graph=graph)
        evaluated[first_move_guid] = result
        if isinstance(result, dict) and 'Geometry' in result:
            geom = result['Geometry']
            print(f"   Output type: {type(geom).__name__}")
            if isinstance(geom, dict):
                print(f"   Geometry dict keys: {list(geom.keys())}")
    except Exception as e:
        print(f"   Error: {e}")

# Step 2: Polar Array (7ad636cc...)
print("\n2. POLAR ARRAY (7ad636cc-e506-4f77-bb82-4a86ba2a3fea):")
polar_array_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == '7ad636cc-e506-4f77-bb82-4a86ba2a3fea':
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
        
        print(f"     Geometry: {type(geometry_input).__name__}")
        print(f"     Plane: {plane_input}")
        print(f"     Count: {count_input}")
        print(f"     Angle: {angle_input} radians")
        
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
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

# Step 3: List Item (27933633...)
print("\n3. LIST ITEM (27933633-dbab-4dc0-a4a2-cfa309c03c45):")
list_item_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == '27933633-dbab-4dc0-a4a2-cfa309c03c45':
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
        print(f"     Index: {index_input}")
        print(f"     Wrap: {wrap_input}")
        
        result = evaluate_component(list_item_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[list_item_guid] = result
        if isinstance(result, dict) and 'Item' in result:
            item = result['Item']
            print(f"\n   Output:")
            print(f"     Type: {type(item).__name__}")
            if isinstance(item, dict):
                print(f"     Keys: {list(item.keys())}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

# Step 4: Second Move "Slats original" (0532cbdf...)
print("\n4. SECOND MOVE 'Slats original' (0532cbdf-875b-4db9-8c88-352e21051436):")
second_move_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == '0532cbdf-875b-4db9-8c88-352e21051436':
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
        print(f"     Motion: {motion_input}")
        
        result = evaluate_component(second_move_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[second_move_guid] = result
        if isinstance(result, dict) and 'Geometry' in result:
            geom = result['Geometry']
            print(f"\n   Output:")
            print(f"     Type: {type(geom).__name__}")
            if isinstance(geom, dict):
                print(f"     Keys: {list(geom.keys())}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

# Step 5: Area (3bd2c1d3...)
print("\n5. AREA (3bd2c1d3-149d-49fb-952c-8db272035f9e):")
area_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == '3bd2c1d3-149d-49fb-952c-8db272035f9e':
            area_guid = comp_id
            break

if area_guid:
    print(f"   Component ID: {area_guid[:8]}...")
    comp_info = graph[area_guid]
    try:
        geometry_input = resolve_input_value(area_guid, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
        
        print(f"\n   Inputs:")
        print(f"     Geometry: {type(geometry_input).__name__}")
        
        result = evaluate_component(area_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[area_guid] = result
        if isinstance(result, dict):
            print(f"\n   Output:")
            print(f"     Area: {result.get('Area', 'N/A')}")
            print(f"     Centroid: {result.get('Centroid', 'N/A')}")
            print(f"     Expected from screenshot: [11.32743, -27.416834, 3.8], [11.32743, -27.416834, 3.722222], ...")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print("The screenshot shows Centroid with:")
print("  - X: 11.32743 (constant)")
print("  - Y: -27.416834 (constant)")
print("  - Z: 3.8, 3.722222, 3.644444, ... (decreasing)")
print("\nThis suggests the Area component should output a list of centroids,")
print("one for each geometry item in the input list.")

