"""Trace the final 2 failing components"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

# Divide Length: DL at step 52 - guid: c7b8773d-fa4e-4f3d-8ef8-fef5f21c8e80
# Line: Between at step 54 - guid: a518331f-8529-47db-bc2e-58ff8ef78e97

failures = {
    "Divide Length: DL": "c7b8773d-fa4e-4f3d-8ef8-fef5f21c8e80",
    "Line: Between": "a518331f-8529-47db-bc2e-58ff8ef78e97"
}

for name, guid in failures.items():
    comp = next((c for c in graph['components'] if c['guid'] == guid), None)
    if not comp:
        print(f"{name}: NOT FOUND")
        continue
    
    print(f"\n{'='*80}")
    print(f"{name} ({guid[:8]}...)")
    print(f"{'='*80}")
    
    for param in comp['params']:
        if param['type'] == 'input':
            print(f"\n  Input: {param['name']}")
            
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
                    print(f"    Source: {source_comp['type_name']}: {source_comp['nickname']} ({source_comp['guid'][:8]}...)")
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
                            print(f"    Output '{source_param['name']}' NOT IN RESULTS")
                    else:
                        print(f"    Source NOT EVALUATED")
            elif param['persistent_data']:
                print(f"    Persistent: {param['persistent_data']}")
            else:
                print(f"    NO DATA")

print("\n" + "="*80)

