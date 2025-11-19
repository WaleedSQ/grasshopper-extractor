"""
Extract Vector components needed for Move component Motion input.
These components produce output parameters d0668a07... and f5598672...
"""
import xml.etree.ElementTree as ET
import json
from parse_ghx_v2 import parse_ghx

def extract_component_from_ghx(ghx_file: str, instance_guid: str):
    """Extract a specific component by InstanceGuid from GHX file."""
    tree = ET.parse(ghx_file)
    root = tree.getroot()
    
    # Find the Definition chunk
    definition = root.find(".//chunk[@name='Definition']")
    if definition is None:
        raise ValueError("No Definition chunk found")
    
    # Find the component by InstanceGuid
    def_objects = definition.find(".//chunk[@name='DefinitionObjects']")
    if def_objects is None:
        return None
    
    # Search for the component
    for obj_chunk in def_objects.findall(".//chunk[@name='Object']"):
        # Look for InstanceGuid in Container items
        container = obj_chunk.find(".//chunk[@name='Container']")
        if container is not None:
            items = container.find("./items")
            if items is not None:
                for item in items.findall("./item"):
                    if item.get("name") == "InstanceGuid" and item.text == instance_guid:
                        # Found it! Now extract the component data
                        return extract_component_data(obj_chunk)
    
    return None

def extract_component_data(obj_chunk):
    """Extract component data from an Object chunk."""
    obj_guid = None
    obj_name = None
    obj_nickname = None
    instance_guid = None
    params = {}
    
    # Get GUID and name from top level
    items_elem = obj_chunk.find("./items")
    if items_elem is not None:
        for item in items_elem.findall("./item"):
            name = item.get("name")
            if name == "GUID":
                obj_guid = item.text
            elif name == "Name":
                obj_name = item.text
    
    # Get Container chunk
    container = obj_chunk.find(".//chunk[@name='Container']")
    if container is not None:
        items = container.find("./items")
        if items is not None:
            for item in items.findall("./item"):
                name = item.get("name")
                if name == "InstanceGuid":
                    instance_guid = item.text
                elif name == "Name":
                    obj_name = item.text
                elif name == "NickName":
                    obj_nickname = item.text
        
        # Extract parameters
        for param_chunk in container.findall(".//chunk"):
            param_name = param_chunk.get("name")
            if not param_name or not param_name.startswith('param_'):
                continue
            param_index = param_chunk.get("index")
            param_key = f"{param_name}_{param_index}" if param_index is not None else param_name
            param_data = {}
            param_items = param_chunk.find("./items")
            if param_items is not None:
                for item in param_items.findall("./item"):
                    item_name = item.get("name")
                    if item_name == "InstanceGuid":
                        param_data['InstanceGuid'] = item.text
                    elif item_name == "Name":
                        param_data['Name'] = item.text
                    elif item_name == "NickName":
                        param_data['NickName'] = item.text
                    elif item_name == "Source":
                        # Source is a list of GUIDs
                        sources = []
                        for source_item in param_items.findall(f"./item[@name='Source']"):
                            sources.append(source_item.text)
                        param_data['Source'] = sources
                    elif item_name == "SourceCount":
                        param_data['SourceCount'] = int(item.text) if item.text else 0
                    else:
                        param_data[item_name] = item.text
                
                # Store in data dict
                param_data_dict = {'data': param_data}
                
                # Extract PersistentData for constant values
                persistent_data = param_chunk.find(".//chunk[@name='PersistentData']")
                persistent_values = []
                if persistent_data is not None:
                    for branch in persistent_data.findall(".//chunk[@name='Branch']"):
                        for item_chunk in branch.findall(".//chunk[@name='Item']"):
                            item_items = item_chunk.find("./items")
                            if item_items is not None:
                                for item in item_items.findall("./item"):
                                    if item.text:
                                        persistent_values.append(item.text)
                
                param_data_dict['persistent_values'] = persistent_values
                param_data_dict['values'] = []
                param_data_dict['sources'] = []
                param_data_dict['source_params'] = []
                
                # Convert Source list to sources format
                if 'Source' in param_data:
                    for idx, source_guid in enumerate(param_data['Source']):
                        param_data_dict['sources'].append({
                            'guid': source_guid,
                            'index': idx
                        })
                    del param_data['Source']
                
                params[param_key] = param_data_dict
    
    return {
        'guid': obj_guid,
        'name': obj_name,
        'type': obj_name,  # Use name as type
        'nickname': obj_nickname or '',
        'instance_guid': instance_guid,
        'params': params
    }

