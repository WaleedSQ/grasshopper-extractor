"""
Verify the "Slat source" Surface component calculation step by step.
From screenshot: Surface receives geometry from Rectangle 2Pt component.
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, get_external_inputs, evaluate_component, resolve_input_value
import json

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

# Surface component GUID
surface_comp_guid = "8fec620f-ff7f-4b94-bb64-4c7fce2fcb34"
# Rectangle 2Pt output GUID (source for Surface)
rectangle_output_guid = "dbc236d4-a2fe-48a8-a86e-eebfb04b1053"

print("=" * 60)
print("Evaluating 'Slat source' Surface Component")
print("=" * 60)
print()

# Step 1: Find Rectangle 2Pt component that produces the output
print("Step 1: Find Rectangle 2Pt Component")
print("-" * 60)

# Find component that produces rectangle_output_guid
rectangle_comp_guid = None
for comp_id, comp_info in graph.items():
    if isinstance(comp_info, dict) and comp_info.get('type') == 'component':
        outputs = comp_info.get('outputs', {})
        for output_key, output_info in outputs.items():
            if output_info.get('instance_guid') == rectangle_output_guid:
                rectangle_comp_guid = comp_id
                comp_type = comp_info.get('obj', {}).get('type', 'Unknown')
                comp_nickname = comp_info.get('obj', {}).get('nickname', '')
                print(f"  [OK] Found component: {comp_id[:8]}... ({comp_type}) '{comp_nickname}'")
                print(f"    Output GUID: {rectangle_output_guid[:8]}...")
                break
        if rectangle_comp_guid:
            break

if not rectangle_comp_guid:
    print("  [X] Rectangle 2Pt component not found in graph")
    print("  Searching in all_objects...")
    # Search in all_objects
    for key, obj in all_objects.items():
        for param_key, param_info in obj.get('params', {}).items():
            if param_key.startswith('param_output'):
                param_guid = param_info.get('data', {}).get('InstanceGuid')
                if param_guid == rectangle_output_guid:
                    rectangle_comp_guid = obj.get('instance_guid')
                    print(f"  [OK] Found in all_objects: {rectangle_comp_guid[:8]}...")
                    break
        if rectangle_comp_guid:
            break

print()

# Step 2: Evaluate Rectangle 2Pt component
if rectangle_comp_guid:
    print("Step 2: Evaluate Rectangle 2Pt Component")
    print("-" * 60)
    
    if rectangle_comp_guid in graph:
        rect_comp_info = graph[rectangle_comp_guid]
    elif rectangle_comp_guid in all_objects:
        # Need to build comp_info structure
        rect_obj = all_objects[rectangle_comp_guid]
        rect_comp_info = {
            'type': 'component',
            'obj': rect_obj,
            'instance_guid': rectangle_comp_guid
        }
        # Build inputs structure
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
    else:
        rect_comp_info = None
    
    if rect_comp_info:
        print(f"  Component: {rectangle_comp_guid[:8]}...")
        print(f"  Type: {rect_comp_info.get('obj', {}).get('type', 'Unknown')}")
        print()
        
        # Get inputs
        inputs = rect_comp_info.get('inputs', {})
        print("  Inputs:")
        for input_key, input_info in inputs.items():
            input_name = input_info.get('name', 'Unknown')
            sources = input_info.get('sources', [])
            print(f"    {input_name}:")
            for source in sources:
                source_guid = source.get('source_guid') or source.get('guid')
                print(f"      Source: {source_guid[:8] if source_guid else 'N/A'}...")
        
        # Evaluate Rectangle 2Pt
        print()
        print("  Evaluating Rectangle 2Pt...")
        try:
            external_inputs = get_external_inputs()
            evaluated = {}
            
            # Resolve inputs
            resolved_inputs = {}
            for input_key, input_info in inputs.items():
                input_name = input_info.get('name', 'Unknown')
                param_info_full = rect_comp_info['obj'].get('params', {}).get(input_key, {})
                value = resolve_input_value(
                    rectangle_comp_guid,
                    input_key,
                    rect_comp_info,
                    evaluated,
                    all_objects,
                    output_params,
                    param_info_full
                )
                resolved_inputs[input_name] = value
                print(f"    {input_name} = {value}")
            
            # Evaluate
            result = evaluate_component(
                rectangle_comp_guid,
                rect_comp_info,
                evaluated,
                all_objects,
                output_params
            )
            
            print()
            print("  Result:")
            print(f"    {result}")
            
            # Store in evaluated for Surface component
            evaluated[rectangle_comp_guid] = result
            if rectangle_output_guid in output_params:
                # Also store by output GUID
                evaluated[rectangle_output_guid] = result
            
        except Exception as e:
            print(f"  [ERROR] Evaluation failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("  [X] Could not build component info")

print()

# Step 3: Evaluate Surface component
print("Step 3: Evaluate Surface Component")
print("-" * 60)

if surface_comp_guid in graph:
    surface_comp_info = graph[surface_comp_guid]
    print(f"  Component: {surface_comp_guid[:8]}...")
    print(f"  Type: {surface_comp_info.get('obj', {}).get('type', 'Unknown')}")
    print(f"  Nickname: {surface_comp_info.get('obj', {}).get('nickname', '')}")
    print()
    
    # Check Container-level Source
    surface_obj = all_objects.get(surface_comp_guid, {})
    container_source = None
    if 'params' not in surface_obj or not surface_obj.get('params'):
        # Check if there's a Container-level Source
        print("  Checking for Container-level Source...")
        # The source should be rectangle_output_guid
        if rectangle_output_guid in output_params:
            print(f"  [OK] Found source: {rectangle_output_guid[:8]}... (Rectangle 2Pt output)")
            container_source = rectangle_output_guid
    
    print("  Surface component receives geometry from Rectangle 2Pt")
    print("  (This is a pass-through component for geometry)")
    
else:
    print(f"  [X] Surface component {surface_comp_guid[:8]}... not found in graph")

print()
print("=" * 60)

