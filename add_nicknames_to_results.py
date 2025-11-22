"""Add component nicknames and metadata to evaluation results"""
import json

# Load graph to get component info
with open('rotatingslats_graph.json', 'r') as f:
    graph = json.load(f)

# Load evaluation results
with open('rotatingslats_evaluation_results.json', 'r') as f:
    results = json.load(f)

# Create component map
comp_map = {c['guid']: c for c in graph['components']}

# Create new structure with metadata
enhanced_results = {}

for guid, outputs in results.items():
    comp = comp_map.get(guid)
    
    if comp:
        enhanced_results[guid] = {
            'component_info': {
                'guid': guid,
                'type': comp['type_name'],
                'nickname': comp['nickname'],
                'position': comp['position']
            },
            'outputs': outputs
        }
    else:
        # Component not found, just include outputs
        enhanced_results[guid] = {
            'component_info': {
                'guid': guid,
                'type': 'Unknown',
                'nickname': 'Unknown'
            },
            'outputs': outputs
        }

# Save enhanced results
with open('rotatingslats_evaluation_results.json', 'w') as f:
    json.dump(enhanced_results, f, indent=2)

print(f"Enhanced {len(enhanced_results)} component results with nicknames")
print("\nExample entries:")
for i, (guid, data) in enumerate(list(enhanced_results.items())[:3]):
    info = data['component_info']
    print(f"\n{i+1}. {info['type']}: {info['nickname']} ({guid[:8]}...)")
    outputs = data['outputs']
    for output_name, output_data in outputs.items():
        print(f"   Output '{output_name}': {output_data['item_count']} items")

