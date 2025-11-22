"""Check Plane Normal output structure in detail"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

# Plane Normal that feeds Angle
plane_normal_guid = "011398ea-ce1d-412a-afeb-fe91e8fac96c"

if plane_normal_guid in results:
    data = results[plane_normal_guid]
    comp_info = data['component_info']
    
    print("="*80)
    print(f"{comp_info['type']}: {comp_info['nickname']} ({plane_normal_guid[:8]}...)")
    print("="*80)
    
    for output_name, output_data in data['outputs'].items():
        print(f"\n{output_name}:")
        print(f"  Total items: {output_data['item_count']}")
        print(f"  Branches: {output_data['branch_count']}")
        print(f"\n  Branch structure:")
        
        for path, items in output_data['branches'].items():
            print(f"    Path {path}: {len(items)} items")
            if len(items) <= 12:
                for i, item in enumerate(items):
                    if isinstance(item, dict) and 'z_axis' in item:
                        z = item['z_axis']
                        print(f"      [{i}]: Plane with z_axis = [{z[0]:.4f}, {z[1]:.4f}, {z[2]:.4f}]")

print("\n" + "="*80)
print("Note: In the screenshot, Angle output shows {0;0} path")
print("But my Plane Normal shows {0} path")
print("="*80)

