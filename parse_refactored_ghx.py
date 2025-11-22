"""
PHASE 1: GHX Structure Extraction
Parse refactored-no-sun.ghx and extract complete component graph.

Rules:
- No heuristics, no approximations
- Extract exact structure from XML
- One-to-one component mapping
- Full wire tracing
"""

import xml.etree.ElementTree as ET
import json
from collections import defaultdict


def parse_ghx(ghx_path):
    """Parse GHX file and extract complete component graph."""
    
    tree = ET.parse(ghx_path)
    root = tree.getroot()
    
    components = []
    wires = []
    
    # Find Definition chunk
    definition = None
    for chunk in root.findall('.//chunk'):
        if chunk.get('name') == 'Definition':
            definition = chunk
            break
    
    if definition is None:
        print("ERROR: No Definition chunk found in GHX")
        return None, None, None
    
    # Find DefinitionObjects chunk within Definition
    def_objects = None
    for chunk in definition.findall('./chunks/chunk'):
        if chunk.get('name') == 'DefinitionObjects':
            def_objects = chunk
            break
    
    if def_objects is None:
        print("ERROR: No DefinitionObjects chunk found")
        return None, None, None
    
    # Extract all components from Object chunks
    for chunk in def_objects.findall('./chunks/chunk'):
        if chunk.get('name') == 'Object' or chunk.get('name') == 'Group':
            component = extract_component_from_chunk(chunk)
            if component:
                components.append(component)
    
    # Extract all wires from Source elements
    for comp in components:
        comp_guid = comp['guid']
        for param in comp['params']:
            param_guid = param['param_guid']
            
            # Check if this parameter has source wires
            if 'sources' in param and param['sources']:
                for source_guid in param['sources']:
                    wires.append({
                        'from_component': source_guid,
                        'from_param': source_guid,  # Will resolve later
                        'to_component': comp_guid,
                        'to_param': param_guid,
                        'to_param_name': param['name']
                    })
    
    return components, wires


def extract_component_from_chunk(chunk):
    """Extract component metadata and parameters from Object/Group chunk."""
    
    chunk_name = chunk.get('name', '')
    
    # Extract top-level Object properties
    items = {}
    items_elem = chunk.find('./items')
    if items_elem is not None:
        for item in items_elem.findall('./item'):
            item_name = item.get('name', '')
            item_value = item.text
            if item_value is None:
                item_value = ''
            items[item_name] = item_value.strip()
    
    # Get component type (Name field for Objects)
    type_name = items.get('Name', chunk_name)
    
    # Find the Container chunk inside the Object
    container_chunk = None
    for sub_chunk in chunk.findall('./chunks/chunk'):
        if sub_chunk.get('name') == 'Container':
            container_chunk = sub_chunk
            break
    
    if container_chunk is None:
        # For groups, the chunk itself contains the data
        if chunk_name == 'Group':
            guid = items.get('InstanceGuid', '')
            nickname = items.get('NickName', items.get('Name', ''))
            return {
                'guid': guid,
                'instance_guid': guid,
                'type_name': 'Group',
                'nickname': nickname,
                'container': '',
                'position': {'x': 0, 'y': 0},
                'params': []
            }
        return None
    
    # Extract Container items (actual component details)
    container_items = {}
    container_items_elem = container_chunk.find('./items')
    if container_items_elem is not None:
        for item in container_items_elem.findall('./item'):
            item_name = item.get('name', '')
            item_value = item.text
            if item_value is None:
                item_value = ''
            container_items[item_name] = item_value.strip()
    
    # Get GUID (required)
    guid = container_items.get('InstanceGuid', '')
    if not guid:
        return None
    
    # Get nickname
    nickname = container_items.get('NickName', container_items.get('Name', ''))
    
    # Get container (group) - stored in attributes
    container = ''
    
    # Position - need to check attributes chunk
    position = {'x': 0, 'y': 0}
    for sub_chunk in container_chunk.findall('./chunks/chunk'):
        if sub_chunk.get('name') == 'Attributes':
            attrs_items_elem = sub_chunk.find('./items')
            if attrs_items_elem is not None:
                for item in attrs_items_elem.findall('./item'):
                    item_name = item.get('name', '')
                    if item_name == 'Pivot':
                        # Parse pivot point from structured XML
                        x_elem = item.find('./X')
                        y_elem = item.find('./Y')
                        if x_elem is not None and y_elem is not None:
                            try:
                                position['x'] = float(x_elem.text)
                                position['y'] = float(y_elem.text)
                            except:
                                pass
                    elif item_name == 'Parent':
                        # This is the container/group GUID
                        parent_guid = item.find('./ParentID')
                        if parent_guid is not None and parent_guid.text:
                            container = parent_guid.text.strip()
    
    instance_guid = guid
    
    # Extract parameters from param_input and param_output chunks in Container
    params = []
    
    for sub_chunk in container_chunk.findall('./chunks/chunk'):
        chunk_name = sub_chunk.get('name', '')
        
        if chunk_name == 'param_input':
            # This IS the parameter chunk
            param = extract_parameter_from_chunk(sub_chunk, 'input')
            if param:
                params.append(param)
        
        elif chunk_name == 'param_output':
            # This IS the parameter chunk
            param = extract_parameter_from_chunk(sub_chunk, 'output')
            if param:
                params.append(param)
        
        elif chunk_name == 'ParameterData':
            # Variable-parameter components (e.g., List Item) use this structure
            for param_chunk in sub_chunk.findall('./chunks/chunk'):
                param_chunk_name = param_chunk.get('name', '')
                if param_chunk_name == 'InputParam':
                    param = extract_parameter_from_chunk(param_chunk, 'input')
                    if param:
                        params.append(param)
                elif param_chunk_name == 'OutputParam':
                    param = extract_parameter_from_chunk(param_chunk, 'output')
                    if param:
                        params.append(param)
        
        elif chunk_name == 'Slider' and type_name == 'Number Slider':
            # Special handling for Number Slider
            slider_items = sub_chunk.find('./items')
            if slider_items is not None:
                slider_value = None
                for item in slider_items.findall('./item'):
                    if item.get('name') == 'Value':
                        slider_value = float(item.text) if item.text else 0
                        break
                
                # Create a synthetic output parameter with the slider value
                if slider_value is not None:
                    param = {
                        'param_guid': guid,  # Use component GUID as param GUID
                        'name': 'Value',
                        'type': 'output',
                        'persistent_data': [slider_value],
                        'sources': [],
                        'mapping': 0  # Sliders don't have mapping
                    }
                    params.append(param)
    
    component = {
        'guid': guid,
        'instance_guid': instance_guid,
        'type_name': type_name,
        'nickname': nickname,
        'container': container,
        'position': position,
        'params': params
    }
    
    return component


