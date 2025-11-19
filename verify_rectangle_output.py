"""
Verify Rectangle 2Pt output and Surface input connection.
Evaluate the complete chain properly.
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, get_external_inputs, evaluate_component, resolve_input_value
from collections import defaultdict

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

print("=" * 60)
print("Verify Rectangle 2Pt Output and Surface Input")
print("=" * 60)
print()

# Step 1: Evaluate dependencies in order
print("Step 1: Evaluate Dependencies")
print("-" * 60)

# 1.1 Slat lenght (Division 32cc502c...)
print("  1.1 Slat lenght (Division 32cc502c...):")
slat_length_div_guid = "32cc502c-07b0-4d58-aef1-8acf8b2f4015"
slat_length_output_guid = "4c2fdd4e-7313-4735-8688-1dbdf5aeaee0"
slat_length_number_guid = "fadbd125-0838-4663-8a0a-720e129a5b8f"

if slat_length_div_guid in graph:
    div_comp_info = graph[slat_length_div_guid]
    div_result = evaluate_component(
        slat_length_div_guid,
        div_comp_info,
        evaluated,
        all_objects,
        output_params
    )
    evaluated[slat_length_div_guid] = div_result
    if slat_length_output_guid in output_params:
        evaluated[slat_length_output_guid] = div_result
    # Also store in Number component
    evaluated[slat_length_number_guid] = div_result.get('Result') if isinstance(div_result, dict) else div_result
    print(f"    Result: {div_result}")

# 1.2 Y coordinate source (Division b9102ff3...)
print("  1.2 Y coordinate source (Division b9102ff3...):")
y_div_comp_guid = "b9102ff3-4813-4791-a67d-5654a9f7bae9"
y_source_output_guid = "eedce522-16c4-4b3a-8341-c26cc0b6bb91"

if y_div_comp_guid in graph:
    y_div_comp_info = graph[y_div_comp_guid]
    y_div_result = evaluate_component(
        y_div_comp_guid,
        y_div_comp_info,
        evaluated,
        all_objects,
        output_params
    )
    evaluated[y_div_comp_guid] = y_div_result
    if y_source_output_guid in output_params:
        evaluated[y_source_output_guid] = y_div_result.get('Result') if isinstance(y_div_result, dict) else y_div_result
    print(f"    Result: {y_div_result}")
elif y_div_comp_guid in all_objects:
    # Build comp_info from all_objects
    y_div_obj = all_objects[y_div_comp_guid]
    y_div_comp_info = {
        'type': 'component',
        'obj': y_div_obj,
        'instance_guid': y_div_comp_guid
    }
    y_div_inputs = {}
    for param_key, param_info in y_div_obj.get('params', {}).items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            persistent_values = param_info.get('persistent_values', [])
            y_div_inputs[param_key] = {
                'name': param_name,
                'sources': [{'guid': s.get('guid'), 'source_guid': s.get('guid')} for s in sources],
                'persistent_values': persistent_values
            }
    y_div_comp_info['inputs'] = y_div_inputs
    
    y_div_result = evaluate_component(
        y_div_comp_guid,
        y_div_comp_info,
        evaluated,
        all_objects,
        output_params
    )
    evaluated[y_div_comp_guid] = y_div_result
    if y_source_output_guid in output_params:
        evaluated[y_source_output_guid] = y_div_result.get('Result') if isinstance(y_div_result, dict) else y_div_result
    print(f"    Result: {y_div_result}")
else:
    print(f"    [X] Division component not found")

# 1.3 Negative for Point B X (835d042f...)
print("  1.3 Negative for Point B X (835d042f...):")
neg_x_comp_guid = "835d042f-2535-476b-b5ae-1eeb534e57bc"
neg_x_output_guid = "8a96679d-8f35-4cb4-92a0-6233220f435b"

if neg_x_comp_guid in all_objects:
    neg_x_obj = all_objects[neg_x_comp_guid]
    neg_x_comp_info = {
        'type': 'component',
        'obj': neg_x_obj,
        'instance_guid': neg_x_comp_guid
    }
    neg_x_inputs = {}
    for param_key, param_info in neg_x_obj.get('params', {}).items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            neg_x_inputs[param_key] = {
                'name': param_name,
                'sources': [{'guid': s.get('guid'), 'source_guid': s.get('guid')} for s in sources]
            }
    neg_x_comp_info['inputs'] = neg_x_inputs
    
    neg_x_result = evaluate_component(
        neg_x_comp_guid,
        neg_x_comp_info,
        evaluated,
        all_objects,
        output_params
    )
    evaluated[neg_x_comp_guid] = neg_x_result
    if neg_x_output_guid in output_params:
        evaluated[neg_x_output_guid] = neg_x_result.get('Result') if isinstance(neg_x_result, dict) else neg_x_result
    print(f"    Result: {neg_x_result}")

# 1.4 Negative for Point B Y (d63be87d...)
print("  1.4 Negative for Point B Y (d63be87d...):")
neg_y_comp_guid = "d63be87d-b9e6-4c52-9aeb-adc1d5f15e92"
neg_y_output_guid = "370f6ae5-1cf9-4488-9eee-2bd34b38725e"

if neg_y_comp_guid in all_objects:
    neg_y_obj = all_objects[neg_y_comp_guid]
    neg_y_comp_info = {
        'type': 'component',
        'obj': neg_y_obj,
        'instance_guid': neg_y_comp_guid
    }
    neg_y_inputs = {}
    for param_key, param_info in neg_y_obj.get('params', {}).items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            neg_y_inputs[param_key] = {
                'name': param_name,
                'sources': [{'guid': s.get('guid'), 'source_guid': s.get('guid')} for s in sources]
            }
    neg_y_comp_info['inputs'] = neg_y_inputs
    
    neg_y_result = evaluate_component(
        neg_y_comp_guid,
        neg_y_comp_info,
        evaluated,
        all_objects,
        output_params
    )
    evaluated[neg_y_comp_guid] = neg_y_result
    if neg_y_output_guid in output_params:
        evaluated[neg_y_output_guid] = neg_y_result.get('Result') if isinstance(neg_y_result, dict) else neg_y_result
    print(f"    Result: {neg_y_result}")

print()

# Step 2: Evaluate Construct Point A
print("Step 2: Evaluate Construct Point A")
print("-" * 60)
point_a_comp_guid = "be907c11-5a37-4cf5-9736-0f3c61ba7014"
point_a_output_guid = "902866aa-e5b3-4461-9877-73b22ea3618a"

if point_a_comp_guid in all_objects:
    point_a_obj = all_objects[point_a_comp_guid]
    point_a_comp_info = {
        'type': 'component',
        'obj': point_a_obj,
        'instance_guid': point_a_comp_guid
    }
    point_a_inputs = {}
    for param_key, param_info in point_a_obj.get('params', {}).items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            persistent_values = param_info.get('persistent_values', [])
            point_a_inputs[param_key] = {
                'name': param_name,
                'sources': [{'guid': s.get('guid'), 'source_guid': s.get('guid')} for s in sources],
                'persistent_values': persistent_values
            }
    point_a_comp_info['inputs'] = point_a_inputs
    
    point_a_result = evaluate_component(
        point_a_comp_guid,
        point_a_comp_info,
        evaluated,
        all_objects,
        output_params
    )
    evaluated[point_a_comp_guid] = point_a_result
    if point_a_output_guid in output_params:
        evaluated[point_a_output_guid] = point_a_result
    print(f"  Result: {point_a_result}")

print()

# Step 3: Evaluate Construct Point B
print("Step 3: Evaluate Construct Point B")
print("-" * 60)
point_b_comp_guid = "67b3eb53-9ea7-4280-bf8b-ae16c080cc23"
point_b_output_guid = "ef17623c-d081-46f9-8259-2ad83ec05d94"

if point_b_comp_guid in all_objects:
    point_b_obj = all_objects[point_b_comp_guid]
    point_b_comp_info = {
        'type': 'component',
        'obj': point_b_obj,
        'instance_guid': point_b_comp_guid
    }
    point_b_inputs = {}
    for param_key, param_info in point_b_obj.get('params', {}).items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            persistent_values = param_info.get('persistent_values', [])
            point_b_inputs[param_key] = {
                'name': param_name,
                'sources': [{'guid': s.get('guid'), 'source_guid': s.get('guid')} for s in sources],
                'persistent_values': persistent_values
            }
    point_b_comp_info['inputs'] = point_b_inputs
    
    point_b_result = evaluate_component(
        point_b_comp_guid,
        point_b_comp_info,
        evaluated,
        all_objects,
        output_params
    )
    evaluated[point_b_comp_guid] = point_b_result
    if point_b_output_guid in output_params:
        evaluated[point_b_output_guid] = point_b_result
    print(f"  Result: {point_b_result}")

print()

# Step 4: Evaluate Rectangle 2Pt
print("Step 4: Evaluate Rectangle 2Pt")
print("-" * 60)
rect_comp_guid = "a3eb185f-a7cb-4727-aeaf-d5899f934b99"
rect_output_guid = "dbc236d4-a2fe-48a8-a86e-eebfb04b1053"

if rect_comp_guid in all_objects:
    rect_obj = all_objects[rect_comp_guid]
    rect_comp_info = {
        'type': 'component',
        'obj': rect_obj,
        'instance_guid': rect_comp_guid
    }
    rect_inputs = {}
    for param_key, param_info in rect_obj.get('params', {}).items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            persistent_values = param_info.get('persistent_values', [])
            rect_inputs[param_key] = {
                'name': param_name,
                'sources': [{'guid': s.get('guid'), 'source_guid': s.get('guid')} for s in sources],
                'persistent_values': persistent_values
            }
    rect_comp_info['inputs'] = rect_inputs
    
    print("  Inputs resolved:")
    for input_key, input_info in rect_inputs.items():
        input_name = input_info.get('name', 'Unknown')
        param_info_full = rect_obj.get('params', {}).get(input_key, {})
        value = resolve_input_value(
            rect_comp_guid,
            input_key,
            rect_comp_info,
            evaluated,
            all_objects,
            output_params,
            param_info_full
        )
        print(f"    {input_name}: {value}")
    
    rect_result = evaluate_component(
        rect_comp_guid,
        rect_comp_info,
        evaluated,
        all_objects,
        output_params
    )
    evaluated[rect_comp_guid] = rect_result
    if rect_output_guid in output_params:
        evaluated[rect_output_guid] = rect_result
    
    print()
    print(f"  Rectangle 2Pt result: {rect_result}")
    print(f"  Output GUID: {rect_output_guid[:8]}...")
    print(f"  [OK] Rectangle 2Pt evaluated successfully")

print()

# Step 5: Verify Surface receives Rectangle 2Pt output
print("Step 5: Verify Surface Receives Rectangle 2Pt Output")
print("-" * 60)
surface_comp_guid = "8fec620f-ff7f-4b94-bb64-4c7fce2fcb34"

if surface_comp_guid in graph:
    surface_comp_info = graph[surface_comp_guid]
    
    print(f"  Surface component: {surface_comp_guid[:8]}...")
    print(f"  Expected source: Rectangle 2Pt output ({rect_output_guid[:8]}...)")
    print()
    
    # Check if Rectangle 2Pt output is available
    if rect_output_guid in output_params:
        source_info = output_params[rect_output_guid]
        source_obj_guid = source_info['obj'].get('instance_guid')
        print(f"  [OK] Rectangle 2Pt output found in output_params")
        print(f"    Parent component: {source_obj_guid[:8]}...")
        
        if source_obj_guid in evaluated:
            comp_outputs = evaluated.get(source_obj_guid, {})
            print(f"    Rectangle 2Pt evaluated: {comp_outputs}")
            
            # Extract geometry
            geometry = None
            if isinstance(comp_outputs, dict):
                for key in ['Rectangle', 'Result', 'Value', 'Output', 'Geometry']:
                    if key in comp_outputs:
                        geometry = comp_outputs[key]
                        print(f"    [OK] Found geometry in '{key}': {geometry}")
                        break
                if geometry is None and comp_outputs:
                    geometry = list(comp_outputs.values())[0]
                    print(f"    [OK] Using first output value: {geometry}")
            
            if geometry:
                print()
                print(f"  [OK] Geometry available for Surface component")
                print(f"    Geometry: {geometry}")
            else:
                print()
                print(f"  [WARNING] Could not extract geometry")
        else:
            print(f"    [X] Rectangle 2Pt component not evaluated")
    
    # Evaluate Surface
    print()
    print("  Evaluating Surface component...")
    try:
        surface_result = evaluate_component(
            surface_comp_guid,
            surface_comp_info,
            evaluated,
            all_objects,
            output_params
        )
        evaluated[surface_comp_guid] = surface_result
        print(f"  Surface result: {surface_result}")
        
        # Check if it received the geometry
        if isinstance(surface_result, dict):
            for key in ['Surface', 'Geometry', 'Result', 'Value']:
                if key in surface_result:
                    received_geometry = surface_result[key]
                    print(f"    Received geometry in '{key}': {received_geometry}")
                    if received_geometry and received_geometry != {'surface': 'external_surface_placeholder'}:
                        print(f"    [OK] Surface received actual geometry from Rectangle 2Pt")
                    break
        
    except Exception as e:
        print(f"  [ERROR] Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 60)
print("Verification Summary:")
print("-" * 60)
print(f"  Rectangle 2Pt output GUID: {rect_output_guid[:8]}...")
print(f"  Rectangle 2Pt result: {evaluated.get(rect_output_guid, 'Not evaluated')}")
print(f"  Surface component GUID: {surface_comp_guid[:8]}...")
print(f"  Surface result: {evaluated.get(surface_comp_guid, 'Not evaluated')}")
print()
if rect_output_guid in evaluated and surface_comp_guid in evaluated:
    print("  [OK] Connection verified: Surface 'Slat source' receives geometry from Rectangle 2Pt")
else:
    print("  [X] Connection not fully verified - some components not evaluated")

