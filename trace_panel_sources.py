"""
Trace Panel Source connections to find their actual values.
This script shows how to trace Panel -> Source -> Value.
"""
import xml.etree.ElementTree as ET
import json

tree = ET.parse('core-only_fixed.ghx')

print("=" * 80)
print("TRACING PANEL SOURCE CONNECTIONS")
print("=" * 80)
print()

panel_traces = {}

# Find all Panel components
for obj_chunk in tree.findall('.//chunk[@name="Object"]'):
    instance_guid = None
    nickname = None
    obj_type = None
    source_guid = None
    
    for item in obj_chunk.findall('.//item'):
        item_name = item.get('name')
        if item_name == 'InstanceGuid':
            instance_guid = item.text
        elif item_name == 'NickName':
            nickname = item.text
        elif item_name == 'TypeName':
            obj_type = item.text
        elif item_name == 'Source':
            source_guid = item.text
        elif item_name == 'Name':
            if obj_type is None and 'Panel' in item.text:
                obj_type = 'GH_Panel'
    
    # Check if it's a Panel
    is_panel = (obj_type == 'GH_Panel' or 
                (obj_type is None and nickname and 'panel' in nickname.lower()) or
                any(item.text and 'Panel' in item.text for item in obj_chunk.findall('.//item[@name="Name"]')))
    
    if is_panel and instance_guid:
        print(f"Found Panel: '{nickname}' ({instance_guid[:8]}...)")
        
        if source_guid:
            print(f"  Has Source: {source_guid[:8]}...")
            
            # Trace the source
            source_value = None
            source_type = None
            source_nickname = None
            
            # First check in rotatingslats_data.json
            try:
                with open('rotatingslats_data.json', 'r') as f:
                    data = json.load(f)
                
                all_objects = {**data['group_objects'], **data['external_objects']}
                
                # Check if source_guid is an output parameter
                output_params = {}
                for key, obj in all_objects.items():
                    for param_key, param_info in obj.get('params', {}).items():
                        param_guid = param_info.get('data', {}).get('InstanceGuid')
                        if param_guid == source_guid:
                            # It's an output parameter
                            parent_obj = obj
                            source_type = parent_obj.get('type')
                            source_nickname = parent_obj.get('nickname')
                            param_name = param_info.get('data', {}).get('NickName', '')
                            print(f"    Source is OUTPUT PARAMETER: {source_type} '{source_nickname}' -> {param_name}")
                            # The value would come from evaluating the parent component
                            break
                
                # Check if source_guid is a component
                if source_guid in all_objects:
                    source_obj = all_objects[source_guid]
                    source_type = source_obj.get('type')
                    source_nickname = source_obj.get('nickname')
                    print(f"    Source is COMPONENT: {source_type} '{source_nickname}'")
                    
                    # Check if it's a Number Slider - look in external_inputs
                    if source_type == 'Number Slider':
                        with open('external_inputs.json', 'r') as f:
                            ext_inputs = json.load(f)
                        if source_guid in ext_inputs:
                            ext_val = ext_inputs[source_guid]
                            if isinstance(ext_val, dict):
                                source_value = ext_val.get('value')
                            else:
                                source_value = ext_val
                            print(f"      Found value in external_inputs: {source_value}")
                
            except FileNotFoundError:
                pass
            
            # Also check GHX file for the source
            if source_value is None:
                for source_chunk in tree.findall('.//chunk[@name="Object"]'):
                    for item in source_chunk.findall('.//item[@name="InstanceGuid"]'):
                        if item.text == source_guid:
                            # Found source component
                            for item in source_chunk.findall('.//item'):
                                name = item.get('name')
                                if name == 'TypeName':
                                    source_type = item.text
                                elif name == 'NickName':
                                    source_nickname = item.text
                            
                            # Check if it's a Number Slider
                            if source_type == 'GH_NumberSlider':
                                # Extract value
                                value_item = source_chunk.find('.//item[@name="Value"]')
                                if value_item is not None:
                                    try:
                                        source_value = float(value_item.text)
                                    except (ValueError, TypeError):
                                        pass
                            
                            # Check if it's a Number component
                            elif source_type == 'GH_Number':
                                # Check PersistentData
                                persistent_data = source_chunk.find('.//chunk[@name="PersistentData"]')
                                if persistent_data is not None:
                                    number_item = persistent_data.find('.//item[@name="number"]')
                                    if number_item is not None:
                                        try:
                                            source_value = float(number_item.text)
                                        except (ValueError, TypeError):
                                            pass
                            
                            break
                    
                    if source_value is not None:
                        break
            
            if source_value is not None:
                print(f"  -> Traced to: {source_type} '{source_nickname}' = {source_value}")
                panel_traces[instance_guid] = {
                    'value': source_value,
                    'source_guid': source_guid,
                    'source_type': source_type,
                    'source_nickname': source_nickname,
                    'panel_nickname': nickname
                }
            else:
                print(f"  -> Could not trace source value (type: {source_type}, nickname: {source_nickname})")
        else:
            print(f"  No Source connection")
        
        print()

print("=" * 80)
print(f"Total Panels traced: {len(panel_traces)}")
print("=" * 80)

# Show example output format
if panel_traces:
    print("\nExample trace result:")
    for guid, info in panel_traces.items():
        print(f"\nPanel: {info['panel_nickname']} ({guid[:8]}...)")
        print(f"  Source: {info['source_type']} '{info['source_nickname']}' ({info['source_guid'][:8]}...)")
        print(f"  Value: {info['value']}")
        print(f"\n  JSON format:")
        print(f"  \"{guid}\": {{")
        print(f"    \"value\": {info['value']},")
        print(f"    \"object_type\": \"Panel\",")
        print(f"    \"object_nickname\": \"{info['panel_nickname']}\",")
        print(f"    \"source_guid\": \"{info['source_guid']}\",")
        print(f"    \"source_type\": \"{info['source_type']}\",")
        print(f"    \"object_guid\": \"{guid}\"")
        print(f"  }}")

# Save to file for reference
with open('panel_source_traces.json', 'w') as f:
    json.dump(panel_traces, f, indent=2, default=str)

print(f"\nSaved traces to panel_source_traces.json")