def extract_parameter_from_chunk(param_chunk, param_type):
    """Extract parameter information including persistent data and sources."""
    
    # Extract parameter properties
    items = {}
    items_elem = param_chunk.find('./items')
    if items_elem is not None:
        for item in items_elem.findall('./item'):
            item_name = item.get('name', '')
            item_value = item.text
            if item_value is None:
                item_value = ''
            items[item_name] = item_value.strip()
    
    param_guid = items.get('InstanceGuid', '')
    if not param_guid:
        return None
    
    name = items.get('Name', '')
    
    # Extract persistent data
    persistent_data = extract_persistent_data_from_chunk(param_chunk)
    
    # Extract source wires (for inputs) - stored as indexed items named "Source"
    sources = []
    if param_type == 'input' and items_elem is not None:
        for item in items_elem.findall('./item'):
            item_name = item.get('name', '')
            if item_name == 'Source':
                item_value = item.text
                if item_value:
                    sources.append(item_value.strip())
    
    # Extract expression if present (for parameters with expressions like "x-1")
    expression = items.get('InternalExpression', None)
    
    # Extract Mapping (0=None, 1=Graft, 2=Flatten)
    mapping = items.get('Mapping', '0')
    try:
        mapping = int(mapping)
    except (ValueError, TypeError):
        mapping = 0
    
    param = {
        'param_guid': param_guid,
        'name': name,
        'type': param_type,
        'persistent_data': persistent_data,
        'sources': sources,
        'expression': expression,
        'mapping': mapping
    }
    
    return param


