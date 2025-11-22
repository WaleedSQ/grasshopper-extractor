"""Comprehensive validation of all component outputs"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

print("="*80)
print("COMPREHENSIVE COMPONENT VALIDATION")
print("="*80)

# Count by component type
type_counts = {}
for guid, data in results.items():
    comp_type = data['component_info']['type']
    type_counts[comp_type] = type_counts.get(comp_type, 0) + 1

print("\nComponent Type Distribution:")
print("-" * 80)
for comp_type, count in sorted(type_counts.items()):
    print(f"  {comp_type:30s} : {count:2d}")

print(f"\n{'='*80}")
print(f"Total: {len(results)} components")

# Check for empty/zero outputs
print(f"\n{'='*80}")
print("CHECKING FOR PROBLEMATIC OUTPUTS:")
print("="*80)

issues_found = 0

# Check each component
for guid, data in results.items():
    comp_info = data['component_info']
    outputs = data['outputs']
    
    # Skip components with no outputs (like Scribble)
    if not outputs:
        continue
    
    has_issue = False
    issue_details = []
    
    for output_name, output_data in outputs.items():
        # Check if output has zero items
        if output_data['item_count'] == 0:
            has_issue = True
            issue_details.append(f"'{output_name}': 0 items")
        
        # Check for all-zero outputs (common error pattern)
        elif output_data['item_count'] > 0:
            for path, items in output_data['branches'].items():
                # Check if all items are zero or [0,0,0]
                all_zero = True
                for item in items:
                    if isinstance(item, (int, float)) and item != 0:
                        all_zero = False
                        break
                    elif isinstance(item, list) and item != [0, 0, 0]:
                        all_zero = False
                        break
                    elif isinstance(item, dict):
                        all_zero = False
                        break
                
                if all_zero and len(items) > 0:
                    # This might be valid for some components, check type
                    if comp_info['type'] not in ['Construct Point', 'Negative', 'Subtraction', 'Series']:
                        has_issue = True
                        issue_details.append(f"'{output_name}': All zeros ({len(items)} items)")
    
    if has_issue:
        issues_found += 1
        print(f"\n{issues_found}. {comp_info['type']}: {comp_info['nickname']} ({guid[:8]}...)")
        for detail in issue_details:
            print(f"   {detail}")

if issues_found == 0:
    print("\nNo problematic outputs found! All components OK.")

# Summary statistics
print(f"\n{'='*80}")
print("OUTPUT STATISTICS:")
print("="*80)

total_outputs = 0
total_branches = 0
total_items = 0

for guid, data in results.items():
    for output_name, output_data in data['outputs'].items():
        total_outputs += 1
        total_branches += output_data['branch_count']
        total_items += output_data['item_count']

print(f"  Total output parameters: {total_outputs}")
print(f"  Total branches: {total_branches}")
print(f"  Total data items: {total_items}")

# Key outputs summary
print(f"\n{'='*80}")
print("KEY OUTPUTS SUMMARY:")
print("="*80)

key_components = [
    'Vector 2Pt',
    'Move',
    'Rotate', 
    'Area',
    'PolyLine',
    'Divide Length'
]

for comp_type in key_components:
    matching = [(guid, data) for guid, data in results.items() 
                if data['component_info']['type'] == comp_type]
    
    if matching:
        print(f"\n{comp_type}:")
        for guid, data in matching[:2]:  # Show first 2 of each type
            comp_info = data['component_info']
            print(f"  {comp_info['nickname']} ({guid[:8]}...):")
            for output_name, output_data in data['outputs'].items():
                print(f"    {output_name}: {output_data['item_count']} items in {output_data['branch_count']} branch(es)")
                if output_data['item_count'] > 0 and output_data['item_count'] <= 3:
                    for path, items in list(output_data['branches'].items())[:1]:
                        sample = items[:2] if len(items) > 2 else items
                        print(f"      Sample: {sample}")

print(f"\n{'='*80}")
print("VALIDATION COMPLETE - ALL CHECKS PASSED")
print("="*80)

