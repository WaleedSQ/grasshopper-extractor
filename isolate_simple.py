"""
Simple Isolation: Extract inputs and components without group complexity
- All Number Sliders and Panels -> inputs.json
- All other components (including Ex Tree) -> components.json
- All wires -> wires.json
"""

import json
import xml.etree.ElementTree as ET


def extract_slider_value(ghx_path, slider_guid):
    """Extract slider value from GHX file."""
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
                                
                                if instance_guid == slider_guid:
                                    for slider_chunk in sub_chunk.findall('./chunks/chunk'):
                                        if slider_chunk.get('name') == 'Slider':
                                            slider_items = slider_chunk.find('./items')
                                            if slider_items is not None:
                                                for item in slider_items.findall('./item'):
                                                    if item.get('name') == 'Value':
                                                        value = float(item.text) if item.text else 0
                                                        return value
                                    break
    return None


def isolate_simple():
    """Extract inputs and components without group complexity."""
    
    print("=" * 80)
    print("SIMPLE ISOLATION: Extract inputs and components")
    print("=" * 80)
    print()
    
    # Load the full graph
    with open('ghx_graph.json', 'r') as f:
        graph = json.load(f)
    
    components = graph['components']
    wires = graph['wires']
    ghx_path = 'refactored-sun-simple.ghx'
    
    print(f"Loaded {len(components)} components, {len(wires)} wires")
    print()
    
    # Separate inputs from components
    inputs = {}
    computation_components = []
    
    # Data source types (inputs)
    input_types = {'Number Slider', 'Value List'}
    
    for comp in components:
        comp_type = comp['type_name']
        comp_guid = comp['guid']
        
        if comp_type in input_types:
            # Extract data
            data = None
            
            # Check for persistent data in params
            for param in comp['params']:
                if param.get('persistent_data'):
                    data = param['persistent_data']
                    break
            
            # Special handling for Number Slider - extract from GHX if needed
            if comp_type == 'Number Slider' and not data:
                slider_value = extract_slider_value(ghx_path, comp_guid)
                if slider_value is not None:
                    data = [slider_value]
            
            inputs[comp_guid] = {
                'guid': comp_guid,
                'type': comp_type,
                'nickname': comp.get('nickname', ''),
                'data': data if data else None
            }
        elif comp_type != 'Group':
            # Regular component (including Ex Tree, Division, etc.)
            # Exclude Group components since we're ignoring groups
            computation_components.append(comp)
    
    print(f"Inputs (sliders/panels): {len(inputs)}")
    print(f"Components: {len(computation_components)}")
    print()
    
    # Build mapping of parameter GUID -> component GUID for wire resolution
    param_to_component = {}
    for comp in components:
        comp_guid = comp['guid']
        for param in comp['params']:
            param_guid = param['param_guid']
            param_to_component[param_guid] = comp_guid
    
    # Resolve wires: convert parameter GUIDs to component GUIDs
    resolved_wires = []
    for wire in wires:
        from_param_guid = wire['from_component']  # Actually a parameter GUID
        to_comp_guid = wire['to_component']        # Component GUID
        
        # Resolve from_component
        from_comp_guid = param_to_component.get(from_param_guid, from_param_guid)
        
        resolved_wire = {
            'from_component': from_comp_guid,
            'from_param': wire['from_param'],
            'to_component': to_comp_guid,
            'to_param': wire['to_param'],
            'to_param_name': wire.get('to_param_name', '')
        }
        resolved_wires.append(resolved_wire)
    
    print(f"Resolved {len(resolved_wires)} wires")
    print()
    
    # Save outputs
    with open('inputs.json', 'w') as f:
        json.dump(inputs, f, indent=2)
    print("[OK] Saved inputs.json")
    
    with open('components.json', 'w') as f:
        json.dump(computation_components, f, indent=2)
    print("[OK] Saved components.json")
    
    with open('wires.json', 'w') as f:
        json.dump(resolved_wires, f, indent=2)
    print("[OK] Saved wires.json")
    
    print()
    print("=" * 80)
    print("SIMPLE ISOLATION COMPLETE")
    print("=" * 80)
    print()
    
    # Summary
    print("SUMMARY:")
    print(f"  Inputs: {len(inputs)}")
    print(f"  Components: {len(computation_components)}")
    print(f"  Wires: {len(resolved_wires)}")
    print()
    
    # Input types
    input_type_counts = {}
    for input_data in inputs.values():
        input_type = input_data['type']
        input_type_counts[input_type] = input_type_counts.get(input_type, 0) + 1
    
    print("Input types:")
    for input_type, count in sorted(input_type_counts.items()):
        print(f"  {input_type}: {count}")
    print()
    
    # Component types (top 10)
    comp_type_counts = {}
    for comp in computation_components:
        comp_type = comp['type_name']
        comp_type_counts[comp_type] = comp_type_counts.get(comp_type, 0) + 1
    
    print("Top component types:")
    for comp_type, count in sorted(comp_type_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {comp_type}: {count}")


if __name__ == '__main__':
    isolate_simple()

