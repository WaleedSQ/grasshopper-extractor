"""Find Divide Length with param ac0efd11"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

target_param = 'ac0efd11-aa24-46cf-8bcc-3ebfa4205ea1'

for comp in graph['components']:
    for param in comp['params']:
        if param['param_guid'] == target_param:
            print(f"Component: {comp['type_name']}: {comp['nickname']} ({comp['guid'][:8]}...)")
            print(f"  Parameter: {param['name']} ({param['type']})")
            
            # Check if evaluated
            if comp['guid'] in results:
                print(f"  Status: EVALUATED")
                if param['name'] in results[comp['guid']]:
                    output = results[comp['guid']][param['name']]
                    print(f"  Output: {output['item_count']} items")
            else:
                print(f"  Status: NOT EVALUATED")
                
                # Check inputs
                print(f"\n  Inputs:")
                for inp in comp['params']:
                    if inp['type'] == 'input':
                        print(f"    {inp['name']}: sources={inp.get('sources', [])}, persistent={inp.get('persistent_data', [])}")

