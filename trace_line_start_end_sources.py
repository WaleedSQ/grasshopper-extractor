"""Trace what feeds the List Item components that feed the Line"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

# Line component
line_guid = "a518331f-8529-47db-bc2e-58ff8ef78e97"

line_comp = next((c for c in graph['components'] if c['guid'] == line_guid), None)

if line_comp:
    print("="*80)
    print("LINE COMPONENT: Between")
    print("="*80)
    
    # Find Start Point and End Point inputs
    for param in line_comp['params']:
        if param['type'] == 'input' and param['name'] in ['Start Point', 'End Point']:
            print(f"\n{param['name']}:")
            
            sources = param.get('sources', [])
            if sources:
                source_guid = sources[0]
                
                # Find the List Item that provides this
                for c in graph['components']:
                    for p in c['params']:
                        if p['param_guid'] == source_guid:
                            print(f"  Source: {c['type_name']}: {c['nickname']} ({c['guid'][:8]}...)")
                            
                            # Now trace this List Item's inputs
                            print(f"\n  This List Item's inputs:")
                            for li_param in c['params']:
                                if li_param['type'] == 'input':
                                    print(f"    {li_param['name']}:")
                                    
                                    li_sources = li_param.get('sources', [])
                                    li_persistent = li_param.get('persistent_data', [])
                                    
                                    if li_sources:
                                        li_source_guid = li_sources[0]
                                        
                                        # Find source of this List Item input
                                        for c2 in graph['components']:
                                            for p2 in c2['params']:
                                                if p2['param_guid'] == li_source_guid:
                                                    print(f"      Source: {c2['type_name']}: {c2['nickname']} ({c2['guid'][:8]}...)")
                                                    
                                                    # Check output count
                                                    if c2['guid'] in results:
                                                        comp_result = results[c2['guid']]
                                                        if p2['name'] in comp_result['outputs']:
                                                            output_data = comp_result['outputs'][p2['name']]
                                                            print(f"      Output: {output_data['item_count']} items")
                                                            
                                                            # Sample a few items
                                                            if output_data['item_count'] <= 10:
                                                                for path, items in list(output_data['branches'].items())[:1]:
                                                                    print(f"        {path}: (showing first 3)")
                                                                    for i, item in enumerate(items[:3]):
                                                                        if isinstance(item, list) and len(item) == 3:
                                                                            print(f"          [{i}]: [{item[0]:.4f}, {item[1]:.4f}, {item[2]:.4f}]")
                                                                        else:
                                                                            print(f"          [{i}]: {item}")
                                                    break
                                            else:
                                                continue
                                            break
                                    elif li_persistent:
                                        print(f"      Persistent: {li_persistent}")
                            
                            # Check this List Item's output
                            if c['guid'] in results:
                                comp_result = results[c['guid']]
                                for output_name, output_data in comp_result['outputs'].items():
                                    print(f"\n  List Item Output ({output_name}): {output_data['item_count']} items")
                                    if output_data['item_count'] <= 5:
                                        for path, items in list(output_data['branches'].items())[:1]:
                                            for i, item in enumerate(items):
                                                if isinstance(item, list) and len(item) == 3:
                                                    print(f"    [{i}]: [{item[0]:.4f}, {item[1]:.4f}, {item[2]:.4f}]")
                            break
                    else:
                        continue
                    break

print("\n" + "="*80)

