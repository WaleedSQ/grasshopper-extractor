"""
Simple script to find Panel source values.
Run this and it will show you what to search for.
"""
import json

# Panel that needs tracing
panel_guid = "d019d2ee-57d3-4d51-ba22-5ed7ca4fa4f8"
source_guid = "20f5465a-8288-49ad-acd1-2eb24e1f8765"

print("=" * 80)
print("FINDING PANEL SOURCE")
print("=" * 80)
print()
print(f"Panel GUID: {panel_guid}")
print(f"Panel Source GUID: {source_guid}")
print()

# Check in rotatingslats_data.json
print("1. Checking rotatingslats_data.json...")
try:
    with open('rotatingslats_data.json', 'r') as f:
        data = json.load(f)
    
    all_objects = {**data['group_objects'], **data['external_objects']}
    
    # Check if source_guid is a component
    if source_guid in all_objects:
        obj = all_objects[source_guid]
        print(f"   [FOUND] Component: {obj.get('type')} '{obj.get('nickname')}'")
    else:
        print(f"   [NOT FOUND] Not found as component")
    
    # Check if source_guid is an output parameter
    found_as_param = False
    for key, obj in all_objects.items():
        for param_key, param_info in obj.get('params', {}).items():
            param_guid = param_info.get('data', {}).get('InstanceGuid')
            if param_guid == source_guid:
                print(f"   [FOUND] OUTPUT PARAMETER:")
                print(f"     Parent: {obj.get('type')} '{obj.get('nickname')}' ({key[:8]}...)")
                print(f"     Parameter: {param_info.get('data', {}).get('NickName', 'Unknown')}")
                found_as_param = True
                break
        if found_as_param:
            break
    
    if not found_as_param:
        print(f"   [NOT FOUND] Not found as output parameter")
        
except FileNotFoundError:
    print("   ✗ File not found")

# Check in external_inputs.json
print()
print("2. Checking external_inputs.json...")
try:
    with open('external_inputs.json', 'r') as f:
        ext_inputs = json.load(f)
    
    if source_guid in ext_inputs:
        print(f"   [FOUND] In external_inputs:")
        print(f"     Value: {ext_inputs[source_guid]}")
    else:
        print(f"   [NOT FOUND] Not in external_inputs")
        print(f"   Searching by object_guid...")
        for key, val in ext_inputs.items():
            if isinstance(val, dict) and val.get('object_guid') == source_guid:
                print(f"   [FOUND] By object_guid ({key[:8]}...):")
                print(f"     Value: {val.get('value', val)}")
                break
        else:
            print(f"   [NOT FOUND] Not found by object_guid")
            
except FileNotFoundError:
    print("   [ERROR] File not found")

# Instructions
print()
print("=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print()
print("If source was NOT found above, you need to:")
print("1. Search in core-only_fixed.ghx for:")
print(f"   <item name=\"InstanceGuid\">{source_guid}</item>")
print()
print("2. Check what component type it is (TypeName item)")
print()
print("3. Extract its value:")
print("   - If Number Slider: look for <item name=\"Value\">")
print("   - If Number: look in PersistentData -> number")
print("   - If Panel: trace its Source recursively")
print("   - If output parameter: evaluate parent component first")
print()
print("4. Add to external_inputs.json:")
print(f'   "{panel_guid}": {{')
print(f'     "value": <FOUND_VALUE>,')
print(f'     "object_type": "Panel",')
print(f'     "object_nickname": "Distance between slats",')
print(f'     "source_guid": "{source_guid}",')
print(f'     "object_guid": "{panel_guid}"')
print(f'   }}')

