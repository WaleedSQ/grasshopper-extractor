"""Compare the two Plane Normal components"""
import json

with open('rotatingslats_graph.json') as f:
    graph = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

pn1_guid = "326da981-351e-4794-9d60-77e8e87bd778"  # At (12043, 2991)
pn2_guid = "011398ea-ce1d-412a-afeb-fe91e8fac96c"  # At (12184, 3075)

for pn_guid in [pn1_guid, pn2_guid]:
    pn = next((c for c in graph['components'] if c['guid'] == pn_guid), None)
    print(f"\nPlane Normal: {pn['nickname']}")
    print(f"  Position: ({pn['position']['x']}, {pn['position']['y']})")
    print(f"  GUID: {pn_guid[:16]}...")
    
    if pn_guid in results:
        planes = list(results[pn_guid]['outputs']['Plane']['branches'].values())[0]
        print(f"  Output z_axis: {planes[0]['z_axis']}")
    
    # Check Z-Axis input
    z_param = next((p for p in pn['params'] if p['name'] == 'Z-Axis'), None)
    if z_param and z_param.get('sources'):
        src_guid = z_param['sources'][0]
        src = next((c for c in graph['components'] 
                   if any(p['param_guid'] == src_guid for p in c['params'])), None)
        if src:
            print(f"  Z-Axis input from: {src['type_name']}: {src['nickname']}")
            print(f"    Position: ({src['position']['x']}, {src['position']['y']})")

print("\n" + "="*80)
print("QUESTION: Which Plane Normal is being used for Angle Vector A?")
print("="*80)

# Trace Angle -> List Item -> Plane Normal
angle = next((c for c in graph['components'] if c['type_name'] == 'Angle'), None)
va = next((p for p in angle['params'] if p['name'] == 'Vector A'), None)
li_guid = va['sources'][0]
li = next((c for c in graph['components'] 
          if any(p['param_guid'] == li_guid for p in c['params'])), None)
list_src = next((p for p in li['params'] if p['name'] == 'List'), None)['sources'][0]
pn = next((c for c in graph['components'] 
          if any(p['param_guid'] == list_src for p in c['params'])), None)

print(f"\nAngle Vector A is fed by:")
print(f"  List Item at ({li['position']['x']}, {li['position']['y']})")
print(f"  Which gets planes from:")
print(f"  Plane Normal at ({pn['position']['x']}, {pn['position']['y']})")
print(f"  GUID: {pn['guid'][:16]}...")

if pn['guid'] == pn1_guid:
    print(f"\n→ Using FIRST Plane Normal (outputs z_axis = (0, -1, 0)) ✗")
elif pn['guid'] == pn2_guid:
    print(f"\n→ Using SECOND Plane Normal (outputs z_axis = (-1, 0, 0)) ✓")

