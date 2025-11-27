"""
PHASE 2: Sun and Rotatingslats Group Isolation
Extract the subgraphs containing all components inside both groups.
"""

import json
import xml.etree.ElementTree as ET


def extract_group_members(ghx_path, group_guid):
    """Extract member GUIDs from a group in the GHX file."""
    tree = ET.parse(ghx_path)
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
                                    # Check if this is our target group
                                    container_items = container_chunk.find('./items')
                                    if container_items is not None:
                                        instance_guid = None
                                        for item in container_items.findall('./item'):
                                            if item.get('name') == 'InstanceGuid':
                                                instance_guid = item.text.strip() if item.text else ''
                                                break
                                        
                                        if instance_guid == group_guid:
                                            # Extract all ID items
                                            for item in container_items.findall('./item'):
                                                if item.get('name') == 'ID':
                                                    guid = item.text.strip() if item.text else ''
                                                    if guid:
                                                        member_guids.append(guid)
                                            break
    
    return member_guids


def isolate_both_groups():
    """Extract both Sun and Rotatingslats subgraphs from the full component graph."""
    
    print("=" * 80)
    print("PHASE 2: SUN AND ROTATINGSLATS GROUP ISOLATION")
    print("=" * 80)
    print()
    
    # Load the full graph
    with open('ghx_graph.json', 'r') as f:
        graph = json.load(f)
    
    components = graph['components']
    wires = graph['wires']
    
    # Find the groups
    sun_guid = 'bb0d5d5a-bc1e-46a9-9bba-42e32b20ca53'
    rotatingslats_guid = 'a310b28b-ac76-4228-8c67-f796bf6ee11f'
    
    sun_group = None
    rotatingslats_group = None
    
    for comp in components:
        if comp['guid'] == sun_guid:
            sun_group = comp
        elif comp['guid'] == rotatingslats_guid:
            rotatingslats_group = comp
    
    if not sun_group:
        print("ERROR: Sun group not found!")
        return
    if not rotatingslats_group:
        print("ERROR: Rotatingslats group not found!")
        return
    
    print(f"Found Sun group: {sun_group.get('nickname', 'N/A')}")
    print(f"  GUID: {sun_group['guid']}")
    print(f"Found Rotatingslats group: {rotatingslats_group.get('nickname', 'N/A')}")
    print(f"  GUID: {rotatingslats_group['guid']}")
    print()
    
    # Extract member GUIDs from GHX file
    ghx_path = 'refactored-sun.ghx'
    sun_member_guids = extract_group_members(ghx_path, sun_guid)
    rotatingslats_member_guids = extract_group_members(ghx_path, rotatingslats_guid)
    
    print(f"Found {len(sun_member_guids)} components inside Sun group")
    print(f"Found {len(rotatingslats_member_guids)} components inside Rotatingslats group")
    print()
    
    # Extract subgraphs
    sun_components = [c for c in components if c['guid'] in sun_member_guids]
    rotatingslats_components = [c for c in components if c['guid'] in rotatingslats_member_guids]
    
    # Build mapping of parameter GUID -> component GUID
    param_to_component = {}
    for comp in components:
        comp_guid = comp['guid']
        for param in comp['params']:
            param_guid = param['param_guid']
            param_to_component[param_guid] = comp_guid
    
    # Extract wires for each group
    all_member_guids = set(sun_member_guids + rotatingslats_member_guids)
    
    sun_wires = []
    rotatingslats_wires = []
    sun_external_inputs = []
    rotatingslats_external_inputs = []
    cross_group_wires = []  # Wires from Sun to Rotatingslats
    
    for wire in wires:
        from_param_guid = wire['from_component']  # This is actually a parameter GUID
        to_comp_guid = wire['to_component']        # This is a component GUID
        
        # Look up the component that owns the from parameter
        from_comp_guid = param_to_component.get(from_param_guid, from_param_guid)
        
        from_sun = from_comp_guid in sun_member_guids
        from_rotatingslats = from_comp_guid in rotatingslats_member_guids
        to_sun = to_comp_guid in sun_member_guids
        to_rotatingslats = to_comp_guid in rotatingslats_member_guids
        
        # Create corrected wire
        corrected_wire = {
            'from_component': from_comp_guid,
            'from_param': wire['from_param'],
            'to_component': wire['to_component'],
            'to_param': wire['to_param'],
            'to_param_name': wire['to_param_name']
        }
        
        if from_sun and to_sun:
            # Internal Sun wire
            sun_wires.append(corrected_wire)
        elif from_rotatingslats and to_rotatingslats:
            # Internal Rotatingslats wire
            rotatingslats_wires.append(corrected_wire)
        elif from_sun and to_rotatingslats:
            # Cross-group wire: Sun -> Rotatingslats
            cross_group_wires.append(corrected_wire)
            rotatingslats_external_inputs.append(corrected_wire)
        elif not from_sun and not from_rotatingslats and to_sun:
            # External input to Sun
            sun_external_inputs.append(corrected_wire)
        elif not from_sun and not from_rotatingslats and to_rotatingslats:
            # External input to Rotatingslats
            rotatingslats_external_inputs.append(corrected_wire)
    
    print(f"Sun group:")
    print(f"  Components: {len(sun_components)}")
    print(f"  Internal wires: {len(sun_wires)}")
    print(f"  External inputs: {len(sun_external_inputs)}")
    print()
    print(f"Rotatingslats group:")
    print(f"  Components: {len(rotatingslats_components)}")
    print(f"  Internal wires: {len(rotatingslats_wires)}")
    print(f"  External inputs: {len(rotatingslats_external_inputs)}")
    print(f"  Cross-group wires (from Sun): {len(cross_group_wires)}")
    print()
    
    # Identify component types
    print("Sun group component types:")
    sun_type_counts = {}
    for comp in sun_components:
        type_name = comp['type_name']
        sun_type_counts[type_name] = sun_type_counts.get(type_name, 0) + 1
    for type_name, count in sorted(sun_type_counts.items()):
        print(f"  {type_name}: {count}")
    print()
    
    # Extract external input data (sliders, panels, etc.)
    def extract_external_inputs(external_wires, member_guids):
        external_source_guids = set()
        for wire in external_wires:
            external_source_guids.add(wire['from_component'])
        
        inputs = {}
        for source_guid in external_source_guids:
            # Skip if this component is inside the group (it's internal, not external)
            if source_guid in member_guids:
                continue
            
            source_comp = None
            for comp in components:
                if comp['guid'] == source_guid:
                    source_comp = comp
                    break
            
            if source_comp:
                # Only include data source components (sliders, panels, etc.), not computation components
                # Exclude: Division, Explode Tree, and other computation components
                excluded_types = {'Division', 'Explode Tree', 'Subtraction', 'Addition', 'Multiplication', 
                                 'Angle', 'Area', 'Line', 'Move', 'Rotate', 'Construct Point', 'Construct Plane'}
                
                if source_comp['type_name'] in excluded_types:
                    continue  # Skip computation components
                
                # Check for persistent data
                has_data = False
                for param in source_comp['params']:
                    if param['persistent_data']:
                        has_data = True
                        inputs[source_guid] = {
                            'guid': source_guid,
                            'type': source_comp['type_name'],
                            'nickname': source_comp['nickname'],
                            'data': param['persistent_data']
                        }
                        break
                
                # Special handling for Number Slider
                if not has_data and source_comp['type_name'] == 'Number Slider':
                    tree = ET.parse(ghx_path)
                    root = tree.getroot()
                    
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
                                    for sub_chunk in chunk.findall('./chunks/chunk'):
                                        if sub_chunk.get('name') == 'Container':
                                            container_items = sub_chunk.find('./items')
                                            if container_items is not None:
                                                instance_guid = None
                                                for item in container_items.findall('./item'):
                                                    if item.get('name') == 'InstanceGuid':
                                                        instance_guid = item.text.strip() if item.text else ''
                                                        break
                                                
                                                if instance_guid == source_guid:
                                                    for slider_chunk in sub_chunk.findall('./chunks/chunk'):
                                                        if slider_chunk.get('name') == 'Slider':
                                                            slider_items = slider_chunk.find('./items')
                                                            if slider_items is not None:
                                                                for item in slider_items.findall('./item'):
                                                                    if item.get('name') == 'Value':
                                                                        value = float(item.text) if item.text else 0
                                                                        inputs[source_guid] = {
                                                                            'guid': source_guid,
                                                                            'type': source_comp['type_name'],
                                                                            'nickname': source_comp['nickname'],
                                                                            'data': [value]
                                                                        }
                                                                        has_data = True
                                                                        break
                                                    break
                                break
                
                # Only add to inputs if it's a data source component (has persistent data or is a slider/panel)
                # Don't add computation components even if they have no data
                if not has_data and source_comp['type_name'] in {'Number Slider', 'Panel', 'Value List'}:
                    inputs[source_guid] = {
                        'guid': source_guid,
                        'type': source_comp['type_name'],
                        'nickname': source_comp['nickname'],
                        'data': None
                    }
        
        return inputs
    
    sun_inputs = extract_external_inputs(sun_external_inputs, sun_member_guids)
    rotatingslats_inputs = extract_external_inputs(rotatingslats_external_inputs, rotatingslats_member_guids)
    
    # Save outputs
    sun_graph = {
        'group_guid': sun_guid,
        'components': sun_components,
        'internal_wires': sun_wires,
        'external_wires': sun_external_inputs,
        'component_count': len(sun_components),
        'internal_wire_count': len(sun_wires),
        'external_wire_count': len(sun_external_inputs)
    }
    
    rotatingslats_graph = {
        'group_guid': rotatingslats_guid,
        'components': rotatingslats_components,
        'internal_wires': rotatingslats_wires,
        'external_wires': rotatingslats_external_inputs,
        'cross_group_wires': cross_group_wires,
        'component_count': len(rotatingslats_components),
        'internal_wire_count': len(rotatingslats_wires),
        'external_wire_count': len(rotatingslats_external_inputs),
        'cross_group_wire_count': len(cross_group_wires)
    }
    
    with open('sun_group_graph.json', 'w') as f:
        json.dump(sun_graph, f, indent=2)
    print("[OK] Saved sun_group_graph.json")
    
    with open('rotatingslats_graph.json', 'w') as f:
        json.dump(rotatingslats_graph, f, indent=2)
    print("[OK] Saved rotatingslats_graph.json")
    
    with open('sun_group_inputs.json', 'w') as f:
        json.dump(sun_inputs, f, indent=2)
    print("[OK] Saved sun_group_inputs.json")
    
    with open('rotatingslats_inputs.json', 'w') as f:
        json.dump(rotatingslats_inputs, f, indent=2)
    print("[OK] Saved rotatingslats_inputs.json")
    
    # Save cross-group wire info
    cross_group_info = {
        'wires': cross_group_wires,
        'count': len(cross_group_wires)
    }
    with open('cross_group_wires.json', 'w') as f:
        json.dump(cross_group_info, f, indent=2)
    print("[OK] Saved cross_group_wires.json")
    
    print()
    print("=" * 80)
    print("PHASE 2 COMPLETE")
    print("=" * 80)
    print()
    print("Ready for PHASE 3: Component implementation and evaluation")


if __name__ == '__main__':
    isolate_both_groups()

