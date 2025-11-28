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

# Non-functional component types to skip
NON_FUNCTIONAL_TYPES = {'Scribble', 'Sketch', 'Group', 'Panel'}


def extract_items(elem):
    """Extract items dict from XML element."""
    items = {}
    items_elem = elem.find('./items')
    if items_elem is not None:
        for item in items_elem.findall('./item'):
            name = item.get('name', '')
            value = item.text or ''
            items[name] = value.strip()
    return items


def find_chunk(parent, name):
    """Find first chunk with given name."""
    for chunk in parent.findall('./chunks/chunk'):
        if chunk.get('name') == name:
            return chunk
    return None


def safe_float(elem, default=0.0):
    """Safely extract float from XML element."""
    if elem is not None and elem.text:
        try:
            return float(elem.text)
        except (ValueError, TypeError):
            pass
    return default


def parse_ghx(ghx_path):
    """Parse GHX file and extract complete component graph."""
    
    tree = ET.parse(ghx_path)
    root = tree.getroot()
    
    components = []
    wires = []
    
    # Find Definition chunk
    definition = next((c for c in root.findall('.//chunk') if c.get('name') == 'Definition'), None)
    if definition is None:
        print("ERROR: No Definition chunk found in GHX")
        return None, None
    
    # Find DefinitionObjects chunk
    def_objects = find_chunk(definition, 'DefinitionObjects')
    if def_objects is None:
        print("ERROR: No DefinitionObjects chunk found")
        return None, None
    
    # Extract components
    for chunk in def_objects.findall('./chunks/chunk'):
        if chunk.get('name') == 'Object':
            component = extract_component_from_chunk(chunk)
            if component:
                components.append(component)
    
    # Extract wires from source connections
    for comp in components:
        for param in comp['params']:
            for source_guid in param.get('sources', []):
                wires.append({
                    'from_component': source_guid,
                    'from_param': source_guid,
                    'to_component': comp['guid'],
                    'to_param': param['param_guid'],
                    'to_param_name': param['name']
                })
    
    return components, wires


def extract_component_from_chunk(chunk):
    """Extract component metadata and parameters from Object chunk."""
    items = extract_items(chunk)
    type_name = items.get('Name', chunk.get('name', ''))
    
    # Skip non-functional components
    if type_name in NON_FUNCTIONAL_TYPES:
        return None
    
    # Find Container chunk (required for all functional components)
    container_chunk = find_chunk(chunk, 'Container')
    if container_chunk is None:
        return None
    
    # Extract component details
    container_items = extract_items(container_chunk)
    guid = container_items.get('InstanceGuid', '')
    if not guid:
        return None
    
    # Extract position and container from Attributes
    position = {'x': 0, 'y': 0}
    container = ''
    attrs_chunk = find_chunk(container_chunk, 'Attributes')
    if attrs_chunk:
        for item in attrs_chunk.findall('./items/item'):
            name = item.get('name', '')
            if name == 'Pivot':
                position['x'] = safe_float(item.find('./X'))
                position['y'] = safe_float(item.find('./Y'))
            elif name == 'Parent':
                parent_id = item.find('./ParentID')
                if parent_id is not None and parent_id.text:
                    container = parent_id.text.strip()
    
    # Extract parameters
    params = []
    for sub_chunk in container_chunk.findall('./chunks/chunk'):
        chunk_name = sub_chunk.get('name', '')
        
        if chunk_name == 'param_input':
            param = extract_parameter_from_chunk(sub_chunk, 'input')
            if param:
                params.append(param)
        elif chunk_name == 'param_output':
            param = extract_parameter_from_chunk(sub_chunk, 'output')
            if param:
                params.append(param)
        elif chunk_name == 'ParameterData':
            # Variable-parameter components (e.g., List Item)
            for param_chunk in sub_chunk.findall('./chunks/chunk'):
                param_type = 'input' if param_chunk.get('name') == 'InputParam' else 'output'
                if param_chunk.get('name') in ('InputParam', 'OutputParam'):
                    param = extract_parameter_from_chunk(param_chunk, param_type)
                    if param:
                        params.append(param)
        elif chunk_name == 'Slider' and type_name == 'Number Slider':
            # Special handling for Number Slider
            slider_items = sub_chunk.find('./items')
            if slider_items:
                for item in slider_items.findall('./item'):
                    if item.get('name') == 'Value':
                        slider_value = safe_float(item, 0)
                        params.append({
                            'param_guid': guid,
                            'name': 'Value',
                            'type': 'output',
                            'persistent_data': [slider_value],
                            'sources': [],
                            'mapping': 0,
                            'reverse_data': False
                        })
                        break
    
    return {
        'guid': guid,
        'instance_guid': guid,
        'type_name': type_name,
        'nickname': container_items.get('NickName', container_items.get('Name', '')),
        'container': container,
        'position': position,
        'params': params
    }


