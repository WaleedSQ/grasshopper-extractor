"""
Comprehensive extraction of all external input values from GHX file.
Extracts PersistentData, traces wired sources, and extracts geometry data.
"""
import xml.etree.ElementTree as ET
import json
import sys

def find_component_by_guid(root, guid):
    """Find a component by its instance GUID."""
    for obj_chunk in root.findall('.//chunk[@name="Object"]'):
        container = obj_chunk.find('.//chunk[@name="Container"]')
        if container is None:
            continue
        instance_guid_elem = container.find('.//item[@name="InstanceGuid"]')
        if instance_guid_elem is not None and instance_guid_elem.text == guid:
            return container
    return None

def find_output_param_by_guid(root, output_guid):
    """Find an output parameter by its GUID and return its parent component."""
    for obj_chunk in root.findall('.//chunk[@name="Object"]'):
        container = obj_chunk.find('.//chunk[@name="Container"]')
        if container is None:
            continue
        
        # Check param_output chunks
        for param_output in container.findall('.//chunk[@name="param_output"]'):
            output_guid_elem = param_output.find('.//item[@name="InstanceGuid"]')
            if output_guid_elem is not None and output_guid_elem.text == output_guid:
                instance_guid_elem = container.find('.//item[@name="InstanceGuid"]')
                if instance_guid_elem is not None:
                    return {
                        'container': container,
                        'parent_guid': instance_guid_elem.text,
                        'param_output': param_output
                    }
    return None

def extract_persistent_data(container, param_key=None):
    """Extract PersistentData from a container or specific parameter."""
    if param_key:
        # Look in specific param_input or param_output
        for param_chunk in container.findall(f'.//chunk[@name="{param_key}"]'):
            persistent_data = param_chunk.find('.//chunk[@name="PersistentData"]')
            if persistent_data is not None:
                return persistent_data
    else:
        # Look in Container-level PersistentData
        persistent_data = container.find('.//chunk[@name="PersistentData"]')
        if persistent_data is not None:
            return persistent_data
    
    return None

def extract_plane_from_persistent_data(persistent_data):
    """Extract plane from PersistentData (gh_plane type).
    Structure: PersistentData/Branch/Item/item[@name="plane"]/Ox, Oy, Oz, Xx, Xy, Xz, Yx, Yy, Yz"""
    for branch in persistent_data.findall('.//chunk[@name="Branch"]'):
        for item_chunk in branch.findall('.//chunk[@name="Item"]'):
            plane_elem = item_chunk.find('.//item[@name="plane"]')
            if plane_elem is not None:
                # Extract origin (Ox, Oy, Oz)
                ox_elem = plane_elem.find('Ox')
                oy_elem = plane_elem.find('Oy')
                oz_elem = plane_elem.find('Oz')
                # Extract X-axis (Xx, Xy, Xz)
                xx_elem = plane_elem.find('Xx')
                xy_elem = plane_elem.find('Xy')
                xz_elem = plane_elem.find('Xz')
                # Extract Y-axis (Yx, Yy, Yz)
                yx_elem = plane_elem.find('Yx')
                yy_elem = plane_elem.find('Yy')
                yz_elem = plane_elem.find('Yz')
                
                if all(elem is not None for elem in [ox_elem, oy_elem, oz_elem, 
                                                      xx_elem, xy_elem, xz_elem,
                                                      yx_elem, yy_elem, yz_elem]):
                    try:
                        origin = [float(ox_elem.text), float(oy_elem.text), float(oz_elem.text)]
                        x_axis = [float(xx_elem.text), float(xy_elem.text), float(xz_elem.text)]
                        y_axis = [float(yx_elem.text), float(yy_elem.text), float(yz_elem.text)]
                        # Calculate Z-axis (normal) as cross product of X and Y
                        # Z = X × Y
                        z_axis = [
                            x_axis[1] * y_axis[2] - x_axis[2] * y_axis[1],
                            x_axis[2] * y_axis[0] - x_axis[0] * y_axis[2],
                            x_axis[0] * y_axis[1] - x_axis[1] * y_axis[0]
                        ]
                        return {
                            'origin': origin,
                            'x_axis': x_axis,
                            'y_axis': y_axis,
                            'z_axis': z_axis,
                            'normal': z_axis
                        }
                    except (ValueError, TypeError):
                        pass
    return None

