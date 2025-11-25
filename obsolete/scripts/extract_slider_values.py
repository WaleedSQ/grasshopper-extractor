"""
Extract Number Slider values from GHX file.
"""
import xml.etree.ElementTree as ET
import json

room_width_guid = "a7d2817a-3182-496e-a453-80e7eeba16fa"

tree = ET.parse('core-only_fixed.ghx')

print("=" * 80)
print("EXTRACTING NUMBER SLIDER VALUES FROM GHX")
print("=" * 80)
print()

# Find all Object chunks
slider_values = {}

for obj_chunk in tree.findall('.//chunk[@name="Object"]'):
    # Get InstanceGuid
    instance_guid = None
    obj_type = None
    nickname = None
    
    for item in obj_chunk.findall('.//item'):
        item_name = item.get('name')
        if item_name == 'InstanceGuid':
            instance_guid = item.text
        elif item_name == 'TypeName':
            obj_type = item.text
        elif item_name == 'NickName':
            nickname = item.text
        elif item_name == 'Name':
            # Also check Name field for component type
            if obj_type is None and 'slider' in item.text.lower():
                obj_type = 'GH_NumberSlider'
    
    # Check if it's a Number Slider (by TypeName or by Name containing "Number Slider")
    is_slider = (obj_type == 'GH_NumberSlider' or 
                 (obj_type is None and nickname and 'slider' in nickname.lower()) or
                 any(item.text and 'Number Slider' in item.text for item in obj_chunk.findall('.//item[@name="Name"]')))
    
    if is_slider and instance_guid:
        # Number Slider found - extract its value
        # The value is stored directly as an item with name="Value"
        value = None
        
        # Check for Value item directly in the object
        value_item = obj_chunk.find('.//item[@name="Value"]')
        if value_item is not None:
            try:
                value = float(value_item.text)
            except (ValueError, TypeError):
                pass
        
        # Also check PersistentData -> Branch -> Item -> number
        if value is None:
            persistent_data = obj_chunk.find('.//chunk[@name="PersistentData"]')
            if persistent_data is not None:
                # Look for number item
                number_item = persistent_data.find('.//item[@name="number"]')
                if number_item is not None:
                    try:
                        value = float(number_item.text)
                    except (ValueError, TypeError):
                        pass
                
                # Also check for value in Branch -> Item structure
                if value is None:
                    for branch in persistent_data.findall('.//chunk[@name="Branch"]'):
                        for item_chunk in branch.findall('.//chunk[@name="Item"]'):
                            number_item = item_chunk.find('.//item[@name="number"]')
                            if number_item is not None:
                                try:
                                    value = float(number_item.text)
                                    break
                                except (ValueError, TypeError):
                                    pass
                            if value is not None:
                                break
                        if value is not None:
                            break
        
        if value is not None:
            slider_values[instance_guid] = {
                'value': value,
                'nickname': nickname or 'Unnamed',
                'type': obj_type
            }
            print(f"Found Number Slider: '{nickname}' ({instance_guid[:8]}...) = {value}")

# Check specifically for room width
if room_width_guid in slider_values:
    print(f"\n[OK] Room width slider found: {slider_values[room_width_guid]['value']}")
else:
    print(f"\n[NOT FOUND] Room width slider ({room_width_guid[:8]}...) not found in slider values")
    print("  Checking if it exists in the file...")
    
    # Check if the object exists at all
    for obj_chunk in tree.findall('.//chunk[@name="Object"]'):
        for item in obj_chunk.findall('.//item[@name="InstanceGuid"]'):
            if item.text == room_width_guid:
                print(f"  Found object with GUID, but couldn't extract value")
                # Try to print the structure
                persistent_data = obj_chunk.find('.//chunk[@name="PersistentData"]')
                if persistent_data is not None:
                    print(f"  PersistentData found, structure:")
                    for elem in persistent_data.iter():
                        if elem.tag == 'item':
                            print(f"    {elem.get('name')}: {elem.text}")

print()
print("=" * 80)
print(f"Total sliders found: {len(slider_values)}")
print("=" * 80)

# Update external_inputs.json with slider values
try:
    with open('external_inputs.json', 'r') as f:
        external_inputs = json.load(f)
except FileNotFoundError:
    external_inputs = {}

# Add slider values
for guid, info in slider_values.items():
    if guid not in external_inputs:
        external_inputs[guid] = {
            'value': info['value'],
            'object_type': info['type'],
            'object_nickname': info['nickname'],
            'parameter_name': 'Value',
            'parameter_guid': None,
            'object_guid': guid
        }
    else:
        # Update value if it's a slider
        external_inputs[guid]['value'] = info['value']

# Save updated external inputs
with open('external_inputs.json', 'w') as f:
    json.dump(external_inputs, f, indent=2, default=str)

print("\nUpdated external_inputs.json with slider values")