def extract_persistent_data_from_chunk(param_chunk):
    """Extract persistent data from parameter chunk (sliders, panels, number inputs)."""
    
    data = []
    
    # Look for PersistentData chunk
    for sub_chunk in param_chunk.findall('./chunks/chunk'):
        if sub_chunk.get('name') == 'PersistentData':
            # Check for direct items (simple values)
            items_elem = sub_chunk.find('./items')
            if items_elem is not None:
                for item in items_elem.findall('./item'):
                    item_name = item.get('name', '')
                    if item_name != 'Count':  # Skip count metadata
                        value = item.text
                        if value is not None:
                            try:
                                if '.' in value or 'e' in value.lower():
                                    data.append(float(value))
                                else:
                                    data.append(int(value))
                            except ValueError:
                                data.append(value.strip())
            
            # Check for tree structure (Branch chunks)
            for branch_chunk in sub_chunk.findall('./chunks/chunk'):
                if branch_chunk.get('name') == 'Branch':
                    branch_data = []
                    # Look for Item chunks within Branch
                    for item_chunk in branch_chunk.findall('./chunks/chunk'):
                        if item_chunk.get('name') == 'Item':
                            # Extract value from item chunk
                            item_items = item_chunk.find('./items')
                            if item_items is not None:
                                for item in item_items.findall('./item'):
                                    item_name = item.get('name', '')
                                    
                                    # Skip TypeName metadata
                                    if item_name == 'TypeName':
                                        continue
                                    
                                    # Check for structured types (point/vector)
                                    if item.find('./X') is not None:
                                        # Point or vector
                                        x = float(item.find('./X').text)
                                        y = float(item.find('./Y').text)
                                        z = float(item.find('./Z').text)
                                        branch_data.append([x, y, z])
                                    elif item_name == 'boolean':
                                        # Boolean type (GHX line 1521)
                                        value = item.text
                                        if value is not None:
                                            branch_data.append(value.strip().lower() == 'true')
                                    else:
                                        # Simple value
                                        value = item.text
                                        if value is not None:
                                            try:
                                                if '.' in value or 'e' in value.lower():
                                                    branch_data.append(float(value))
                                                else:
                                                    branch_data.append(int(value))
                                            except ValueError:
                                                branch_data.append(value.strip())
                    if branch_data:
                        data.extend(branch_data)  # Flatten for now
    
    return data


def build_graph_structure(components, wires):
    """Build structured graph with component index and wire index."""
    
    # Component index
    component_index = {}
    for comp in components:
        component_index[comp['guid']] = {
            'guid': comp['guid'],
            'type_name': comp['type_name'],
            'nickname': comp['nickname'],
            'container': comp['container'],
            'position': comp['position'],
            'params': {p['name']: p['param_guid'] for p in comp['params']}
        }
    
    # Wire index
    wire_index = []
    for wire in wires:
        wire_index.append({
            'from': wire['from_component'],
            'to': wire['to_component'],
            'to_param': wire['to_param_name']
        })
    
    # Full graph
    graph = {
        'components': components,
        'wires': wires,
        'component_count': len(components),
        'wire_count': len(wires)
    }
    
    return graph, component_index, wire_index


def main():
    """Main execution: parse GHX and save outputs."""
    
    print("=" * 80)
    print("PHASE 1: GHX STRUCTURE EXTRACTION")
    print("=" * 80)
    print()
    
    ghx_path = 'refactored-no-sun.ghx'
    
    print(f"Parsing {ghx_path}...")
    components, wires = parse_ghx(ghx_path)
    
    if components is None:
        print("ERROR: Failed to parse GHX")
        return
    
    print(f"[OK] Found {len(components)} components")
    print(f"[OK] Found {len(wires)} wires")
    print()
    
    # Build structured outputs
    graph, component_index, wire_index = build_graph_structure(components, wires)
    
    # Save outputs
    print("Saving outputs...")
    
    with open('ghx_graph.json', 'w') as f:
        json.dump(graph, f, indent=2)
    print("[OK] Saved ghx_graph.json")
    
    with open('component_index.json', 'w') as f:
        json.dump(component_index, f, indent=2)
    print("[OK] Saved component_index.json")
    
    with open('wire_index.json', 'w') as f:
        json.dump(wire_index, f, indent=2)
    print("[OK] Saved wire_index.json")
    
    print()
    print("=" * 80)
    print("PHASE 1 COMPLETE")
    print("=" * 80)
    print()
    
    # Summary statistics
    print("SUMMARY:")
    print(f"  Total components: {len(components)}")
    print(f"  Total wires: {len(wires)}")
    print()
    
    # Component type distribution
    type_counts = defaultdict(int)
    for comp in components:
        type_counts[comp['type_name']] += 1
    
    print("Component types found:")
    for type_name, count in sorted(type_counts.items()):
        print(f"  {type_name}: {count}")
    print()
    
    # Group/Container distribution
    containers = set()
    for comp in components:
        if comp['container']:
            containers.add(comp['container'])
    
    if containers:
        print(f"Groups found: {len(containers)}")
        for container in sorted(containers):
            comp_count = sum(1 for c in components if c['container'] == container)
            print(f"  {container}: {comp_count} components")
    else:
        print("No groups found (will use position-based detection)")
    
    print()
    print("Ready for PHASE 2: Rotatingslats group isolation")
    print()


if __name__ == '__main__':
    main()

