"""
PHASE 2: Rotatingslats Group Isolation
Extract the subgraph containing all components inside the Rotatingslats group.
"""

import json


def isolate_rotatingslats():
    """Extract Rotatingslats subgraph from the full component graph."""
    
    print("=" * 80)
    print("PHASE 2: ROTATINGSLATS GROUP ISOLATION")
    print("=" * 80)
    print()
    
    # Load the full graph
    with open('ghx_graph.json', 'r') as f:
        graph = json.load(f)
    
    components = graph['components']
    wires = graph['wires']
    
    # Find the Rotatingslats group
    rotatingslats_guid = 'a310b28b-ac76-4228-8c67-f796bf6ee11f'
    rotatingslats_group = None
    
    for comp in components:
        if comp['guid'] == rotatingslats_guid:
            rotatingslats_group = comp
            break
    
    if not rotatingslats_group:
        print("ERROR: Rotatingslats group not found!")
        return
    
    print(f"Found Rotatingslats group: {rotatingslats_group['nickname']}")
    print(f"  GUID: {rotatingslats_group['guid']}")
    print()
    
    # The Group component doesn't have a list of member GUIDs in our current parsing
    # We need to extract this from the GHX file
    # Groups in GHX have an "ID" array containing all member component GUIDs
    
    # Re-parse just the group to get member IDs
    import xml.etree.ElementTree as ET
    tree = ET.parse('refactored-no-sun.ghx')
    root = tree.getroot()
    
    member_guids = []
    
    # Find Definition > DefinitionObjects > Group chunks
    definition = None
    for chunk in root.findall('.//chunk'):
        if chunk.get('name') == 'Definition':
            definition = chunk
            break
    
    if definition:
        for chunk in definition.findall('.//chunk'):
            if chunk.get('name') == 'DefinitionObjects':
                for obj_chunk in chunk.findall('./chunks/chunk'):
                    if obj_chunk.get('name') == 'Object':
                        # Check if this Object is a Group
                        obj_items = obj_chunk.find('./items')
                        if obj_items is not None:
                            obj_name = None
                            for item in obj_items.findall('./item'):
                                if item.get('name') == 'Name':
                                    obj_name = item.text.strip() if item.text else ''
                                    break
                            
                            if obj_name == 'Group':
                                # Find the Container chunk
                                container_chunk = None
                                for sub_chunk in obj_chunk.findall('./chunks/chunk'):
                                    if sub_chunk.get('name') == 'Container':
                                        container_chunk = sub_chunk
                                        break
                                
                                if container_chunk is not None:
                                    # Check if this is our Rotatingslats group
                                    container_items = container_chunk.find('./items')
                                    if container_items is not None:
                                        instance_guid = None
                                        for item in container_items.findall('./item'):
                                            if item.get('name') == 'InstanceGuid':
                                                instance_guid = item.text.strip() if item.text else ''
                                                break
                                        
                                        if instance_guid == rotatingslats_guid:
                                            # Extract all ID items
                                            for item in container_items.findall('./item'):
                                                if item.get('name') == 'ID':
                                                    guid = item.text.strip() if item.text else ''
                                                    if guid:
                                                        member_guids.append(guid)
                                            break
    
    print(f"Found {len(member_guids)} components inside Rotatingslats group")
    print()
    
    # Extract subgraph: all components that are members of Rotatingslats
    rotatingslats_components = []
    for comp in components:
        if comp['guid'] in member_guids:
            rotatingslats_components.append(comp)
    
    # Build mapping of parameter GUID -> component GUID
    param_to_component = {}
    for comp in components:
        comp_guid = comp['guid']
        for param in comp['params']:
            param_guid = param['param_guid']
            param_to_component[param_guid] = comp_guid
    
    # Extract wires that connect components within the group
    # Resolve wires by looking up which component owns each parameter
    # Also include external inputs (wires coming FROM outside TO inside)
    rotatingslats_wires = []
    external_inputs = []
    
    for wire in wires:
        from_param_guid = wire['from_component']  # This is actually a parameter GUID
        to_comp_guid = wire['to_component']        # This is a component GUID
        
        # Look up the component that owns the from parameter
        from_comp_guid = param_to_component.get(from_param_guid, from_param_guid)
        
        from_inside = from_comp_guid in member_guids
        to_inside = to_comp_guid in member_guids
        
        # Create corrected wire with resolved component GUID
        corrected_wire = {
            'from_component': from_comp_guid,
            'from_param': wire['from_param'],
            'to_component': wire['to_component'],
            'to_param': wire['to_param'],
            'to_param_name': wire['to_param_name']
        }
        
        if from_inside and to_inside:
            # Internal wire
            rotatingslats_wires.append(corrected_wire)
        elif not from_inside and to_inside:
            # External input wire
            external_inputs.append(corrected_wire)
    
    print(f"Extracted subgraph:")
    print(f"  Components: {len(rotatingslats_components)}")
    print(f"  Internal wires: {len(rotatingslats_wires)}")
    print(f"  External inputs: {len(external_inputs)}")
    print()
    
    # Identify component types in the subgraph
    type_counts = {}
    for comp in rotatingslats_components:
        type_name = comp['type_name']
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    print("Component types in Rotatingslats:")
    for type_name, count in sorted(type_counts.items()):
        print(f"  {type_name}: {count}")
    print()
    
    # Identify external input sources
    external_source_guids = set()
    for wire in external_inputs:
        external_source_guids.add(wire['from_component'])
    
    print(f"External input sources: {len(external_source_guids)}")
    for source_guid in external_source_guids:
        # Find the component
        source_comp = None
        for comp in components:
            if comp['guid'] == source_guid:
                source_comp = comp
                break
        if source_comp:
            print(f"  {source_comp['type_name']}: {source_comp['nickname']}")
    print()
    
    # Extract persistent data from external inputs (sliders, panels, etc.)
    rotatingslats_inputs = {}
    
    for source_guid in external_source_guids:
        source_comp = None
        for comp in components:
            if comp['guid'] == source_guid:
                source_comp = comp
                break
        
        if source_comp:
            # Check if this component has persistent data
            has_data = False
            
            # First check parameters for persistent data
            for param in source_comp['params']:
                if param['persistent_data']:
                    has_data = True
                    rotatingslats_inputs[source_guid] = {
                        'guid': source_guid,
                        'type': source_comp['type_name'],
                        'nickname': source_comp['nickname'],
                        'data': param['persistent_data']
                    }
                    break
            
            # If no param data, check for Number Slider special handling
            if not has_data and source_comp['type_name'] == 'Number Slider':
                # Extract slider value from GHX directly
                import xml.etree.ElementTree as ET
                tree = ET.parse('refactored-no-sun.ghx')
                root = tree.getroot()
                
                # Find this slider in GHX
                for chunk in root.findall('.//chunk'):
                    if chunk.get('name') == 'Object':
                        obj_items = chunk.find('./items')
                        if obj_items is not None:
                            name_item = None
                            for item in obj_items.findall('./item'):
                                if item.get('name') == 'Name' and item.text and 'Number Slider' in item.text:
                                    name_item = item
                                    break
                            
                            if name_item is not None:
                                # Find Container chunk
                                for sub_chunk in chunk.findall('./chunks/chunk'):
                                    if sub_chunk.get('name') == 'Container':
                                        # Check if this is our slider
                                        container_items = sub_chunk.find('./items')
                                        if container_items is not None:
                                            instance_guid = None
                                            for item in container_items.findall('./item'):
                                                if item.get('name') == 'InstanceGuid':
                                                    instance_guid = item.text.strip() if item.text else ''
                                                    break
                                            
                                            if instance_guid == source_guid:
                                                # Found our slider - extract value from Slider chunk
                                                for slider_chunk in sub_chunk.findall('./chunks/chunk'):
                                                    if slider_chunk.get('name') == 'Slider':
                                                        slider_items = slider_chunk.find('./items')
                                                        if slider_items is not None:
                                                            for item in slider_items.findall('./item'):
                                                                if item.get('name') == 'Value':
                                                                    value = float(item.text) if item.text else 0
                                                                    rotatingslats_inputs[source_guid] = {
                                                                        'guid': source_guid,
                                                                        'type': source_comp['type_name'],
                                                                        'nickname': source_comp['nickname'],
                                                                        'data': [value]
                                                                    }
                                                                    has_data = True
                                                                    break
                                                break
                                break
            
            if not has_data:
                # No persistent data - might need to be provided manually
                rotatingslats_inputs[source_guid] = {
                    'guid': source_guid,
                    'type': source_comp['type_name'],
                    'nickname': source_comp['nickname'],
                    'data': None
                }
    
    # Save outputs
    rotatingslats_graph = {
        'group_guid': rotatingslats_guid,
        'components': rotatingslats_components,
        'internal_wires': rotatingslats_wires,
        'external_wires': external_inputs,
        'component_count': len(rotatingslats_components),
        'internal_wire_count': len(rotatingslats_wires),
        'external_wire_count': len(external_inputs)
    }
    
    with open('rotatingslats_graph.json', 'w') as f:
        json.dump(rotatingslats_graph, f, indent=2)
    print("[OK] Saved rotatingslats_graph.json")
    
    with open('rotatingslats_inputs.json', 'w') as f:
        json.dump(rotatingslats_inputs, f, indent=2)
    print("[OK] Saved rotatingslats_inputs.json")
    
    print()
    print("=" * 80)
    print("PHASE 2 COMPLETE")
    print("=" * 80)
    print()
    print("Ready for PHASE 3: DataTree engine and component dispatch")


if __name__ == '__main__':
    isolate_rotatingslats()

