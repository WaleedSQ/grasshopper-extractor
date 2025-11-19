"""
Extract PersistentData values from Construct Point components.
"""
import xml.etree.ElementTree as ET
import json

def extract_construct_point_persistent_data(ghx_file='core-only_fixed.ghx'):
    """Extract PersistentData from Construct Point components."""
    
    tree = ET.parse(ghx_file)
    root = tree.getroot()
    
    # GUIDs of Construct Point components from external_inputs.json
    construct_point_guids = {
        'a6b98c27-e4dd-405e-93f5-755c12294748': 'p1',
        '577ce3f3-2b5e-4a55-ae60-c5c3c6c12e3c': 'p1',
        '57648120-f088-4498-99d0-f8f7f3b69b89': 'Target point'
    }
    
    # Parameter GUIDs from external_inputs.json
    param_guids = {
        '4a6b02a6-3501-43c9-b450-fbba3759cd55': ('a6b98c27-e4dd-405e-93f5-755c12294748', 'X coordinate'),
        'c4d9428f-dd29-4a16-bad2-de57930939bf': ('a6b98c27-e4dd-405e-93f5-755c12294748', 'Y coordinate'),
        '6c448807-c177-4d0c-9ec7-076f700a48ee': ('a6b98c27-e4dd-405e-93f5-755c12294748', 'Z coordinate'),
        '760ab637-afff-4339-9907-16307d9ba82a': ('577ce3f3-2b5e-4a55-ae60-c5c3c6c12e3c', 'X coordinate'),
        '75d9495d-5576-4d02-ae6c-acbdc71ec7d6': ('577ce3f3-2b5e-4a55-ae60-c5c3c6c12e3c', 'Y coordinate'),
        '94f511a2-f54e-45a3-a270-40e694999caa': ('577ce3f3-2b5e-4a55-ae60-c5c3c6c12e3c', 'Z coordinate'),
        '3123e48f-57be-4ba1-874d-f7d477453176': ('57648120-f088-4498-99d0-f8f7f3b69b89', 'X coordinate'),
    }
    
    updates = {}
    
    # Find all Object chunks
    for obj_chunk in root.findall('.//chunk[@name="Object"]'):
        container = obj_chunk.find('.//chunk[@name="Container"]')
        if container is None:
            continue
        
        instance_guid_elem = container.find('.//item[@name="InstanceGuid"]')
        if instance_guid_elem is None:
            continue
        
        instance_guid = instance_guid_elem.text
        
        # Check if this is a Construct Point we're interested in
        if instance_guid in construct_point_guids:
            print(f"\nFound Construct Point {instance_guid[:8]}... ({construct_point_guids[instance_guid]}):")
            
            # Check all param_input chunks
            for param_input in container.findall('.//chunk[@name="param_input"]'):
                param_guid_elem = param_input.find('.//item[@name="InstanceGuid"]')
                if param_guid_elem is None:
                    continue
                
                param_guid = param_guid_elem.text
                param_name_elem = param_input.find('.//item[@name="Name"]')
                param_name = param_name_elem.text if param_name_elem is not None else 'Unknown'
                
                # Check if this parameter is in our list
                if param_guid in param_guids:
                    expected_comp, expected_param = param_guids[param_guid]
                    if expected_comp == instance_guid and expected_param == param_name:
                        # Check for PersistentData
                        persistent_data = param_input.find('.//chunk[@name="PersistentData"]')
                        if persistent_data is not None:
                            # GH PersistentData structure: PersistentData/Branch/Item/item[@name="number"]
                            for branch in persistent_data.findall('.//chunk[@name="Branch"]'):
                                for item_chunk in branch.findall('.//chunk[@name="Item"]'):
                                    number_elem = item_chunk.find('.//item[@name="number"]')
                                    if number_elem is not None and number_elem.text:
                                        try:
                                            value = float(number_elem.text.strip())
                                            updates[param_guid] = value
                                            print(f"  {param_name} ({param_guid[:8]}...): {value}")
                                        except (ValueError, TypeError):
                                            pass
    
    return updates

if __name__ == '__main__':
    print("Extracting Construct Point PersistentData values...")
    updates = extract_construct_point_persistent_data()
    
    # Load existing external_inputs.json
    with open('external_inputs.json', 'r') as f:
        external_inputs = json.load(f)
    
    # Update values
    for param_guid, value in updates.items():
        if param_guid in external_inputs:
            external_inputs[param_guid]['value'] = value
            print(f"\nUpdated {param_guid[:8]}...: {value}")
    
    # Save
    with open('external_inputs.json', 'w') as f:
        json.dump(external_inputs, f, indent=2)
    
    print(f"\n[OK] Updated {len(updates)} Construct Point values")

