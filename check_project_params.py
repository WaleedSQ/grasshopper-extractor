"""Check Project component parameters"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

project = next(c for c in graph['components'] if c['type_name'] == 'Project')

print(f"Project: {project['nickname']} ({project['guid'][:8]}...)")
print("\nParameters:")
for p in project['params']:
    print(f"  {p['type']}: {p['name']}")

