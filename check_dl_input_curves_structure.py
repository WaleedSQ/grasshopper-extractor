"""Check if DL input curves provide 10 branches"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

# Find the two DL components
dl_guids = [
    "c7b8773d-e1e0-4c31-9b7c-b8b54f9e40e0",  # Feeds List Item for Start Point
    "1e2231f7-0d69-4908-8f56-55f13a5d4237"   # Feeds List Item for End Point
]

print("="*80)
print("CHECKING DL INPUT CURVES STRUCTURE")
print("="*80)

for dl_guid in dl_guids:
    dl_comp = next((c for c in graph['components'] if c['guid'] == dl_guid), None)
    
    print(f"\n{'='*80}")
    print(f"DL: {dl_comp['nickname']}")
    print(f"Position: ({dl_comp['position']['x']}, {dl_comp['position']['y']})")
    
    # Find its Curve input
    for param in dl_comp['params']:
        if param['name'] == 'Curve' and param['type'] == 'input':
            sources = param.get('sources', [])
            
            if sources:
                source_param_guid = sources[0]
                
                # Find the component providing this curve
                for comp in graph['components']:
                    for p in comp['params']:
                        if p['param_guid'] == source_param_guid:
                            print(f"\n  Input Curve FROM: {comp['type_name']}: {comp['nickname']}")
                            print(f"  Component GUID: {comp['guid'][:8]}...")
                            
                            # Check this component's output in results
                            if comp['guid'] in results:
                                comp_results = results[comp['guid']]
                                
                                for output_name, output_data in comp_results['outputs'].items():
                                    if output_name == p['name']:
                                        print(f"\n  Output '{output_name}':")
                                        print(f"    Total items: {output_data['item_count']}")
                                        print(f"    Branches: {output_data['branch_count']}")
                                        
                                        # Show branch structure
                                        print(f"\n    Branch structure:")
                                        for path, items in list(output_data['branches'].items())[:5]:
                                            print(f"      Path {path}: {len(items)} items")
                                        
                                        if output_data['branch_count'] > 5:
                                            print(f"      ... ({output_data['branch_count']} branches total)")
                                        
                                        # Check if it's 10 branches
                                        if output_data['branch_count'] == 10:
                                            print(f"\n    [OK] HAS 10 BRANCHES! This should create 10-branched DL output!")
                                        elif output_data['branch_count'] == 1:
                                            print(f"\n    [ISSUE] Only 1 branch - this is why DL outputs are flat!")
                            
                            break

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("If input curves have 10 branches, DL should output 10 branches.")
print("If input curves have 1 branch, DL outputs 1 flat branch (current issue!).")

