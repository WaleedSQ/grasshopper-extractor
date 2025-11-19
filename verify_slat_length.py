"""
Verify the "Slat lenght" calculation step by step.
From screenshot: room width (5) - slat width (0.080) = 4.92
"""
import json

# Load external inputs
with open('external_inputs.json', 'r') as f:
    external_inputs = json.load(f)

# Expected values from screenshot
room_width = 5.0  # From "room width" slider
slat_width = 0.080  # From "Slat width" slider
# Note: Screenshot shows subtraction (5 - 0.080 = 4.92)
# But GHX shows Division component (room width / 2 = 2.5)
expected_result_subtraction = room_width - slat_width  # 4.92
expected_result_division = room_width / 2  # 2.5

print("=" * 60)
print("Step-by-Step Verification: Slat lenght Calculation")
print("=" * 60)
print()

# Step 1: Check external inputs
print("Step 1: External Inputs")
print("-" * 60)
room_width_guid = "a7d2817a-3182-496e-a453-80e7eeba16fa"
slat_width_guid = "0d27dd7f-44bf-4778-8d07-d44b711c47f2"

if room_width_guid in external_inputs:
    room_width_value = external_inputs[room_width_guid].get('value') if isinstance(external_inputs[room_width_guid], dict) else external_inputs[room_width_guid]
    print(f"  [OK] Room width ({room_width_guid[:8]}...): {room_width_value}")
else:
    print(f"  [X] Room width ({room_width_guid[:8]}...): NOT FOUND")
    room_width_value = None

if slat_width_guid in external_inputs:
    slat_width_value = external_inputs[slat_width_guid].get('value') if isinstance(external_inputs[slat_width_guid], dict) else external_inputs[slat_width_guid]
    print(f"  [OK] Slat width ({slat_width_guid[:8]}...): {slat_width_value}")
else:
    print(f"  [X] Slat width ({slat_width_guid[:8]}...): NOT FOUND")
    slat_width_value = None

print()

# Step 2: Find subtraction component
print("Step 2: Find Subtraction Component")
print("-" * 60)
print("  Looking for subtraction component with output GUID: 4c2fdd4e...")
print("  This output feeds into 'Slat lenght' Number component (fadbd125...)")
print()

# Load component graph to find the subtraction
try:
    with open('complete_component_graph.json', 'r') as f:
        graph = json.load(f)
    
    # Find component that produces output 4c2fdd4e...
    output_guid = "4c2fdd4e-7313-4735-8688-1dbdf5aeaee0"
    found_component = None
    
    for comp_id, comp_info in graph.items():
        if isinstance(comp_info, dict) and comp_info.get('type') == 'component':
            outputs = comp_info.get('outputs', {})
            for output_key, output_info in outputs.items():
                if output_info.get('instance_guid') == output_guid:
                    found_component = comp_id
                    comp_type = comp_info.get('obj', {}).get('type', 'Unknown')
                    comp_nickname = comp_info.get('obj', {}).get('nickname', '')
                    print(f"  [OK] Found component: {comp_id[:8]}... ({comp_type}) '{comp_nickname}'")
                    print(f"    Output GUID: {output_guid[:8]}...")
                    break
            if found_component:
                break
    
    if found_component:
        comp_info = graph[found_component]
        inputs = comp_info.get('inputs', {})
        print()
        print("  Component Inputs:")
        for input_key, input_info in inputs.items():
            input_name = input_info.get('name', 'Unknown')
            sources = input_info.get('sources', [])
            print(f"    {input_name}:")
            for source in sources:
                source_guid = source.get('source_guid')
                source_type = source.get('type', 'unknown')
                source_name = source.get('source_obj_name', '')
                print(f"      Source: {source_guid[:8] if source_guid else 'N/A'}... ({source_type}) {source_name}")
    else:
        print("  [X] Component not found in graph")
        print("  Need to search GHX file directly")
        
except FileNotFoundError:
    print("  ✗ complete_component_graph.json not found")

print()

# Step 3: Calculate expected result
print("Step 3: Expected Calculation")
print("-" * 60)
if room_width_value is not None and slat_width_value is not None:
    calculated = room_width_value - slat_width_value
    print(f"  Room width: {room_width_value}")
    print(f"  Slat width: {slat_width_value}")
    print(f"  Calculation (Subtraction): {room_width_value} - {slat_width_value} = {calculated}")
    print(f"  Expected (from screenshot - subtraction): {expected_result_subtraction}")
    print(f"  Match (subtraction): {'[OK]' if abs(calculated - expected_result_subtraction) < 0.001 else '[X]'}")
    print()
    calculated_div = room_width_value / 2
    print(f"  Calculation (Division by 2): {room_width_value} / 2 = {calculated_div}")
    print(f"  Expected (from GHX - division): {expected_result_division}")
    print(f"  Match (division): {'[OK]' if abs(calculated_div - expected_result_division) < 0.001 else '[X]'}")
else:
    print("  Cannot calculate - missing input values")

print()

# Step 4: Check if component is evaluated
print("Step 4: Check Evaluator Output")
print("-" * 60)
print("  Run: python evaluate_rotatingslats.py")
print("  Look for component output: 4c2fdd4e...")
print("  Or Number component 'Slat lenght' (fadbd125...)")
print()

print("=" * 60)

