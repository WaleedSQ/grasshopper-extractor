"""Check if the 10 planes have different origins"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

plane_normal_guid = "011398ea-ce1d-412a-afeb-fe91e8fac96c"

if plane_normal_guid in results:
    planes = results[plane_normal_guid]['outputs']['Plane']['branches']['(0,)']
    
    print("Plane Origins:")
    for i, p in enumerate(planes[:10]):
        origin = p['origin']
        print(f"  [{i}]: [{origin[0]:.6f}, {origin[1]:.6f}, {origin[2]:.6f}]")

