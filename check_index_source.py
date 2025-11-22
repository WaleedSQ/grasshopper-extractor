"""Check what provides the Index to List Item"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

# Find the source
source_guid = '537142d8-e672-4d12-8254-46dbe1e3c7ef'

# Find which component has this as an output parameter
source_comp = None
source_param = None
for c in graph['components']:
    for p in c['params']:
        if p['param_guid'] == source_guid:
            source_comp = c
            source_param = p
            break
    if source_comp:
        break

if source_comp:
    print(f"Index source: {source_comp['type_name']}: {source_comp['nickname']}")
    print(f"  Output param: {source_param['name']}")
    
    if source_comp['guid'] in results:
        result = results[source_comp['guid']]
        if source_param['name'] in result:
            output = result[source_param['name']]
            print(f"  Output data: {output}")
        else:
            print(f"  Output '{source_param['name']}' not in results")
    else:
        print(f"  Component not evaluated")
else:
    print(f"Source param {source_guid} not found")

