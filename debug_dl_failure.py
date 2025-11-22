"""Debug which DL failed and why"""
import json

# Load results
with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

# Load graph
with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

# Find both DL components
dl_guids = [
    "1e2231f7-0d69-4908-8f56-55f13a5d4237",  # DL at (12167, 2879) - From Project
    "c7b8773d-e1e0-4c31-9b7c-b8b54f9e40e0"   # DL at (12167, 2800) - From Line
]

print("="*80)
print("DL COMPONENTS ANALYSIS")
print("="*80)

for guid in dl_guids:
    dl = next((c for c in graph['components'] if c['guid'] == guid), None)
    
    print(f"\nDL: {dl['nickname']}")
    print(f"GUID: {guid[:8]}...")
    print(f"Position: ({dl['position']['x']}, {dl['position']['y']})")
    
    # Check if it was evaluated
    if guid in results:
        data = results[guid]
        print(f"Status: EVALUATED")
        print(f"  Points output: {data['outputs']['Points']['branch_count']} branches, {data['outputs']['Points']['item_count']} items")
    else:
        print(f"Status: FAILED (not in results)")
    
    # Check input source
    curve_param = next((p for p in dl['params'] if p['name'] == 'Curve' and p['type'] == 'input'), None)
    if curve_param and curve_param.get('sources'):
        src_param_guid = curve_param['sources'][0]
        
        # Find source component
        for comp in graph['components']:
            for param in comp['params']:
                if param['param_guid'] == src_param_guid:
                    print(f"\n  Curve Input FROM:")
                    print(f"    Component: {comp['type_name']}: {comp['nickname']}")
                    print(f"    Output param: {param['name']}")
                    print(f"    Mapping: {param.get('mapping', 0)}")
                    
                    # Check source's output in results
                    if comp['guid'] in results:
                        source_data = results[comp['guid']]
                        if param['name'] in source_data['outputs']:
                            output = source_data['outputs'][param['name']]
                            print(f"    Output structure: {output['branch_count']} branches, {output['item_count']} items")
                    break

