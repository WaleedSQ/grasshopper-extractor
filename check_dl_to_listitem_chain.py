"""Check the complete chain from DL to List Item"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

# List Items feeding Line "Between"
list_items = [
    "ed4878fc-7b79-46d9-a4b1-7637f35de976",  # Start Point
    "3f21b46a-6839-4ce7-b107-eb3908e540ac"   # End Point
]

print("="*80)
print("TRACING DL -> LIST ITEM CONNECTION")
print("="*80)

for li_guid in list_items:
    li_comp = next((c for c in graph['components'] if c['guid'] == li_guid), None)
    
    print(f"\n{'='*80}")
    print(f"List Item: {li_comp['nickname']}")
    print(f"GUID: {li_guid[:8]}...")
    print(f"Position: ({li_comp['position']['x']}, {li_comp['position']['y']})")
    
    # Find what feeds its List input
    for param in li_comp['params']:
        if param['name'] == 'List' and param['type'] == 'input':
            print(f"\n  List input:")
            sources = param.get('sources', [])
            print(f"    Source param GUID: {sources[0] if sources else 'None'}")
            
            if sources:
                # Find the component that owns this parameter
                source_param_guid = sources[0]
                
                for comp in graph['components']:
                    for p in comp['params']:
                        if p['param_guid'] == source_param_guid:
                            print(f"\n    FROM: {comp['type_name']}: {comp['nickname']}")
                            print(f"    Component GUID: {comp['guid'][:8]}...")
                            print(f"    Output param: {p['name']}")
                            print(f"    Position: ({comp['position']['x']}, {comp['position']['y']})")
                            
                            # Check for Graft/Flatten settings
                            if 'graft' in p or 'flatten' in p:
                                print(f"    Graft: {p.get('graft', 'N/A')}")
                                print(f"    Flatten: {p.get('flatten', 'N/A')}")
                            
                            # If it's a DL, check its input curve
                            if comp['type_name'] == 'Divide Length':
                                print(f"\n    DL inputs:")
                                for dl_param in comp['params']:
                                    if dl_param['type'] == 'input':
                                        print(f"      {dl_param['name']}: ", end='')
                                        if dl_param.get('sources'):
                                            # Find source
                                            src_guid = dl_param['sources'][0]
                                            for c2 in graph['components']:
                                                for p2 in c2['params']:
                                                    if p2['param_guid'] == src_guid:
                                                        print(f"{c2['type_name']}: {c2['nickname']}")
                                                        break
                                        else:
                                            print(f"Persistent: {dl_param.get('persistent_data', [])}")
                            
                            break

print("\n" + "="*80)
print("CHECKING FOR PARTITION/SPLIT COMPONENTS")
print("="*80)

partition_components = [c for c in graph['components'] if 'Partition' in c['type_name'] or 'Split' in c['type_name']]
print(f"\nFound {len(partition_components)} Partition/Split components:")
for pc in partition_components:
    print(f"  - {pc['type_name']}: {pc['nickname']} ({pc['guid'][:8]}...)")
    print(f"    Position: ({pc['position']['x']}, {pc['position']['y']})")