def extract_parameter_from_chunk(param_chunk, param_type):
    """Extract parameter information including persistent data and sources."""
    items = extract_items(param_chunk)
    param_guid = items.get('InstanceGuid', '')
    if not param_guid:
        return None
    
    # Extract source wires (for inputs)
    sources = []
    if param_type == 'input':
        items_elem = param_chunk.find('./items')
        if items_elem:
            for item in items_elem.findall('./item'):
                if item.get('name') == 'Source' and item.text:
                    sources.append(item.text.strip())
    
    # Extract mapping and reverse_data
    mapping = int(items.get('Mapping', '0')) if items.get('Mapping', '0').isdigit() else 0
    reverse_data = items.get('ReverseData', 'false').lower() == 'true'
    
    return {
        'param_guid': param_guid,
        'name': items.get('Name', ''),
        'type': param_type,
        'persistent_data': extract_persistent_data_from_chunk(param_chunk),
        'sources': sources,
        'expression': items.get('InternalExpression'),
        'mapping': mapping,
        'reverse_data': reverse_data
    }


def extract_persistent_data_from_chunk(param_chunk):
    """Extract persistent data from parameter chunk (sliders, number inputs)."""
    data = []
    persistent_chunk = find_chunk(param_chunk, 'PersistentData')
    if not persistent_chunk:
        return data
    
    # Extract direct items (simple values)
    for item in persistent_chunk.findall('./items/item'):
        if item.get('name') != 'Count' and item.text:
            value = item.text.strip()
            try:
                data.append(float(value) if '.' in value or 'e' in value.lower() else int(value))
            except ValueError:
                data.append(value)
    
    # Extract tree structure (Branch chunks)
    for branch_chunk in persistent_chunk.findall('./chunks/chunk'):
        if branch_chunk.get('name') != 'Branch':
            continue
        
        branch_data = []
        for item_chunk in branch_chunk.findall('./chunks/chunk'):
            if item_chunk.get('name') != 'Item':
                continue
            
            item_items = item_chunk.find('./items')
            if not item_items:
                continue
            
            for item in item_items.findall('./item'):
                item_name = item.get('name', '')
                if item_name == 'TypeName':
                    continue
                
                # Handle plane type
                if item_name == 'plane':
                    try:
                        plane_dict = {
                            'origin': [safe_float(item.find('./Ox')), safe_float(item.find('./Oy')), safe_float(item.find('./Oz'))],
                            'x_axis': [safe_float(item.find('./Xx'), 1.0), safe_float(item.find('./Xy')), safe_float(item.find('./Xz'))],
                            'y_axis': [safe_float(item.find('./Yx')), safe_float(item.find('./Yy'), 1.0), safe_float(item.find('./Yz'))]
                        }
                        # Calculate Z-axis (normal) as cross product
                        x, y = plane_dict['x_axis'], plane_dict['y_axis']
                        z_axis = [
                            x[1] * y[2] - x[2] * y[1],
                            x[2] * y[0] - x[0] * y[2],
                            x[0] * y[1] - x[1] * y[0]
                        ]
                        plane_dict['z_axis'] = plane_dict['normal'] = z_axis
                        branch_data.append(plane_dict)
                    except (ValueError, TypeError, AttributeError):
                        pass
                # Handle point/vector
                elif item.find('./X') is not None:
                    branch_data.append([safe_float(item.find('./X')), safe_float(item.find('./Y')), safe_float(item.find('./Z'))])
                # Handle boolean
                elif item_name == 'boolean' and item.text:
                    branch_data.append(item.text.strip().lower() == 'true')
                # Handle simple value
                elif item.text:
                    value = item.text.strip()
                    try:
                        branch_data.append(float(value) if '.' in value or 'e' in value.lower() else int(value))
                    except ValueError:
                        branch_data.append(value)
        
        data.extend(branch_data)
    
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
    
    ghx_path = 'refactored-sun-simple.ghx'
    
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

