"""
Extract external input values from GHX file for placeholder components.
"""
import xml.etree.ElementTree as ET
import json
import re

def parse_ghx_for_external_inputs(ghx_file='core-only_fixed.ghx'):
    """Extract external input values from GHX."""
    
    # Read GHX file
    with open(ghx_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse XML
    tree = ET.parse(ghx_file)
    root = tree.getroot()
    
    external_inputs = {}
    
    # Find all Object chunks
    for obj_chunk in root.findall('.//chunk[@name="Object"]'):
        container = obj_chunk.find('.//chunk[@name="Container"]')
        if container is None:
            continue
        
        instance_guid_elem = container.find('.//item[@name="InstanceGuid"]')
        if instance_guid_elem is None:
            continue
        
        instance_guid = instance_guid_elem.text
        name_elem = container.find('.//item[@name="Name"]')
        name = name_elem.text if name_elem is not None else None
        
        # MD Slider (c4c92669-f802-4b5f-b3fb-61b8a642dc0a)
        if instance_guid == 'c4c92669-f802-4b5f-b3fb-61b8a642dc0a':
            slider_value = container.find('.//item[@name="slider_value"]')
            if slider_value is not None:
                x = float(slider_value.find('X').text)
                y = float(slider_value.find('Y').text)
                z = float(slider_value.find('Z').text)
                external_inputs[instance_guid] = {
                    'value': [x, y, z],
                    'type': 'MD Slider',
                    'object_guid': instance_guid
                }
                print(f"MD Slider {instance_guid[:8]}...: [{x}, {y}, {z}]")
        
        # Value List (e5d1f3af-f59d-40a8-aa35-162cf16c9594)
        elif instance_guid == 'e5d1f3af-f59d-40a8-aa35-162cf16c9594':
            # Value List has ListItem chunks with Expression and Selected
            list_items = container.findall('.//chunk[@name="ListItem"]')
            all_values = []
            selected_value = None
            for list_item in list_items:
                expression_elem = list_item.find('.//item[@name="Expression"]')
                selected_elem = list_item.find('.//item[@name="Selected"]')
                if expression_elem is not None:
                    try:
                        val = float(expression_elem.text)
                        all_values.append(val)
                        # Check if this item is selected
                        if selected_elem is not None and selected_elem.text.lower() == 'true':
                            selected_value = val
                    except (ValueError, TypeError):
                        pass
            if all_values:
                # Use selected value if found, otherwise use all values
                value_to_store = selected_value if selected_value is not None else all_values
                external_inputs[instance_guid] = {
                    'value': value_to_store,
                    'type': 'Value List',
                    'object_guid': instance_guid,
                    'all_values': all_values,
                    'selected_index': selected_value
                }
                print(f"Value List {instance_guid[:8]}...: all={all_values}, selected={selected_value}")
        
        # Point (12d02e9b-6145-4953-8f48-b184902a818f)
        elif instance_guid == '12d02e9b-6145-4953-8f48-b184902a818f':
            # Check for Source connection
            source_elem = container.find('.//item[@name="Source"]')
            if source_elem is not None:
                source_guid = source_elem.text
                print(f"Point {instance_guid[:8]}... has Source: {source_guid[:8]}...")
                # Trace the source - find component with this output GUID
                # This will be resolved during evaluation, but we can note it
                external_inputs[instance_guid] = {
                    'value': None,  # Will be resolved from source
                    'type': 'Point',
                    'object_guid': instance_guid,
                    'source_guid': source_guid
                }
            else:
                # Check for PersistentData
                persistent_data = container.find('.//chunk[@name="PersistentData"]')
                if persistent_data is not None:
                    coord_elem = persistent_data.find('.//item[@name="Coordinate"]')
                    if coord_elem is not None:
                        x = float(coord_elem.find('X').text)
                        y = float(coord_elem.find('Y').text)
                        z = float(coord_elem.find('Z').text)
                        external_inputs[instance_guid] = {
                            'value': [x, y, z],
                            'type': 'Point',
                            'object_guid': instance_guid
                        }
                        print(f"Point {instance_guid[:8]}...: [{x}, {y}, {z}]")
        
        # Surface (8fec620f-ff7f-4b94-bb64-4c7fce2fcb34)
        elif instance_guid == '8fec620f-ff7f-4b94-bb64-4c7fce2fcb34':
            # Check for Container-level Source
            source_elem = container.find('.//item[@name="Source"]')
            if source_elem is not None:
                source_guid = source_elem.text
                print(f"Surface {instance_guid[:8]}... has Source: {source_guid[:8]}...")
                external_inputs[instance_guid] = {
                    'value': None,  # Will be resolved from source (Rectangle 2Pt)
                    'type': 'Surface',
                    'object_guid': instance_guid,
                    'source_guid': source_guid
                }
    
    # Now trace Point source (567ff6ee-60ff-40f6-ac83-4dfc36f2fda7)
    # Find what component produces this output
    for obj_chunk in root.findall('.//chunk[@name="Object"]'):
        container = obj_chunk.find('.//chunk[@name="Container"]')
        if container is None:
            continue
        
        # Check if this is the Geometry component with instance_guid 567ff6ee...
        instance_guid_elem = container.find('.//item[@name="InstanceGuid"]')
        if instance_guid_elem is not None and instance_guid_elem.text == '567ff6ee-60ff-40f6-ac83-4dfc36f2fda7':
            # This is a Geometry component - external input from Rhino
            name_elem = container.find('.//item[@name="Name"]')
            parent_name = name_elem.text if name_elem is not None else None
            print(f"Point source {instance_guid_elem.text[:8]}... is Geometry component ({parent_name}) - external Rhino input")
            # Geometry components don't have values in GHX, they're external
            external_inputs['567ff6ee-60ff-40f6-ac83-4dfc36f2fda7'] = {
                'value': None,  # External geometry - no value in GHX
                'type': 'Geometry (external)',
                'object_guid': '567ff6ee-60ff-40f6-ac83-4dfc36f2fda7',
                'note': 'External geometry input from Rhino - no value in GHX'
            }
        
        # Also check param_output chunks for this GUID
        param_outputs = container.findall('.//chunk[@name="param_output"]')
        for param_output in param_outputs:
            output_guid_elem = param_output.find('.//item[@name="InstanceGuid"]')
            if output_guid_elem is not None and output_guid_elem.text == '567ff6ee-60ff-40f6-ac83-4dfc36f2fda7':
                # Found the output parameter
                parent_instance_guid = container.find('.//item[@name="InstanceGuid"]')
                if parent_instance_guid is not None:
                    parent_guid = parent_instance_guid.text
                    name_elem = container.find('.//item[@name="Name"]')
                    parent_name = name_elem.text if name_elem is not None else None
                    print(f"Point source {output_guid_elem.text[:8]}... is output of {parent_name} ({parent_guid[:8]}...)")
                    # Check if this component has PersistentData
                    persistent_data = param_output.find('.//chunk[@name="PersistentData"]')
                    if persistent_data is not None:
                        coord_elem = persistent_data.find('.//item[@name="Coordinate"]')
                        if coord_elem is not None:
                            x = float(coord_elem.find('X').text)
                            y = float(coord_elem.find('Y').text)
                            z = float(coord_elem.find('Z').text)
                            external_inputs['567ff6ee-60ff-40f6-ac83-4dfc36f2fda7'] = {
                                'value': [x, y, z],
                                'type': 'Point (from source)',
                                'object_guid': parent_guid,
                                'output_guid': '567ff6ee-60ff-40f6-ac83-4dfc36f2fda7'
                            }
                            print(f"  Found point value: [{x}, {y}, {z}]")
    
    return external_inputs

if __name__ == '__main__':
    print("Extracting external inputs from GHX...")
    inputs = parse_ghx_for_external_inputs()
    
    # Load existing external_inputs.json
    try:
        with open('external_inputs.json', 'r') as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = {}
    
    # Merge new inputs
    for guid, value_info in inputs.items():
        if guid not in existing or existing[guid].get('value') is None:
            existing[guid] = value_info
    
    # Save updated external_inputs.json
    with open('external_inputs.json', 'w') as f:
        json.dump(existing, f, indent=2)
    
    print(f"\nUpdated external_inputs.json with {len(inputs)} new entries")

