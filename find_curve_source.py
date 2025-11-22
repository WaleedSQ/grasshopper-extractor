"""Find source of Divide Length Curve input"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

source_param_guid = 'aeedb946-4c19-44d8-8e7d-77f9dd230432'

for comp in graph['components']:
    for param in comp['params']:
        if param['param_guid'] == source_param_guid:
            print(f"Source: {comp['type_name']}: {comp['nickname']} ({comp['guid'][:8]}...)")
            print(f"  Output param: {param['name']}")
            print(f"  Evaluated: {comp['guid'] in results}")
            
            if comp['guid'] in results:
                if param['name'] in results[comp['guid']]:
                    output = results[comp['guid']][param['name']]
                    print(f"  Output data: {output['item_count']} items")
                    if output['item_count'] > 0:
                        for path, items in list(output['branches'].items())[:1]:
                            print(f"    {path}: {items}")
                else:
                    print(f"  Output '{param['name']}' not in results")
            break

