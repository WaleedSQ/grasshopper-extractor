import json
import os

# Load all objects
with open('rotatingslats_data.json', 'r') as f:
    data = json.load(f)

all_objs = {**data['group_objects'], **data['external_objects']}

# Load external Vector 2Pt component
ext_file = 'external_vector_2pt_1f794702_component.json'
if os.path.exists(ext_file):
    with open(ext_file, 'r') as f:
        comp = json.load(f)
        comp_guid = comp.get('instance_guid')
        if comp_guid:
            all_objs[comp_guid] = comp
            print(f"Loaded Vector 2Pt component: {comp_guid[:8]}...")

# Build output_params
output_params = {}
for key, obj in all_objs.items():
    for param_key, param_info in obj.get('params', {}).items():
        if param_key.startswith('param_output'):
            param_guid = param_info.get('data', {}).get('InstanceGuid')
            if param_guid:
                output_params[param_guid] = {
                    'obj': obj,
                    'param_key': param_key,
                    'param_info': param_info
                }

target_param = '84214afe-c1b8-443f-8209-3ed4dcca86b9'
print(f"\nOutput param {target_param[:8]}... in output_params: {target_param in output_params}")

if target_param in output_params:
    parent_info = output_params[target_param]
    parent_guid = parent_info['obj'].get('instance_guid')
    parent_type = parent_info['obj'].get('type')
    parent_nickname = parent_info['obj'].get('nickname')
    print(f"  Parent component: {parent_guid[:8] if parent_guid else 'N/A'}...")
    print(f"  Parent type: {parent_type}")
    print(f"  Parent nickname: {parent_nickname}")

