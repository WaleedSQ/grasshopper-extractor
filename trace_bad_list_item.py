"""Trace the List Item outputting 0"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

li_guid = "3f21b46a-6839-4ce7-b107-eb3908e540ac"
li = next(c for c in graph['components'] if c['guid'] == li_guid)

print("List Item: LI (3f21b46a...)")
print("="*80)

for param in li['params']:
    print(f"\n{param['type'].upper()}: {param['name']}")
    if param['type'] == 'input':
        print(f"  persistent_data: {param.get('persistent_data', [])}")
        print(f"  sources: {param.get('sources', [])}")
        
        if param['sources']:
            source_guid = param['sources'][0]
            
            # Find source
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
                print(f"  Source: {source_comp['type_name']}: {source_comp['nickname']}")
                print(f"    Output param: {source_param['name']}")
                
                if source_comp['guid'] in results:
                    result = results[source_comp['guid']]
                    if source_param['name'] in result:
                        output = result[source_param['name']]
                        print(f"    Data: {output['item_count']} items")
                        if output['item_count'] > 0:
                            for path, items in list(output['branches'].items())[:1]:
                                print(f"      {path}: {items}")
                else:
                    print(f"    NOT EVALUATED")

print("\n" + "="*80)
print("List Item OUTPUT:")
if li_guid in results:
    output = results[li_guid]['Item']
    print(f"  {output}")
else:
    print("  NOT EVALUATED")

