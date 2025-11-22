"""Trace List Item Index inputs"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

print("="*80)
print("LIST ITEM INDEX TRACING")
print("="*80)

# Find all List Item components
list_items = [c for c in graph['components'] if c['type_name'] == 'List Item']

print(f"\nFound {len(list_items)} List Item components\n")

for li_comp in list_items:
    print("-" * 80)
    print(f"List Item: {li_comp['nickname']} ({li_comp['guid'][:8]}...)")
    print("-" * 80)
    
    # Find Index input
    for param in li_comp['params']:
        if param['type'] == 'input' and param['name'] == 'Index':
            print(f"\n  Index Input:")
            print(f"    Parameter GUID: {param['param_guid']}")
            
            sources = param.get('sources', [])
            persistent = param.get('persistent_data', [])
            
            if sources:
                source_guid = sources[0]
                print(f"    Source GUID: {source_guid[:8]}...")
                
                # Find source component
                for c in graph['components']:
                    for p in c['params']:
                        if p['param_guid'] == source_guid:
                            print(f"    Source: {c['type_name']}: {c['nickname']}")
                            
                            # Check output
                            if c['guid'] in results:
                                comp_result = results[c['guid']]
                                if p['name'] in comp_result['outputs']:
                                    output_data = comp_result['outputs'][p['name']]
                                    print(f"    Output: {output_data['item_count']} items")
                                    
                                    for path, items in list(output_data['branches'].items())[:1]:
                                        if output_data['item_count'] <= 15:
                                            print(f"      Values: {items}")
                                        else:
                                            print(f"      First 10: {items[:10]}")
                            break
                    else:
                        continue
                    break
            elif persistent:
                print(f"    Persistent data: {persistent}")
            else:
                print(f"    No source or persistent data!")
    
    # Check this List Item's output
    if li_comp['guid'] in results:
        comp_result = results[li_comp['guid']]
        print(f"\n  List Item Output:")
        for output_name, output_data in comp_result['outputs'].items():
            print(f"    {output_name}: {output_data['item_count']} items")

print("\n" + "="*80)

