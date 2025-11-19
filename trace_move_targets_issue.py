"""
Trace why Move component "Targets" (80fd9f48) is getting wrong output.
The issue: List Item c0f3d527 returns None instead of the list of points.
"""

import json

# Load evaluation results
with open('evaluation_results.md', 'r') as f:
    content = f.read()

# Find the relevant components
print("=" * 80)
print("TRACING MOVE COMPONENT 'Targets' ISSUE")
print("=" * 80)

# Component chain:
# 1. Polar Array e7683176... outputs: [[[0.0, -4.5, 4.0], ...]]
# 2. List Item c0f3d527... should get index 0 from that list
# 3. Move b38a38f1... (output 80fd9f48) should move the list item by Amplitude vector

print("\n1. POLAR ARRAY OUTPUT (e7683176...):")
print("   Component 8: Polar Array PA.Geometry")
print("   Output: [[[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]]")
print("   This is a list of lists of points")

print("\n2. LIST ITEM INPUT (c0f3d527...):")
print("   Component 61: List Item LI.i")
print("   List source: e7683176... (Polar Array Geometry output)")
print("   Index: 0 (from Value List 'Orientations')")
print("   Wrap: true")
print("   Expected output: [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]")
print("   Actual output: None [ERROR]")

print("\n3. AMPLITUDE OUTPUT (d0668a07...):")
print("   Component 47: Amplitude Amplitude.Vector")
print("   Output: [11.327429598006665, -27.346834162334087, 0.0] [OK]")

print("\n4. MOVE COMPONENT 'Targets' (b38a38f1... / 80fd9f48...):")
print("   Component 38/128: Move Targets")
print("   Geometry input: c0f3d527... (List Item output) = None ❌")
print("   Motion input: d0668a07... (Amplitude output) = [11.327429598006665, -27.346834162334087, 0.0] [OK]")
print("   Expected: Move each point in the list by the motion vector")
print("   Actual: Getting wrong output because geometry is None [ERROR]")

print("\n" + "=" * 80)
print("ROOT CAUSE:")
print("=" * 80)
print("The List Item component (c0f3d527...) is returning None instead of")
print("extracting the first list from the Polar Array output.")
print("\nPossible causes:")
print("1. Output parameter extraction failing - Polar Array output not being")
print("   correctly extracted from evaluated component")
print("2. List Item function not handling nested list structure correctly")
print("3. Output parameter GUID not matching or not registered correctly")

print("\n" + "=" * 80)
print("CHECKING OUTPUT PARAMETER RESOLUTION")
print("=" * 80)

# Load the graph to check output_params registration
try:
    with open('complete_component_graph.json', 'r') as f:
        graph_data = json.load(f)
    
    components = graph_data.get('components', {})
    
    # Find Polar Array component
    polar_array_guid = None
    for comp_id, comp in components.items():
        if isinstance(comp, dict):
            obj = comp.get('obj', {})
            if obj.get('type') == 'Polar Array':
                # Check if it has the output parameter e7683176...
                for param_key, param_info in obj.get('params', {}).items():
                    if param_key.startswith('param_output'):
                        param_guid = param_info.get('data', {}).get('InstanceGuid')
                        if param_guid == 'e7683176-0e64-40c9-ae31-e6c1c043bd15':
                            polar_array_guid = comp_id
                            print(f"[OK] Found Polar Array component: {comp_id[:8]}...")
                            print(f"  Output param GUID: {param_guid}")
                            print(f"  Output param NickName: {param_info.get('data', {}).get('NickName', 'N/A')}")
                            break
                if polar_array_guid:
                    break
    
    # Find List Item component
    list_item_guid = None
    for comp_id, comp in components.items():
        if isinstance(comp, dict):
            obj = comp.get('obj', {})
            if obj.get('type') == 'List Item':
                instance_guid = obj.get('instance_guid')
                if instance_guid and instance_guid.startswith('c0f3d527'):
                    list_item_guid = comp_id
                    print(f"\n[OK] Found List Item component: {comp_id[:8]}...")
                    print(f"  Instance GUID: {instance_guid}")
                    # Check its List input source
                    inputs = comp.get('inputs', {})
                    list_input = inputs.get('param_input_0', {})
                    sources = list_input.get('sources', [])
                    if sources:
                        source_guid = sources[0].get('source_guid')
                        print(f"  List input source: {source_guid}")
                        if source_guid == 'e7683176-0e64-40c9-ae31-e6c1c043bd15':
                            print(f"  [OK] Source matches Polar Array output param")
                        else:
                            print(f"  [ERROR] Source does NOT match Polar Array output param")
                    break
    
except FileNotFoundError:
    print("Could not load complete_component_graph.json")

print("\n" + "=" * 80)
print("SOLUTION:")
print("=" * 80)
print("Need to check:")
print("1. How resolve_input_value extracts 'Geometry' from Polar Array output")
print("2. Whether the output_params dictionary has the correct mapping")
print("3. Whether the List Item is correctly handling the nested list structure")