def extract_point_from_persistent_data(persistent_data):
    """Extract point coordinates from PersistentData.
    Handles both 'Coordinate' and 'vector' (gh_point3d) items."""
    # Try Coordinate first (for Point components)
    coord_elem = persistent_data.find('.//item[@name="Coordinate"]')
    if coord_elem is not None:
        x_elem = coord_elem.find('X')
        y_elem = coord_elem.find('Y')
        z_elem = coord_elem.find('Z')
        if x_elem is not None and y_elem is not None and z_elem is not None:
            try:
                x = float(x_elem.text)
                y = float(y_elem.text)
                z = float(z_elem.text)
                return [x, y, z]
            except (ValueError, TypeError):
                pass
    
    # Try vector (gh_point3d) - for Move component Motion input
    # Structure: PersistentData/Branch/Item/item[@name="vector"]/X, Y, Z
    for branch in persistent_data.findall('.//chunk[@name="Branch"]'):
        for item_chunk in branch.findall('.//chunk[@name="Item"]'):
            vector_elem = item_chunk.find('.//item[@name="vector"]')
            if vector_elem is not None:
                x_elem = vector_elem.find('X')
                y_elem = vector_elem.find('Y')
                z_elem = vector_elem.find('Z')
                if x_elem is not None and y_elem is not None and z_elem is not None:
                    try:
                        x = float(x_elem.text)
                        y = float(y_elem.text)
                        z = float(z_elem.text)
                        return [x, y, z]
                    except (ValueError, TypeError):
                        pass
    
    return None

def extract_value_from_persistent_data(persistent_data):
    """Extract a numeric or string value from PersistentData."""
    # GH PersistentData structure: PersistentData/Branch/Item/item[@name="number"]
    # Try to find value in Branch/Item structure first
    for branch in persistent_data.findall('.//chunk[@name="Branch"]'):
        for item_chunk in branch.findall('.//chunk[@name="Item"]'):
            # Check for "number" item (gh_double)
            number_elem = item_chunk.find('.//item[@name="number"]')
            if number_elem is not None and number_elem.text:
                try:
                    return float(number_elem.text.strip())
                except (ValueError, TypeError):
                    pass
            
            # Check for "integer" item (gh_int32)
            integer_elem = item_chunk.find('.//item[@name="integer"]')
            if integer_elem is not None and integer_elem.text:
                try:
                    return int(integer_elem.text.strip())
                except (ValueError, TypeError):
                    pass
    
    # Try different item names at top level
    for item_name in ['Value', 'Expression', 'Text', 'Number']:
        value_elem = persistent_data.find(f'.//item[@name="{item_name}"]')
        if value_elem is not None and value_elem.text:
            text = value_elem.text.strip()
            if text and text not in ['', '\n                                      ']:
                # Try to convert to number
                try:
                    if '.' in text:
                        return float(text)
                    else:
                        return int(text)
                except ValueError:
                    # Return as string
                    return text
    return None

def trace_source_value(root, source_guid):
    """Trace a source GUID to find its value."""
    # First check if it's an output parameter
    output_info = find_output_param_by_guid(root, source_guid)
    if output_info:
        # Check PersistentData in the output parameter
        persistent_data = extract_persistent_data(output_info['param_output'])
        if persistent_data:
            # Try to extract point
            point = extract_point_from_persistent_data(persistent_data)
            if point:
                return point
            # Try to extract value
            value = extract_value_from_persistent_data(persistent_data)
            if value is not None:
                return value
        
        # Check parent component's PersistentData
        container = output_info['container']
        persistent_data = extract_persistent_data(container)
        if persistent_data:
            point = extract_point_from_persistent_data(persistent_data)
            if point:
                return point
            value = extract_value_from_persistent_data(persistent_data)
            if value is not None:
                return value
    
    # Check if it's a component instance GUID
    container = find_component_by_guid(root, source_guid)
    if container:
        persistent_data = extract_persistent_data(container)
        if persistent_data:
            point = extract_point_from_persistent_data(persistent_data)
            if point:
                return point
            value = extract_value_from_persistent_data(persistent_data)
            if value is not None:
                return value
    
    return None

