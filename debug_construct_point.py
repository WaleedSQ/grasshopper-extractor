"""Debug Construct Point component that outputs zeros"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

cp_guid = '9754db2b-c513-48b6-bbf7-0d06f53b3ce4'

# Find the component
cp = next((c for c in graph['components'] if c['guid'] == cp_guid), None)

if cp:
    print(f"Construct Point: {cp['nickname']} ({cp_guid[:8]}...)")
    print("="*80)
    
    for param in cp['params']:
        if param['type'] == 'input':
            print(f"\nInput: {param['name']}")
            print(f"  param_guid: {param['param_guid']}")
            print(f"  persistent_data: {param.get('persistent_data', [])}")
            print(f"  sources: {param.get('sources', [])}")
            
            if param['sources']:
                source_guid = param['sources'][0]
                
                # Find source component
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
                            print(f"    Evaluated: YES")
                            print(f"    Data: {output['item_count']} items")
                            if output['item_count'] > 0:
                                for path, items in list(output['branches'].items())[:1]:
                                    print(f"      {path}: {items}")
                        else:
                            print(f"    Output '{source_param['name']}' NOT IN RESULTS")
                    else:
                        print(f"    NOT EVALUATED")
                else:
                    print(f"  Source NOT FOUND (param {source_guid[:8]}...)")
    
    print("\n" + "="*80)
    print("Construct Point OUTPUT:")
    if cp_guid in results:
        output = results[cp_guid]['Point']
        print(f"  {output}")
    else:
        print("  NOT EVALUATED")
else:
    print(f"Component {cp_guid} NOT FOUND")

