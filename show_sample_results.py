"""Show sample results with nicknames"""
import json

with open('rotatingslats_evaluation_results.json', 'r') as f:
    results = json.load(f)

print("Sample of Enhanced Results:")
print("="*80)

for i, (guid, data) in enumerate(list(results.items())[:10], 1):
    info = data['component_info']
    outputs = data['outputs']
    
    print(f"\n{i}. {info['type']}: \"{info['nickname']}\"")
    print(f"   GUID: {guid[:8]}...")
    print(f"   Position: ({info['position']['x']}, {info['position']['y']})")
    print(f"   Outputs:")
    for output_name, output_data in outputs.items():
        print(f"     - {output_name}: {output_data['item_count']} items in {output_data['branch_count']} branch(es)")

print("\n" + "="*80)
print(f"Total components: {len(results)}")

