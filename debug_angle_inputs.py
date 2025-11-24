"""Debug what inputs the Angle component is receiving"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

# Find Angle component
angle_comp = next((c for c in graph['components'] if c['type_name'] == 'Angle'), None)

print("="*80)
print("ANGLE COMPONENT INPUTS")
print("="*80)

print(f"\nAngle component: {angle_comp['nickname']}")
print(f"GUID: {angle_comp['guid'][:8]}...")

# Check each input parameter
for param in angle_comp['params']:
    if param['type'] == 'input':
        print(f"\n{param['name']}:")
        print(f"  Mapping: {param.get('mapping', 0)}")
        
        if param.get('sources'):
            src_param_guid = param['sources'][0]
            
            # Find source component
            for comp in graph['components']:
                for p in comp['params']:
                    if p['param_guid'] == src_param_guid:
                        print(f"  FROM: {comp['type_name']}: {comp['nickname']}")
                        print(f"  Output param: {p['name']}")
                        
                        # Check actual values
                        if comp['guid'] in results:
                            output_data = results[comp['guid']]['outputs'][p['name']]
                            print(f"  Output structure: {output_data['branch_count']} branches, {output_data['item_count']} items")
                            
                            # Show first 3 values from first branch
                            first_branch = list(output_data['branches'].values())[0]
                            print(f"  First branch sample (first 3 items): {first_branch[:3]}")
                        break

# Now check Angle output
angle_guid = angle_comp['guid']
if angle_guid in results:
    angle_data = results[angle_guid]['outputs']['Angle']
    print(f"\n{'='*80}")
    print("ANGLE OUTPUT")
    print(f"{'='*80}")
    print(f"Branches: {angle_data['branch_count']}, Items: {angle_data['item_count']}")
    
    # Show first 3 branches
    for i, (path, items) in enumerate(list(angle_data['branches'].items())[:3]):
        print(f"  Branch {path}: {items[0]:.6f} radians = {items[0] * 57.2958:.2f} degrees")

