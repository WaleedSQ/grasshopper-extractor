"""Temporary script to parse refactored-sun.ghx"""
from parse_refactored_ghx import parse_ghx
import json

components, wires = parse_ghx('refactored-sun.ghx')
graph = {'components': components, 'wires': wires}
with open('ghx_graph.json', 'w') as f:
    json.dump(graph, f, indent=2)
print(f'Parsed {len(components)} components, {len(wires)} wires')

