"""
Extract the Division component f9a68fee... and its dependencies from GHX file.
This component is outside the Rotatingslats group but is needed by a Panel.
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
    
    # Get Container data
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
            # Use index to distinguish multiple params with same name
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
            
            # Also extract PersistentData for constant values
            persistent_data = param_chunk.find(".//chunk[@name='PersistentData']")
            persistent_values = []
            if persistent_data is not None:
                for branch in persistent_data.findall(".//chunk[@name='Branch']"):
                    for item_chunk in branch.findall(".//chunk[@name='Item']"):
                        for item in item_chunk.findall(".//item"):
                            item_name = item.get("name")
                            if item_name in ["number", "value", "data"]:
                                persistent_values.append(item.text)
            
            if persistent_values:
                param_data['persistent_values'] = persistent_values
            
            if param_data:
                params[param_key] = {'data': param_data}
    
    return {
        'guid': obj_guid,
        'name': obj_name,
        'nickname': obj_nickname,
        'instance_guid': instance_guid,
        'type': 'component',
        'params': params
    }

if __name__ == "__main__":
    division_guid = "f9a68fee-bd6c-477a-9d8e-ae9e35697ab1"
    
    print(f"Extracting Division component {division_guid[:8]}...")
    comp_data = extract_component_from_ghx("core-only_fixed.ghx", division_guid)
    
    if comp_data:
        print(f"Found component: {comp_data['name']} '{comp_data['nickname']}'")
        print(f"  InstanceGuid: {comp_data['instance_guid']}")
        print(f"  Parameters: {list(comp_data['params'].keys())}")
        
        # Extract input sources
        print("\nInput sources:")
        for param_key, param_info in comp_data['params'].items():
            if param_key.startswith('param_input'):
                param_data = param_info.get('data', {})
                sources = param_data.get('Source', [])
                if sources:
                    print(f"  {param_data.get('Name')}: {sources}")
        
        # Save to JSON
        with open('external_division_component.json', 'w') as f:
            json.dump(comp_data, f, indent=2)
        print("\nSaved to external_division_component.json")
    else:
        print("Component not found!")

