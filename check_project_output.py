"""Check Project component outputs"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

project_guid = '9cd053c9-b4f3-4b18-a82e-ebff73b0e6f6'

if project_guid in results:
    project_result = results[project_guid]
    print(f"Project outputs: {list(project_result.keys())}")
    for name, data in project_result.items():
        print(f"  {name}: {data['item_count']} items")
else:
    print("Project NOT in results")

# Check what outputs Project SHOULD have
project_comp = next((c for c in graph['components'] if c['guid'] == project_guid), None)
if project_comp:
    print(f"\nProject component parameters:")
    for p in project_comp['params']:
        if p['type'] == 'output':
            print(f"  OUTPUT: {p['name']}")