if __name__ == '__main__':
    # Extract Vector XYZ component (produces f5598672...)
    vector_xyz_guid = '0e4c5858-a163-486c-b7b2-57d2cbb41dc0'
    print(f"Extracting Vector XYZ component {vector_xyz_guid[:8]}...")
    vector_xyz = extract_component_from_ghx('core-only_fixed.ghx', vector_xyz_guid)
    
    if vector_xyz:
        with open('external_vector_xyz_component.json', 'w') as f:
            json.dump(vector_xyz, f, indent=2)
        print(f"Saved Vector XYZ component to external_vector_xyz_component.json")
        print(f"  Type: {vector_xyz.get('type')}")
        print(f"  Nickname: {vector_xyz.get('nickname')}")
        print(f"  Output param: {vector_xyz['params'].get('param_output_0', {}).get('data', {}).get('InstanceGuid', 'N/A')[:8]}...")
    else:
        print(f"Could not find Vector XYZ component")
    
    # Find the other Vector component that produces d0668a07...
    # Search for output parameter d0668a07...
    print(f"\nSearching for component with output param d0668a07...")
    tree = ET.parse('core-only_fixed.ghx')
    root = tree.getroot()
    definition = root.find(".//chunk[@name='Definition']")
    def_objects = definition.find(".//chunk[@name='DefinitionObjects']")
    
    target_output_param = 'd0668a07-838c-481c-88eb-191574362cc2'
    found_component = None
    
    for obj_chunk in def_objects.findall(".//chunk[@name='Object']"):
        container = obj_chunk.find(".//chunk[@name='Container']")
        if container is not None:
            # Check all param_output chunks
            for param_output in container.findall(".//chunk[@name='param_output']"):
                items = param_output.find("./items")
                if items is not None:
                    for item in items.findall("./item"):
                        if item.get("name") == "InstanceGuid" and item.text == target_output_param:
                            # Found the component!
                            instance_guid_elem = container.find("./items/item[@name='InstanceGuid']")
                            if instance_guid_elem is not None:
                                comp_instance_guid = instance_guid_elem.text
                                found_component = extract_component_from_ghx('core-only_fixed.ghx', comp_instance_guid)
                                break
                if found_component:
                    break
        if found_component:
            break
    
    if found_component:
        with open('external_vector_d0668a07_component.json', 'w') as f:
            json.dump(found_component, f, indent=2)
        print(f"Saved component to external_vector_d0668a07_component.json")
        print(f"  Type: {found_component.get('type')}")
        print(f"  Nickname: {found_component.get('nickname')}")
        print(f"  Instance GUID: {found_component.get('instance_guid')[:8]}...")
    else:
        print(f"Could not find component with output param d0668a07...")
    
    # Also extract Vector 2Pt component that produces 84214afe...
    vector_2pt_guid = '1f794702-1a6b-441e-b41d-c4749b372177'
    print(f"\nExtracting Vector 2Pt component {vector_2pt_guid[:8]}...")
    vector_2pt = extract_component_from_ghx('core-only_fixed.ghx', vector_2pt_guid)
    
    if vector_2pt:
        with open('external_vector_2pt_1f794702_component.json', 'w') as f:
            json.dump(vector_2pt, f, indent=2)
        print(f"Saved Vector 2Pt component to external_vector_2pt_1f794702_component.json")
        print(f"  Type: {vector_2pt.get('type')}")
        print(f"  Nickname: {vector_2pt.get('nickname')}")
        print(f"  Output param: {vector_2pt['params'].get('param_output_0', {}).get('data', {}).get('InstanceGuid', 'N/A')[:8]}...")
    else:
        print(f"Could not find Vector 2Pt component")
    
    # Also extract Mirror component that produces db399c50...
    mirror_guid = '47650d42-5fa9-44b3-b970-9f28b94bb031'
    print(f"\nExtracting Mirror component {mirror_guid[:8]}...")
    mirror = extract_component_from_ghx('core-only_fixed.ghx', mirror_guid)
    
    if mirror:
        with open('external_mirror_component.json', 'w') as f:
            json.dump(mirror, f, indent=2)
        print(f"Saved Mirror component to external_mirror_component.json")
        print(f"  Type: {mirror.get('type')}")
        print(f"  Nickname: {mirror.get('nickname')}")
        output_param_guid = mirror['params'].get('param_output_0', {}).get('data', {}).get('InstanceGuid', 'N/A')
        print(f"  Output param: {output_param_guid[:8] if output_param_guid != 'N/A' else 'N/A'}...")
    else:
        print(f"Could not find Mirror component")

