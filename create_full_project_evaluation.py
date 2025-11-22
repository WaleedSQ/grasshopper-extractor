"""Create comprehensive evaluation output for both Rotatingslats and Slats control"""

import json

# Load data
with open('ghx_graph.json') as f:
    full_graph = json.load(f)

with open('rotatingslats_graph.json') as f:
    rot_graph = json.load(f)

with open('rotatingslats_inputs.json') as f:
    inputs = json.load(f)

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

# Find the slats control group
slats_control_guid = '85286674-9111-419a-9e16-d7f5002f685f'

# Build component index
all_components = {c['guid']: c for c in full_graph['components']}

# Find slats control members
slats_control_components = []
for comp in full_graph['components']:
    if comp['guid'] == slats_control_guid:
        # This is the group itself
        for member_guid in comp.get('members', []):
            if member_guid in all_components:
                slats_control_components.append(all_components[member_guid])

print("=" * 80)
print("FULL PROJECT STRUCTURE")
print("=" * 80)
print()

print("1. SLATS CONTROL GROUP")
print(f"   GUID: {slats_control_guid}")
print(f"   Components: {len(slats_control_components)}")
print()

if slats_control_components:
    print("   Components in Slats Control:")
    for comp in slats_control_components:
        nickname = comp.get('nickname', comp.get('type_name', 'Unknown'))
        print(f"     - {comp['type_name']}: {nickname}")
        if comp['type_name'] == 'Number Slider':
            # Show value
            for param in comp.get('params', []):
                if param.get('name') == 'Number' and param.get('persistent_data'):
                    print(f"       Value: {param['persistent_data']}")
                    break
else:
    print("   No components found (may need to parse group container)")

print()
print("2. ROTATINGSLATS GROUP")
print(f"   GUID: a310b28b-ac76-4228-8c67-f796bf6ee11f")
print(f"   Components: {len(rot_graph['components'])}")
print(f"   Evaluated: {len(results)} / {len(rot_graph['components'])}")
print()

print("=" * 80)
print("EVALUATION OUTPUT")
print("=" * 80)
print()

# Create comprehensive output
output = {
    "project": {
        "source_file": "refactored-no-sun.ghx",
        "total_components": len(full_graph['components']),
        "evaluation_date": "2025-11-22"
    },
    "slats_control": {
        "group_guid": slats_control_guid,
        "description": "Input sliders for controlling slat geometry",
        "sliders": {}
    },
    "rotatingslats": {
        "group_guid": "a310b28b-ac76-4228-8c67-f796bf6ee11f",
        "description": "Main computation group for rotating slats geometry",
        "components_total": len(rot_graph['components']),
        "components_evaluated": len(results),
        "success_rate": f"{len(results) / len(rot_graph['components']) * 100:.1f}%"
    },
    "external_inputs": {},
    "key_outputs": {}
}

# Add slider values
for guid, data in inputs.items():
    nickname = data['nickname']
    value = data['data'][0] if data['data'] else None
    output["external_inputs"][nickname] = {
        "guid": guid,
        "type": data['type'],
        "value": value
    }
    output["slats_control"]["sliders"][nickname] = value

# Add key outputs
# Vector 2Pt
vector2pt_guid = 'ea032caa-ddff-403c-ab58-8ab6e24931ac'
if vector2pt_guid in results:
    vec_data = results[vector2pt_guid]
    vector_out = vec_data.get('Vector', {})
    length_out = vec_data.get('Length', {})
    
    if vector_out.get('branch_count', 0) > 0:
        branches = vector_out['branches']
        vectors = list(branches.values())[0]
        lengths = list(length_out['branches'].values())[0] if length_out.get('branch_count', 0) > 0 else []
        
        output["key_outputs"]["Vector_2Pt"] = {
            "component_guid": vector2pt_guid,
            "description": "Direction vectors for slat orientation",
            "vectors": vectors,
            "lengths": lengths
        }

# Rotate components (final slat geometry)
rotate_comps = [c for c in rot_graph['components'] if c['type_name'] == 'Rotate']
output["key_outputs"]["Rotated_Slats"] = []

for rot_comp in rotate_comps:
    if rot_comp['guid'] in results:
        rot_data = results[rot_comp['guid']]
        geom_out = rot_data.get('Geometry', {})
        
        if geom_out.get('branch_count', 0) > 0:
            branches = geom_out['branches']
            geometry = list(branches.values())[0]
            
            output["key_outputs"]["Rotated_Slats"].append({
                "component_guid": rot_comp['guid'],
                "nickname": rot_comp['nickname'],
                "geometry": geometry[:3] if len(geometry) > 3 else geometry,  # Sample
                "total_items": len(geometry)
            })

# Save output
with open('full_project_evaluation.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Saved: full_project_evaluation.json")
print()

print("SUMMARY:")
print(f"  Slats Control: {len(output['slats_control']['sliders'])} sliders")
print(f"  Rotatingslats: {output['rotatingslats']['components_evaluated']}/{output['rotatingslats']['components_total']} components")
print(f"  Key outputs: {len(output['key_outputs'])} collections")
print()

print("=" * 80)

