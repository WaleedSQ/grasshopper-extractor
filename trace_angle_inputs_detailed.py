"""Trace Vector A and Vector B sources in detail"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

# List Item (Vector A source)
list_item_guid = "157c48b5-f9eb-46be-ad3c-e8c16ba7f8dd"

# Line Between (Vector B source)
line_guid = "a518331f-8529-47db-bc2e-58ff8ef78e97"

print("="*80)
print("TRACING ANGLE INPUTS")
print("="*80)

for guid, label in [(list_item_guid, "List Item (Vector A)"), (line_guid, "Line (Vector B)")]:
    comp = next((c for c in graph['components'] if c['guid'] == guid), None)
    
    if comp:
        print(f"\n{label}:")
        print(f"  Type: {comp['type_name']}")
        print(f"  Nickname: {comp['nickname']}")
        print("-" * 80)
        
        # Check inputs
        print("\n  Inputs:")
        for param in comp['params']:
            if param['type'] == 'input':
                print(f"    {param['name']}:")
                
                sources = param.get('sources', [])
                if sources:
                    source_guid = sources[0]
                    
                    # Find source component
                    for c in graph['components']:
                        for p in c['params']:
                            if p['param_guid'] == source_guid:
                                print(f"      Source: {c['type_name']}: {c['nickname']}")
                                
                                # Check output
                                if c['guid'] in results:
                                    comp_result = results[c['guid']]
                                    if p['name'] in comp_result['outputs']:
                                        output_data = comp_result['outputs'][p['name']]
                                        print(f"      Output: {output_data['item_count']} items")
                                        
                                        if output_data['item_count'] <= 10:
                                            for path, items in list(output_data['branches'].items())[:1]:
                                                for i, item in enumerate(items[:3]):
                                                    if isinstance(item, list) and len(item) == 3:
                                                        print(f"        [{i}]: [{item[0]:.4f}, {item[1]:.4f}, {item[2]:.4f}]")
                                                    elif isinstance(item, dict):
                                                        print(f"        [{i}]: {type(item).__name__}")
                                                    else:
                                                        print(f"        [{i}]: {item}")
                                break
                        else:
                            continue
                        break
                else:
                    persistent = param.get('persistent_data', [])
                    if persistent:
                        print(f"      Persistent: {persistent}")
        
        # Check output
        print("\n  Outputs:")
        if guid in results:
            comp_result = results[guid]
            for output_name, output_data in comp_result['outputs'].items():
                print(f"    {output_name}: {output_data['item_count']} items")
                
                if output_data['item_count'] <= 10 and output_data['item_count'] > 0:
                    for path, items in list(output_data['branches'].items())[:1]:
                        for i, item in enumerate(items[:3]):
                            if isinstance(item, list) and len(item) == 3:
                                print(f"      [{i}]: [{item[0]:.4f}, {item[1]:.4f}, {item[2]:.4f}]")
                            elif isinstance(item, dict):
                                if 'z_axis' in item:
                                    print(f"      [{i}]: Plane with z_axis: {item['z_axis']}")
                                elif 'start' in item:
                                    print(f"      [{i}]: Line from {item['start']} to {item['end']}")
                                else:
                                    print(f"      [{i}]: {type(item).__name__} with keys: {list(item.keys())[:5]}")
                            else:
                                print(f"      [{i}]: {item}")

print("\n" + "="*80)
print("EXPECTED: Both should produce 10 DIFFERENT items")
print("="*80)

