"""
Extract all external inputs (sliders, panels, constants) from the Rotatingslats data.
"""
import json

with open('rotatingslats_data.json', 'r') as f:
    data = json.load(f)

all_objects = {**data['group_objects'], **data['external_objects']}

external_inputs = {}

print("=" * 80)
print("EXTRACTING EXTERNAL INPUTS AND CONSTANTS")
print("=" * 80)
print()

for obj_key, obj in all_objects.items():
    obj_guid = obj.get('instance_guid') or obj.get('guid')
    obj_type = obj.get('type', 'Unknown')
    obj_nickname = obj.get('nickname', 'Unnamed')
    
    # Check all input parameters for constant values
    for param_key, param_info in obj.get('params', {}).items():
        if param_key.startswith('param_input'):
            sources = param_info.get('sources', [])
            persistent_values = param_info.get('persistent_values', [])
            values = param_info.get('values', [])
            
            # If no sources and has a value, it's an external input or constant
            if not sources and (persistent_values or values):
                param_name = param_info.get('data', {}).get('NickName', param_key)
                param_guid = param_info.get('data', {}).get('InstanceGuid')
                
                # Get the value
                value = None
                if persistent_values:
                    value_str = persistent_values[0]
                elif values:
                    value_str = values[0]
                else:
                    continue
                
                # Try to convert to number
                try:
                    if '.' in value_str:
                        value = float(value_str)
                    else:
                        value = int(value_str)
                except ValueError:
                    value = value_str
                
                # Store by parameter GUID if available, otherwise by object GUID
                key = param_guid if param_guid else obj_guid
                external_inputs[key] = {
                    'value': value,
                    'object_type': obj_type,
                    'object_nickname': obj_nickname,
                    'parameter_name': param_name,
                    'parameter_guid': param_guid,
                    'object_guid': obj_guid
                }
                
                print(f"{obj_type} '{obj_nickname}' -> {param_name}: {value}")
                if param_guid:
                    print(f"  Parameter GUID: {param_guid}")
                print(f"  Object GUID: {obj_guid}")
                print()

# Also check for the source GUID mentioned in the task
source_guid = "a7d2817a-3182-496e-a453-80e7eeba16fa"
if source_guid in external_inputs:
    print(f"Found source GUID {source_guid[:8]}...: {external_inputs[source_guid]}")
else:
    print(f"Source GUID {source_guid[:8]}... not found in external inputs")
    # Check if it's in the objects
    for obj_key, obj in all_objects.items():
        if obj.get('instance_guid') == source_guid or obj.get('guid') == source_guid:
            print(f"  Found object: {obj.get('type')} '{obj.get('nickname')}'")
            # Check its parameters
            for param_key, param_info in obj.get('params', {}).items():
                if param_key.startswith('param_output'):
                    param_guid = param_info.get('data', {}).get('InstanceGuid')
                    if param_guid:
                        print(f"    Output: {param_info.get('data', {}).get('NickName')} ({param_guid})")

print()
print("=" * 80)
print(f"Total external inputs/constants found: {len(external_inputs)}")
print("=" * 80)

# Save to JSON
with open('external_inputs.json', 'w') as f:
    json.dump(external_inputs, f, indent=2, default=str)

print("\nSaved to external_inputs.json")

