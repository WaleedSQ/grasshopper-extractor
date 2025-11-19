"""
Check what the evaluator produces for "Slat lenght" output.
"""
import json

# Load the component graph
with open('complete_component_graph.json', 'r') as f:
    graph = json.load(f)

# Find the Division component that produces output 4c2fdd4e...
output_guid = "4c2fdd4e-7313-4735-8688-1dbdf5aeaee0"
division_comp_guid = "32cc502c-07b0-4d58-aef1-8acf8b2f4015"

print("=" * 60)
print("Slat lenght Component Analysis")
print("=" * 60)
print()

print("Division Component (32cc502c...):")
print("-" * 60)
if division_comp_guid in graph:
    comp_info = graph[division_comp_guid]
    if isinstance(comp_info, dict):
        inputs = comp_info.get('inputs', {})
        print("  Inputs:")
        for input_key, input_info in inputs.items():
            input_name = input_info.get('name', 'Unknown')
            sources = input_info.get('sources', [])
            print(f"    {input_name}:")
            for source in sources:
                source_guid = source.get('source_guid')
                source_type = source.get('type', 'unknown')
                source_name = source.get('source_obj_name', '')
                print(f"      Source: {source_guid[:8] if source_guid else 'N/A'}... ({source_type}) {source_name}")
        
        # Check for constant value in input B
        if 'param_input_1' in inputs:
            param_b = inputs['param_input_1']
            persistent_values = param_b.get('persistent_values', [])
            if persistent_values:
                print(f"    Input B constant value: {persistent_values[0]}")
        
        outputs = comp_info.get('outputs', {})
        print("  Outputs:")
        for output_key, output_info in outputs.items():
            output_guid_check = output_info.get('instance_guid')
            if output_guid_check == output_guid:
                print(f"    [MATCH] Output GUID: {output_guid[:8]}...")
                print(f"      This feeds into 'Slat lenght' Number component")
else:
    print("  [X] Component not found in graph")

print()
print("Expected Calculation:")
print("-" * 60)
print("  From GHX: room width (5.0) / 2 = 2.5")
print("  From screenshot: room width (5.0) - slat width (0.080) = 4.92")
print()
print("  Note: There's a discrepancy between GHX and screenshot!")
print("  Need to verify which is correct.")

