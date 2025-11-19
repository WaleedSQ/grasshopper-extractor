"""
Evaluate the complete "Slat source" chain step by step.
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

print("=" * 60)
print("Step-by-Step 'Slat source' Chain Evaluation")
print("=" * 60)
print()

# Step 1: Slat lenght (already verified = 2.5)
print("Step 1: Slat lenght")
print("-" * 60)
slat_length_guid = "fadbd125-0838-4663-8a0a-720e129a5b8f"
slat_length_output_guid = "4c2fdd4e-7313-4735-8688-1dbdf5aeaee0"
print(f"  Number component: {slat_length_guid[:8]}...")
print(f"  Output: {slat_length_output_guid[:8]}...")
print(f"  Value: 2.5 (room width 5.0 / 2)")
evaluated[slat_length_output_guid] = 2.5
print()

# Step 2: Find Y coordinate source (eedce522...)
print("Step 2: Y Coordinate Source (eedce522...)")
print("-" * 60)
y_source_guid = "eedce522-16c4-4b3a-8341-c26cc0b6bb91"

# Find component that produces this
y_source_comp = None
for key, obj in all_objects.items():
    for param_key, param_info in obj.get('params', {}).items():
        if param_key.startswith('param_output'):
            param_guid = param_info.get('data', {}).get('InstanceGuid')
            if param_guid == y_source_guid:
                y_source_comp = obj.get('instance_guid')
                print(f"  [OK] Found component: {y_source_comp[:8]}...")
                print(f"    Type: {obj.get('type', 'Unknown')}")
                print(f"    Nickname: {obj.get('nickname', '')}")
                break
    if y_source_comp:
        break

if y_source_comp:
    # Try to evaluate it
    if y_source_comp in graph:
        y_comp_info = graph[y_source_comp]
    elif y_source_comp in all_objects:
        y_obj = all_objects[y_source_comp]
        y_comp_info = {
            'type': 'component',
            'obj': y_obj,
            'instance_guid': y_source_comp
        }
        # Build inputs
        inputs_dict = {}
        for param_key, param_info in y_obj.get('params', {}).items():
            if param_key.startswith('param_input'):
                param_name = param_info.get('data', {}).get('Name', '')
                sources = param_info.get('sources', [])
                inputs_dict[param_key] = {
                    'name': param_name,
                    'sources': [{'guid': s.get('guid'), 'source_guid': s.get('guid')} for s in sources]
                }
        y_comp_info['inputs'] = inputs_dict
        
        try:
            result = evaluate_component(
                y_source_comp,
                y_comp_info,
                evaluated,
                all_objects,
                output_params
            )
            evaluated[y_source_comp] = result
            if y_source_guid in output_params:
                evaluated[y_source_guid] = result
            print(f"  Result: {result}")
        except Exception as e:
            print(f"  [ERROR] Could not evaluate: {e}")

print()

# Step 3: Construct Point A
print("Step 3: Construct Point A (be907c11...)")
print("-" * 60)
point_a_comp_guid = "be907c11-5a37-4cf5-9736-0f3c61ba7014"
point_a_output_guid = "902866aa-e5b3-4461-9877-73b22ea3618a"

if point_a_comp_guid in all_objects:
    point_a_obj = all_objects[point_a_comp_guid]
    print(f"  Component: {point_a_comp_guid[:8]}...")
    
    # Build comp_info
    point_a_comp_info = {
        'type': 'component',
        'obj': point_a_obj,
        'instance_guid': point_a_comp_guid
    }
    inputs_dict = {}
    for param_key, param_info in point_a_obj.get('params', {}).items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            inputs_dict[param_key] = {
                'name': param_name,
                'sources': [{'guid': s.get('guid'), 'source_guid': s.get('guid')} for s in sources]
            }
    point_a_comp_info['inputs'] = inputs_dict
    
    try:
        result = evaluate_component(
            point_a_comp_guid,
            point_a_comp_info,
            evaluated,
            all_objects,
            output_params
        )
        evaluated[point_a_comp_guid] = result
        if point_a_output_guid in output_params:
            evaluated[point_a_output_guid] = result
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  [ERROR] Could not evaluate: {e}")

print()

# Step 4: Construct Point B
print("Step 4: Construct Point B (67b3eb53...)")
print("-" * 60)
point_b_comp_guid = "67b3eb53-9ea7-4280-bf8b-ae16c080cc23"
point_b_output_guid = "ef17623c-d081-46f9-8259-2ad83ec05d94"

if point_b_comp_guid in all_objects:
    point_b_obj = all_objects[point_b_comp_guid]
    print(f"  Component: {point_b_comp_guid[:8]}...")
    
    # Build comp_info
    point_b_comp_info = {
        'type': 'component',
        'obj': point_b_obj,
        'instance_guid': point_b_comp_guid
    }
    inputs_dict = {}
    for param_key, param_info in point_b_obj.get('params', {}).items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            persistent_values = param_info.get('persistent_values', [])
            inputs_dict[param_key] = {
                'name': param_name,
                'sources': [{'guid': s.get('guid'), 'source_guid': s.get('guid')} for s in sources],
                'persistent_values': persistent_values
            }
    point_b_comp_info['inputs'] = inputs_dict
    
    try:
        result = evaluate_component(
            point_b_comp_guid,
            point_b_comp_info,
            evaluated,
            all_objects,
            output_params
        )
        evaluated[point_b_comp_guid] = result
        if point_b_output_guid in output_params:
            evaluated[point_b_output_guid] = result
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  [ERROR] Could not evaluate: {e}")

print()

# Step 5: Rectangle 2Pt
print("Step 5: Rectangle 2Pt (a3eb185f...)")
print("-" * 60)
rect_comp_guid = "a3eb185f-a7cb-4727-aeaf-d5899f934b99"
rect_output_guid = "dbc236d4-a2fe-48a8-a86e-eebfb04b1053"

if rect_comp_guid in all_objects:
    rect_obj = all_objects[rect_comp_guid]
    print(f"  Component: {rect_comp_guid[:8]}...")
    
    # Build comp_info
    rect_comp_info = {
        'type': 'component',
        'obj': rect_obj,
        'instance_guid': rect_comp_guid
    }
    inputs_dict = {}
    for param_key, param_info in rect_obj.get('params', {}).items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('Name', '')
            sources = param_info.get('sources', [])
            inputs_dict[param_key] = {
                'name': param_name,
                'sources': [{'guid': s.get('guid'), 'source_guid': s.get('guid')} for s in sources]
            }
    rect_comp_info['inputs'] = inputs_dict
    
    try:
        result = evaluate_component(
            rect_comp_guid,
            rect_comp_info,
            evaluated,
            all_objects,
            output_params
        )
        evaluated[rect_comp_guid] = result
        if rect_output_guid in output_params:
            evaluated[rect_output_guid] = result
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  [ERROR] Could not evaluate: {e}")

print()

# Step 6: Surface
print("Step 6: Surface 'Slat source' (8fec620f...)")
print("-" * 60)
surface_comp_guid = "8fec620f-ff7f-4b94-bb64-4c7fce2fcb34"

if surface_comp_guid in graph:
    surface_comp_info = graph[surface_comp_guid]
    try:
        result = evaluate_component(
            surface_comp_guid,
            surface_comp_info,
            evaluated,
            all_objects,
            output_params
        )
        evaluated[surface_comp_guid] = result
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  [ERROR] Could not evaluate: {e}")

print()
print("=" * 60)
print("Final Results:")
print("-" * 60)
print(f"  Construct Point A: {evaluated.get(point_a_output_guid, 'Not evaluated')}")
print(f"  Construct Point B: {evaluated.get(point_b_output_guid, 'Not evaluated')}")
print(f"  Rectangle 2Pt: {evaluated.get(rect_output_guid, 'Not evaluated')}")
print(f"  Surface 'Slat source': {evaluated.get(surface_comp_guid, 'Not evaluated')}")

