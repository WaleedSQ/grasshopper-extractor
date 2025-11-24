"""Compare our evaluation results with screenshot values"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

print("="*80)
print("COMPARING EVALUATION RESULTS WITH SCREENSHOTS")
print("="*80)

# Plane Normal 1 (at 12043, 2991)
pn1_guid = '326da981-351e-4794-9d60-77e8e87bd778'
print("\n" + "="*80)
print("PLANE NORMAL 1 (at position 12043, 2991)")
print("="*80)
print("Screenshot shows: Bottom-Left Panel")
print("  Format: O(x,y,z) Z(x,y,z)")
print("  Expected: 10 planes with Z(0.00,-1.00,0.00)")
print("  Y coordinates vary: 3.80 to 3.10")

if pn1_guid in results:
    pn1_planes = results[pn1_guid]['outputs']['Plane']['branches']
    first_branch = list(pn1_planes.values())[0]
    
    print(f"\nOur evaluation: {len(first_branch)} plane(s) in first branch")
    
    for i, plane in enumerate(first_branch[:3]):
        origin = plane['origin']
        z_axis = plane['z_axis']
        print(f"\n  Plane {i}:")
        print(f"    Origin: O({origin[0]:.2f},{origin[1]:.2f},{origin[2]:.2f})")
        print(f"    Z-axis: Z({z_axis[0]:.2f},{z_axis[1]:.2f},{z_axis[2]:.2f})")
        print(f"    Expected Z: (0.00,-1.00,0.00)")
        
        if z_axis == [0.0, -1.0, 0.0]:
            print(f"    MATCHES!")
        else:
            print(f"    DOES NOT MATCH")
    
    # Check all 10 planes
    if len(first_branch) == 10:
        print(f"\n  All 10 planes:")
        z_axes = [p['z_axis'] for p in first_branch]
        origins_y = [p['origin'][2] for p in first_branch]  # Z coordinate in origin
        
        all_match_z = all(z == [0.0, -1.0, 0.0] for z in z_axes)
        print(f"    All Z-axes match (0, -1, 0): {all_match_z}")
        print(f"    Y coordinates (origin Z): {[f'{y:.2f}' for y in origins_y]}")
        print(f"    Expected range: 3.80 to 3.10")

# Construct Plane (at 12039, 3119)
cp_guid = '30f76ec5-d532-4903-aa18-cd18b27442f9'
print("\n" + "="*80)
print("CONSTRUCT PLANE (at position 12039, 3119)")
print("="*80)
print("Screenshot shows: Bottom-Middle Panel")
print("  Format: O(x,y,z) Z(x,y,z)")
print("  Expected: 10 planes with Z(-1.00,0.00,0.00)")
print("  Y coordinates vary: 3.80 to 3.10")

if cp_guid in results:
    cp_planes = results[cp_guid]['outputs']['Plane']['branches']
    first_branch = list(cp_planes.values())[0]
    
    print(f"\nOur evaluation: {len(first_branch)} plane(s) in first branch")
    
    for i, plane in enumerate(first_branch[:3]):
        origin = plane['origin']
        z_axis = plane['z_axis']
        print(f"\n  Plane {i}:")
        print(f"    Origin: O({origin[0]:.2f},{origin[1]:.2f},{origin[2]:.2f})")
        print(f"    Z-axis: Z({z_axis[0]:.2f},{z_axis[1]:.2f},{z_axis[2]:.2f})")
        print(f"    Expected Z: (-1.00,0.00,0.00)")
        
        if z_axis == [-1.0, 0.0, 0.0]:
            print(f"    MATCHES!")
        else:
            print(f"    DOES NOT MATCH")
    
    # Check all 10 planes
    if len(first_branch) == 10:
        print(f"\n  All 10 planes:")
        z_axes = [p['z_axis'] for p in first_branch]
        origins_y = [p['origin'][2] for p in first_branch]  # Z coordinate in origin
        
        all_match_z = all(z == [-1.0, 0.0, 0.0] for z in z_axes)
        print(f"    All Z-axes match (-1, 0, 0): {all_match_z}")
        print(f"    Y coordinates (origin Z): {[f'{y:.2f}' for y in origins_y]}")
        print(f"    Expected range: 3.80 to 3.10")

# Plane Normal 2 (at 12184, 3075)
pn2_guid = '011398ea-ce1d-412a-afeb-fe91e8fac96c'
print("\n" + "="*80)
print("PLANE NORMAL 2 (at position 12184, 3075)")
print("="*80)
print("Screenshot shows: Bottom-Right Panel")
print("  Format: O(x,y,z) Z(x,y,z)")
print("  Expected: 10 planes with Z(-1.00,0.00,0.00)")
print("  Y coordinate constant: 3.10")

if pn2_guid in results:
    pn2_planes = results[pn2_guid]['outputs']['Plane']['branches']
    first_branch = list(pn2_planes.values())[0]
    
    print(f"\nOur evaluation: {len(first_branch)} plane(s) in first branch")
    
    for i, plane in enumerate(first_branch[:3]):
        origin = plane['origin']
        z_axis = plane['z_axis']
        print(f"\n  Plane {i}:")
        print(f"    Origin: O({origin[0]:.2f},{origin[1]:.2f},{origin[2]:.2f})")
        print(f"    Z-axis: Z({z_axis[0]:.2f},{z_axis[1]:.2f},{z_axis[2]:.2f})")
        print(f"    Expected Z: (0.00,-1.00,0.00) OR (-1.00,0.00,0.00)?")
        
        # Check which one matches
        if z_axis == [0.0, -1.0, 0.0]:
            print(f"    Matches (0, -1, 0)")
        elif z_axis == [-1.0, 0.0, 0.0]:
            print(f"    Matches (-1, 0, 0)")
        else:
            print(f"    DOES NOT MATCH either")
    
    # Check all 10 planes
    if len(first_branch) == 10:
        print(f"\n  All 10 planes:")
        z_axes = [p['z_axis'] for p in first_branch]
        origins_y = [p['origin'][2] for p in first_branch]  # Z coordinate in origin
        
        all_same_z = len(set(tuple(z) for z in z_axes)) == 1
        all_same_y = len(set(origins_y)) == 1
        print(f"    All Z-axes same: {all_same_z} (value: {z_axes[0]})")
        print(f"    All Y coordinates same: {all_same_y} (value: {origins_y[0]:.2f})")
        print(f"    Expected constant Y: 3.10")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("Checking if all values match the screenshots...")

