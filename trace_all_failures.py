"""Trace all failing components to understand their inputs"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

comp_map = {c['guid']: c for c in graph['components']}

# Failing components from evaluation_summary.txt
failures = [
    ("Line: In Ray", "c7dba531-36f1-4a2d-8e0e-ed94b3873bba", "direction vector is None"),
    ("Line: Out Ray", "9a33273a-910e-439d-98d5-d225e29faebf", "direction vector is None"),
    ("Line: Between", "a518331f-8529-47db-bc2e-58ff8ef78e97", "direction vector is None"),
    ("Plane Normal", "326da981-351e-4794-9d60-77e8e87bd778", "plane dict missing z_axis key"),
    ("Plane Normal", "011398ea-ce1d-412a-afeb-fe91e8fac96c", "origin must be [x,y,z], got float"),
    ("Divide Length: DL", "1e2231f7-0d69-4908-8f56-55f13a5d4237", "curve must be dict"),
    ("Divide Length: DL", "c7b8773d-fa4e-4f3d-8ef8-fef5f21c8e80", "curve must be dict"),
]

print("=" * 80)
print("FAILING COMPONENTS INPUT TRACE")
print("=" * 80)

for nickname, guid, error in failures:
    comp = comp_map.get(guid)
    if not comp:
        print(f"\n{nickname} ({guid[:8]}...): NOT FOUND IN GRAPH")
        continue
    
    print(f"\n{comp['type_name']}: {comp['nickname']} ({guid[:8]}...)")
    print(f"  Error: {error}")
    print(f"  Inputs:")
    
    for param in comp['params']:
        if param['type'] == 'input':
            print(f"\n    {param['name']}:")
            
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
                    print(f"      Source: {source_comp['type_name']}: {source_comp['nickname']}")
                    
                    # Check if evaluated
                    if source_comp['guid'] in results:
                        result = results[source_comp['guid']]
                        output_name = source_param['name']
                        if output_name in result:
                            output_data = result[output_name]
                            print(f"      Output '{output_name}': {output_data['item_count']} items")
                            
                            if output_data['item_count'] > 0:
                                branches = output_data['branches']
                                for path, items in list(branches.items())[:1]:
                                    print(f"        {path}: {items[:3] if len(items) > 3 else items}")
                        else:
                            print(f"      Output '{output_name}': NOT IN RESULTS")
                    else:
                        print(f"      NOT EVALUATED")
                else:
                    print(f"      Source NOT FOUND (param_guid: {source_guid[:8]}...)")
            elif param['persistent_data']:
                print(f"      Persistent: {param['persistent_data']}")
            else:
                print(f"      NO DATA")

print("\n" + "=" * 80)