def parse_ghx_for_all_external_inputs(ghx_file='core-only_fixed.ghx'):
    """Extract all external input values from GHX."""
    
    tree = ET.parse(ghx_file)
    root = tree.getroot()
    
    external_inputs = {}
    
    # Load existing external_inputs.json to preserve structure
    try:
        with open('external_inputs.json', 'r') as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = {}
    
    print("Extracting all external input values from GHX...")
    print("=" * 60)
    
    # Process all entries in existing external_inputs.json
    for guid, info in existing.items():
        if not isinstance(info, dict):
            continue
        
        value = info.get('value')
        object_guid = info.get('object_guid', guid)
        object_type = info.get('object_type') or info.get('type', 'Unknown')
        
        # Skip if already has a real value (not None, not empty string, not placeholder)
        if value is not None:
            if isinstance(value, (int, float, list)):
                continue
            if isinstance(value, str) and value.strip() and value.strip() != '\n                                      ':
                continue
        
        print(f"\nProcessing {object_type} ({guid[:8]}...):")
        
        # Find the component in GHX
        container = find_component_by_guid(root, object_guid)
        if container is None:
            # Try finding by output parameter GUID
            output_info = find_output_param_by_guid(root, guid)
            if output_info:
                container = output_info['container']
                object_guid = output_info['parent_guid']
        
        if container is None:
            print(f"  [SKIP] Component not found in GHX")
            continue
        
        # Check for PersistentData
        persistent_data = extract_persistent_data(container)
        if persistent_data:
            # Try to extract point
            point = extract_point_from_persistent_data(persistent_data)
            if point:
                external_inputs[guid] = info.copy()
                external_inputs[guid]['value'] = point
                print(f"  [OK] Extracted point: {point}")
                continue
            
            # Try to extract value
            value = extract_value_from_persistent_data(persistent_data)
            if value is not None:
                external_inputs[guid] = info.copy()
                external_inputs[guid]['value'] = value
                print(f"  [OK] Extracted value: {value}")
                continue
        
        # Check for Source connection
        source_elem = container.find('.//item[@name="Source"]')
        if source_elem is not None:
            source_guid = source_elem.text
            print(f"  [TRACE] Has Source: {source_guid[:8]}...")
            traced_value = trace_source_value(root, source_guid)
            if traced_value is not None:
                external_inputs[guid] = info.copy()
                external_inputs[guid]['value'] = traced_value
                external_inputs[guid]['source_guid'] = source_guid
                print(f"  [OK] Traced source value: {traced_value}")
                continue
        
        # Check param_input chunks for PersistentData
        for param_input in container.findall('.//chunk[@name="param_input"]'):
            param_guid_elem = param_input.find('.//item[@name="InstanceGuid"]')
            if param_guid_elem is not None and param_guid_elem.text == guid:
                persistent_data = extract_persistent_data(param_input)
                if persistent_data:
                    point = extract_point_from_persistent_data(persistent_data)
                    if point:
                        external_inputs[guid] = info.copy()
                        external_inputs[guid]['value'] = point
                        print(f"  [OK] Extracted point from param: {point}")
                        break
                    value = extract_value_from_persistent_data(persistent_data)
                    if value is not None:
                        external_inputs[guid] = info.copy()
                        external_inputs[guid]['value'] = value
                        print(f"  [OK] Extracted value from param: {value}")
                        break
        
        # If still no value found
        if guid not in external_inputs or external_inputs[guid].get('value') is None:
            print(f"  [SKIP] No PersistentData or traceable source found")
            # Keep existing entry (might be external geometry)
            if guid in existing:
                external_inputs[guid] = existing[guid]
    
    # Merge with existing (preserve entries that weren't processed)
    for guid, info in existing.items():
        if guid not in external_inputs:
            external_inputs[guid] = info
    
    return external_inputs

if __name__ == '__main__':
    print("=" * 60)
    print("Extracting ALL External Input Values from GHX")
    print("=" * 60)
    
    inputs = parse_ghx_for_all_external_inputs()
    
    # Save updated external_inputs.json
    with open('external_inputs.json', 'w') as f:
        json.dump(inputs, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"Total entries: {len(inputs)}")
    
    # Count placeholders
    placeholders = []
    for guid, info in inputs.items():
        if isinstance(info, dict):
            value = info.get('value')
            if value is None:
                placeholders.append(guid)
    
    print(f"Placeholders (None values): {len(placeholders)}")
    if placeholders:
        print("\nRemaining placeholders (external geometry - no values in GHX):")
        for guid in placeholders:
            info = inputs[guid]
            print(f"  {guid[:8]}... ({info.get('type', 'Unknown')}): {info.get('note', '')}")
    
    print("\n[OK] Updated external_inputs.json")

