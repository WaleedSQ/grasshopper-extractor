"""
Debug why the Y coordinate in Targets Move output doesn't match the screenshot.
Screenshot shows Y values around -22.846834, but we're getting -31.846834.
"""
import json

# Load evaluation results
with open('evaluation_results.md', 'r') as f:
    content = f.read()

print("=" * 80)
print("DEBUGGING TARGETS Y COORDINATE")
print("=" * 80)

# Expected from screenshot: Y = -22.846834 (approximately)
# Actual from evaluation: Y = -31.846834162334087
# Difference: ~9.0

print("\n1. FIRST MOVE 'Targets' OUTPUT (2587762a...):")
print("   Should be: [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]")
if '2587762a' in content:
    print("   [FOUND] First Move Targets output exists")

print("\n2. POLAR ARRAY OUTPUT (e7683176...):")
print("   Should be: [[[0.0, -4.5, 4.0], ...], [[rotated copy], ...], ...]")
if 'e7683176' in content:
    print("   [FOUND] Polar Array output exists")
    # Extract the actual value
    lines = content.split('\n')
    for line in lines:
        if 'e7683176' in line and 'Polar Array' in line:
            print(f"   Line: {line[:150]}...")

print("\n3. LIST ITEM OUTPUT (f03b9ab7...):")
print("   Should extract index 0 from Polar Array")
print("   Expected: [[0.0, -4.5, 4.0], [0.0, -4.111111111111111, 4.0], ...]")
if 'f03b9ab7' in content:
    print("   [FOUND] List Item output exists")
    lines = content.split('\n')
    for line in lines:
        if 'f03b9ab7' in line and 'List Item' in line:
            print(f"   Line: {line[:150]}...")

print("\n4. AMPLITUDE OUTPUT (d0668a07...):")
print("   Should be: [11.327429598006665, -27.346834162334087, 0.0]")
if 'd0668a07' in content:
    print("   [FOUND] Amplitude output exists")

print("\n5. SECOND MOVE 'Targets' OUTPUT (b38a38f1... / 80fd9f48...):")
print("   Expected calculation:")
print("   [0.0, -4.5, 4.0] + [11.327429598006665, -27.346834162334087, 0.0]")
print("   = [11.327429598006665, -31.846834162334087, 4.0]")
print("   But screenshot shows Y approximately -22.846834")
print("   Difference: -22.846834 - (-31.846834) = 9.0")
if 'b38a38f1' in content or '80fd9f48' in content:
    print("   [FOUND] Second Move Targets output exists")
    lines = content.split('\n')
    for line in lines:
        if ('b38a38f1' in line or '80fd9f48' in line) and 'Targets' in line:
            print(f"   Line: {line[:150]}...")

print("\n" + "=" * 80)
print("HYPOTHESIS:")
print("=" * 80)
print("The Y coordinate difference of ~9.0 suggests:")
print("1. The List Item might be extracting the wrong index")
print("2. The Polar Array might be outputting a different structure")
print("3. The first Move 'Targets' might have a different Y value than expected")
print("\nLet's check the actual component graph to see the data flow...")

# Load the graph
try:
    with open('complete_component_graph.json', 'r') as f:
        graph_data = json.load(f)
    
    components = graph_data.get('components', {})
    
    # Find Polar Array component
    polar_array_comp = None
    for comp_id, comp in components.items():
        if isinstance(comp, dict):
            obj = comp.get('obj', {})
            if obj.get('instance_guid') == 'b4a4862a-3bba-4868-943f-cf86bdc99cf3':
                polar_array_comp = comp
                print(f"\n[OK] Found Polar Array component: {comp_id[:8]}...")
                print(f"  Instance GUID: {obj.get('instance_guid')}")
                # Check Geometry input source
                inputs = comp.get('inputs', {})
                geom_input = inputs.get('param_input_0', {})
                sources = geom_input.get('sources', [])
                if sources:
                    source_guid = sources[0].get('source_guid')
                    print(f"  Geometry input source: {source_guid}")
                    if source_guid == '2587762a-e6a9-4ba9-8724-f347436a5953':
                        print(f"  [OK] Source is first Move 'Targets' output")
    
    # Find List Item component
    list_item_comp = None
    for comp_id, comp in components.items():
        if isinstance(comp, dict):
            obj = comp.get('obj', {})
            if obj.get('instance_guid') == 'f03b9ab7-3e3f-417e-97be-813257e5f7de':
                list_item_comp = comp
                print(f"\n[OK] Found List Item component: {comp_id[:8]}...")
                print(f"  Instance GUID: {obj.get('instance_guid')}")
                # Check List input source
                inputs = comp.get('inputs', {})
                list_input = inputs.get('param_input_0', {})
                sources = list_input.get('sources', [])
                if sources:
                    source_guid = sources[0].get('source_guid')
                    print(f"  List input source: {source_guid}")
                    if source_guid == 'e7683176-0e64-40c9-ae31-e6c1c043bd15':
                        print(f"  [OK] Source is Polar Array Geometry output")
                # Check Index input
                index_input = inputs.get('param_input_1', {})
                index_sources = index_input.get('sources', [])
                persistent_values = index_input.get('persistent_values', [])
                print(f"  Index sources: {len(index_sources)}")
                print(f"  Index persistent values: {persistent_values}")
                if persistent_values:
                    print(f"  Index value: {persistent_values[0]}")
    
except FileNotFoundError:
    print("Could not load complete_component_graph.json")

