"""Check List Item index parameter"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

li = next(c for c in graph['components'] if c['guid'] == '9ff79870-05d0-483d-87be-b3641d71c6fc')

print("List Item parameters:")
for p in li['params']:
    print(f"  {p['type']}: {p['name']}")
    print(f"    persistent_data: {p.get('persistent_data', [])}")
    print(f"    sources: {p.get('sources', [])}")

