"""Check Divide Length Points output structure"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

# Find Divide Length components
dl_components = [c for c in graph['components'] if c['type_name'] == 'Divide Length']

print("="*80)
print("DIVIDE LENGTH (DL) COMPONENTS")
print("="*80)

for dl in dl_components:
    dl_guid = dl['guid']
    
    print(f"\n{dl['nickname']} ({dl_guid[:8]}...):")
    print(f"Position: ({dl['position']['x']}, {dl['position']['y']})")
    
    if dl_guid in results:
        data = results[dl_guid]
        
        for output_name, output_data in data['outputs'].items():
            if output_name == 'Points':
                print(f"\n  Points output:")
                print(f"    Total items: {output_data['item_count']}")
                print(f"    Branches: {output_data['branch_count']}")
                
                # Check branch structure
                for path, items in output_data['branches'].items():
                    print(f"\n    Path {path}:")
                    print(f"      Items in this branch: {len(items)}")
                    
                    # Check if items are grouped
                    print(f"      First 3 points:")
                    for i in range(min(3, len(items))):
                        pt = items[i]
                        if isinstance(pt, list) and len(pt) == 3:
                            print(f"        [{i}]: ({pt[0]:.4f}, {pt[1]:.4f}, {pt[2]:.4f})")
                    
                    print(f"      Last 3 points:")
                    for i in range(max(0, len(items)-3), len(items)):
                        pt = items[i]
                        if isinstance(pt, list) and len(pt) == 3:
                            print(f"        [{i}]: ({pt[0]:.4f}, {pt[1]:.4f}, {pt[2]:.4f})")
                    
                    # Check if total items is divisible by 10
                    if len(items) % 10 == 0:
                        points_per_slat = len(items) // 10
                        print(f"\n      ANALYSIS: {len(items)} points ÷ 10 slats = {points_per_slat} points per slat")

print("\n" + "="*80)
print("KEY QUESTION: Are DL points structured as 10 separate branches?")
print("Or as one branch with all points that should be split?")
print("="*80)

