"""
Check the Motion input to the second Move "Slats original" component (0532cbdf...)
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, get_external_inputs, resolve_input_value

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
print("CHECKING SECOND MOVE 'Slats original' MOTION INPUT")
print("=" * 80)

# Second Move "Slats original" (0532cbdf-875b-4db9-8c88-352e21051436)
second_move_guid = None
for comp_id, comp in graph.items():
    if isinstance(comp, dict):
        obj = comp.get('obj', {})
        if obj.get('instance_guid') == '0532cbdf-875b-4db9-8c88-352e21051436':
            second_move_guid = comp_id
            break

if second_move_guid:
    print(f"\nComponent ID: {second_move_guid[:8]}...")
    comp_info = graph[second_move_guid]
    
    # Check Motion input (param_input_1)
    print("\nMotion Input (param_input_1):")
    param_info = comp_info['obj'].get('params', {}).get('param_input_1', {})
    sources = param_info.get('sources', [])
    persistent_values = param_info.get('persistent_values', [])
    
    print(f"  Sources: {len(sources)}")
    for src in sources:
        source_guid = src.get('guid')
        print(f"    Source GUID: {source_guid}")
        if source_guid == 'd0668a07-838c-481c-88eb-191574362cc2':
            print(f"      [OK] This is Amplitude output")
        else:
            print(f"      ? Unknown source")
    
    print(f"  PersistentData: {persistent_values}")
    
    # Try to resolve the Motion input
    print("\nResolving Motion input value:")
    try:
        motion_value = resolve_input_value(second_move_guid, 'param_input_1', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"  Resolved value: {motion_value}")
        print(f"  Type: {type(motion_value).__name__}")
        if isinstance(motion_value, list):
            if len(motion_value) > 0 and isinstance(motion_value[0], list):
                print(f"  List of vectors, length: {len(motion_value)}")
                print(f"  First vector: {motion_value[0]}")
            elif len(motion_value) == 3:
                print(f"  Single vector: {motion_value}")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("EXPECTED:")
print("  Motion should be Amplitude: [11.32743, -27.346834, 0.0]")
print("  But combined with Unit Z: [[0.0, 0.0, 3.8], [0.0, 0.0, 3.722222], ...]")
print("  Result: [[11.32743, -27.346834, 3.8], [11.32743, -27.346834, 3.722222], ...]")
print("\nACTUAL:")
print("  Motion is resolving to: [0.0, 0.07, 3.8] (from first Move's Vector 2Pt)")

