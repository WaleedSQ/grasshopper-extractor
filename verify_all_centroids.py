"""Verify all Area component centroids"""
import json

with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

print("="*80)
print("ALL AREA COMPONENT CENTROIDS")
print("="*80)

area_count = 0
for guid, data in results.items():
    comp_info = data['component_info']
    if comp_info['type'] == 'Area':
        area_count += 1
        print(f"\n{area_count}. {comp_info['nickname']} ({guid[:8]}...)")
        print(f"   Position: ({comp_info['position']['x']}, {comp_info['position']['y']})")
        
        if 'Centroid' in data['outputs']:
            centroid_data = data['outputs']['Centroid']
            if centroid_data['item_count'] > 0:
                for path, items in list(centroid_data['branches'].items())[:3]:
                    print(f"   {path}: {items[:5] if len(items) > 5 else items}")
            else:
                print("   No centroid data")
        
        if 'Area' in data['outputs']:
            area_data = data['outputs']['Area']
            if area_data['item_count'] > 0:
                for path, items in list(area_data['branches'].items())[:1]:
                    print(f"   Area: {items[:1]}")

print(f"\n{'='*80}")
print(f"Total Area components: {area_count}")
print("="*80)

