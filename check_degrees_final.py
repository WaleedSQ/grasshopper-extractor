"""Check final Degrees output"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

degrees_guid = "fa0ba5a6-7dd9-43f4-a82a-cf02841d0f58"

screenshot_values = [
    43.701519,
    43.033895,
    42.213797,
    41.218013,
    39.968747,
    38.335501,
    36.180578,
    33.323467,
    29.029873,
    22.969535
]

if degrees_guid in results:
    degrees_data = results[degrees_guid]
    degrees_output = degrees_data['outputs']['Degrees']
    degrees_values = degrees_output['branches']['(0,)']
    
    print("="*80)
    print("DEGREES OUTPUT COMPARISON")
    print("="*80)
    print(f"\nCurrent: {len(degrees_values)} items")
    print(f"Expected: {len(screenshot_values)} items\n")
    
    print("Index | Current      | Expected     | Match?")
    print("-" * 60)
    
    for i in range(min(len(degrees_values), len(screenshot_values))):
        current = degrees_values[i]
        expected = screenshot_values[i]
        match = "YES" if abs(current - expected) < 1.0 else "NO"
        print(f"  [{i}] | {current:12.6f} | {expected:12.6f} | {match}")

print("\n" + "="*80)
listitem_guid = "9ff79870-05d0-483d-87be-b3641d71c6fc"
if listitem_guid in results:
    listitem_data = results[listitem_guid]
    listitem_output = listitem_data['outputs']['Item']
    print(f"List Item with expression: {listitem_output['item_count']} items")

plane_normal_guid = "011398ea-ce1d-412a-afeb-fe91e8fac96c"
if plane_normal_guid in results:
    plane_data = results[plane_normal_guid]
    plane_output = plane_data['outputs']['Plane']
    plane_values = plane_output['branches']['(0,)']
    z_axis = plane_values[0]['z_axis']
    print(f"Plane Normal Z-axis: ({z_axis[0]:.2f}, {z_axis[1]:.2f}, {z_axis[2]:.2f}) - {'CORRECT' if z_axis[0]==-1 else 'WRONG'}")
print("="*80)

