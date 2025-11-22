"""Debug why Angle outputs 1 value instead of 10"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

angle_guid = "0d695e6b-3696-4337-bc80-d14104f8a59e"

# Find Angle component
angle_comp = next((c for c in graph['components'] if c['guid'] == angle_guid), None)

if angle_comp:
    print("="*80)
    print("ANGLE COMPONENT INPUT ANALYSIS")
    print("="*80)
    
    for param in angle_comp['params']:
        if param['type'] == 'input':
            print(f"\n{param['name']}:")
            print(f"  Parameter GUID: {param['param_guid']}")
            
            sources = param.get('sources', [])
            if sources:
                source_guid = sources[0]
                print(f"  Source param GUID: {source_guid[:8]}...")
                
                # Find source component
                for c in graph['components']:
                    for p in c['params']:
                        if p['param_guid'] == source_guid:
                            print(f"  Source: {c['type_name']}: {c['nickname']} ({c['guid'][:8]}...)")
                            
                            # Check output
                            if c['guid'] in results:
                                comp_result = results[c['guid']]
                                if p['name'] in comp_result['outputs']:
                                    output_data = comp_result['outputs'][p['name']]
                                    print(f"  Output: {output_data['item_count']} items in {output_data['branch_count']} branch(es)")
                                    
                                    if output_data['item_count'] > 0:
                                        for path, items in list(output_data['branches'].items())[:1]:
                                            print(f"    Path {path}:")
                                            if output_data['item_count'] <= 15:
                                                for i, item in enumerate(items):
                                                    if isinstance(item, dict):
                                                        print(f"      [{i}]: {type(item).__name__} with keys: {list(item.keys())[:5]}")
                                                    else:
                                                        print(f"      [{i}]: {item}")
                                            else:
                                                print(f"      (showing first 3 of {len(items)})")
                                                for i in range(min(3, len(items))):
                                                    item = items[i]
                                                    if isinstance(item, dict):
                                                        print(f"      [{i}]: {type(item).__name__} with keys: {list(item.keys())[:5]}")
                                                    else:
                                                        print(f"      [{i}]: {item}")
                            break
                    else:
                        continue
                    break
    
    # Check Angle output
    print("\n" + "="*80)
    print("ANGLE OUTPUT:")
    print("="*80)
    
    if angle_guid in results:
        angle_result = results[angle_guid]
        for output_name, output_data in angle_result['outputs'].items():
            print(f"\n{output_name}: {output_data['item_count']} items in {output_data['branch_count']} branch(es)")
            if output_data['item_count'] > 0:
                for path, items in list(output_data['branches'].items())[:1]:
                    print(f"  Path {path}:")
                    if len(items) <= 12:
                        for i, item in enumerate(items):
                            print(f"    [{i}]: {item}")
                    else:
                        print(f"    (showing first 5 of {len(items)})")
                        for i in range(5):
                            print(f"    [{i}]: {items[i]}")

print("\n" + "="*80)
print("EXPECTED: 10 items with values matching screenshot")
print("Screenshot first value: 43.701519 degrees = 0.7627 radians")
print("="*80)

