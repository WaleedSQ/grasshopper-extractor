"""
Rebuild the complete component graph including ALL dependencies.
This ensures we have all upstream components needed for evaluation.
"""
import json
from collections import defaultdict, OrderedDict

with open('rotatingslats_data.json', 'r') as f:
    data = json.load(f)

source_guid = "a7d2817a-3182-496e-a453-80e7eeba16fa"
panel_source_guid = "4d5670e5-1abc-417e-b9ce-3cf7878b98c2"  # Degrees output

all_objects = {**data['group_objects'], **data['external_objects']}

# Build output parameter map
output_params = {}
for key, obj in all_objects.items():
    for param_key, param_info in obj.get('params', {}).items():
        param_guid = param_info.get('data', {}).get('InstanceGuid')
        if param_guid:
            output_params[param_guid] = {
                'obj_key': key,
                'obj': obj,
                'param_key': param_key,
                'param_info': param_info
            }

# Build reverse connections: target -> [sources]
reverse_conn = defaultdict(list)
for conn in data['connections']:
    reverse_conn[conn['target']].append({
        'source': conn['source'],
        'target_param': conn.get('target_param'),
        'source_param': conn.get('source_param')
    })

# Also from parameter sources
for key, obj in all_objects.items():
    obj_guid = obj.get('instance_guid') or obj.get('guid')
    for param_key, param_info in obj.get('params', {}).items():
        for source in param_info.get('sources', []):
            source_guid_conn = source.get('guid')
            if source_guid_conn:
                reverse_conn[obj_guid].append({
                    'source': source_guid_conn,
                    'target_param': param_key,
                    'source_param': None
                })
                # Also add reverse connection for the parameter itself
                param_guid = param_info.get('data', {}).get('InstanceGuid')
                if param_guid:
                    reverse_conn[param_guid].append({
                        'source': source_guid_conn,
                        'target_param': param_key,
                        'source_param': None
                    })

def get_component_full_info(obj_guid: str) -> dict:
    """Get full component information."""
    # Check if it's an output parameter
    if obj_guid in output_params:
        info = output_params[obj_guid]
        obj = info['obj']
        return {
            'type': 'output_param',
            'obj': obj,
            'param_key': info['param_key'],
            'param_info': info['param_info'],
            'instance_guid': obj_guid
        }
    
    # Find object
    obj = None
    obj_key = None
    for key, o in all_objects.items():
        if o.get('instance_guid') == obj_guid:
            obj = o
            obj_key = key
            break
    
    if not obj:
        return None
    
    # Get inputs with sources
    inputs = {}
    for param_key, param_info in obj.get('params', {}).items():
        if param_key.startswith('param_input'):
            param_name = param_info.get('data', {}).get('NickName', param_key)
            param_desc = param_info.get('data', {}).get('Description', '')
            sources = param_info.get('sources', [])
            # Also check if sources are in data.Source (for external components)
            if not sources:
                source_list = param_info.get('data', {}).get('Source', [])
                if source_list:
                    sources = [{'guid': src, 'source_guid': src} for src in source_list if src]
            
            input_sources = []
            for source in sources:
                source_guid_conn = source.get('guid')
                if source_guid_conn in output_params:
                    source_info = output_params[source_guid_conn]
                    input_sources.append({
                        'type': 'output_param',
                        'source_guid': source_guid_conn,
                        'source_obj_guid': source_info['obj'].get('instance_guid'),
                        'source_obj_name': source_info['obj'].get('nickname', source_info['obj']['type']),
                        'source_obj_type': source_info['obj']['type'],
                        'source_param_name': source_info['param_info'].get('data', {}).get('NickName', source_info['param_key'])
                    })
                else:
                    # Check if it's an external input (slider, panel, etc.)
                    try:
                        import os
                        if os.path.exists('external_inputs.json'):
                            with open('external_inputs.json', 'r') as f:
                                external_inputs = json.load(f)
                            if source_guid_conn in external_inputs:
                                ext_input = external_inputs[source_guid_conn]
                                input_sources.append({
                                    'type': 'external_input',
                                    'source_guid': source_guid_conn,
                                    'source_obj_name': ext_input.get('object_nickname', ext_input.get('object_type', 'External Input')),
                                    'source_obj_type': ext_input.get('object_type', 'External Input')
                                })
                                continue
                    except Exception:
                        pass
                    
                    # Check if it's a component in all_objects
                    source_obj = None
                    for key, o in all_objects.items():
                        if o.get('instance_guid') == source_guid_conn:
                            source_obj = o
                            break
                    if source_obj:
                        input_sources.append({
                            'type': 'object',
                            'source_guid': source_guid_conn,
                            'source_obj_name': source_obj.get('nickname', source_obj['type']),
                            'source_obj_type': source_obj['type']
                        })
                    else:
                        # Source not found - still add it so resolve_input_value can try to resolve it
                        input_sources.append({
                            'type': 'unknown',
                            'source_guid': source_guid_conn
                        })
            
            inputs[param_key] = {
                'name': param_name,
                'description': param_desc,
                'sources': input_sources,
                'persistent_values': param_info.get('persistent_values', []),  # Preserve PersistentData
                'values': param_info.get('values', [])
            }
    
    # Get outputs
    outputs = {}
    for param_key, param_info in obj.get('params', {}).items():
        if param_key.startswith('param_output'):
            param_name = param_info.get('data', {}).get('NickName', param_key)
            param_desc = param_info.get('data', {}).get('Description', '')
            param_guid = param_info.get('data', {}).get('InstanceGuid')
            
            # Find targets from reverse connections
            targets = []
            # Check reverse connections for this output parameter GUID
            for conn in reverse_conn.get(param_guid, []):
                source_guid_conn = conn['source']
                if source_guid_conn in output_params:
                    source_info = output_params[source_guid_conn]
                    targets.append({
                        'type': 'output_param',
                        'target_guid': source_guid_conn,
                        'target_obj_guid': source_info['obj'].get('instance_guid'),
                        'target_obj_name': source_info['obj'].get('nickname', source_info['obj']['type']),
                        'target_param': conn.get('target_param')
                    })
                else:
                    target_obj = None
                    for key, o in all_objects.items():
                        if o.get('instance_guid') == source_guid_conn:
                            target_obj = o
                            break
                    if target_obj:
                        targets.append({
                            'type': 'object',
                            'target_guid': source_guid_conn,
                            'target_obj_name': target_obj.get('nickname', target_obj['type']),
                            'target_obj_type': target_obj['type'],
                            'target_param': conn.get('target_param')
                        })
            
            outputs[param_key] = {
                'name': param_name,
                'description': param_desc,
                'instance_guid': param_guid,
                'targets': targets
            }
    
    return {
        'type': 'component',
        'obj_key': obj_key,
        'obj': obj,
        'instance_guid': obj_guid,
        'inputs': inputs,
        'outputs': outputs
    }

# Build dependency graph backwards from target, including ALL dependencies
def build_complete_dependency_graph(end_param_guid: str) -> OrderedDict:
    """Build complete dependency graph by working backwards from target."""
    graph = OrderedDict()
    visited = set()
    queue = [end_param_guid]
    
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        
        comp_info = get_component_full_info(current)
        if not comp_info:
            continue
        
        graph[current] = comp_info
        
        # If this is an output parameter, add the parent object
        if comp_info['type'] == 'output_param':
            obj_guid = comp_info['obj'].get('instance_guid')
            if obj_guid and obj_guid not in visited:
                queue.append(obj_guid)
        
        # Follow reverse connections to find sources
        if comp_info['type'] == 'component':
            # Check reverse connections for all outputs
            for output_key, output_info in comp_info.get('outputs', {}).items():
                param_guid = output_info.get('instance_guid')
                if param_guid:
                    for conn in reverse_conn.get(param_guid, []):
                        source_guid = conn['source']
                        if source_guid not in visited:
                            queue.append(source_guid)
                        # If source is output param, also add parent
                        if source_guid in output_params:
                            parent_obj_guid = output_params[source_guid]['obj'].get('instance_guid')
                            if parent_obj_guid and parent_obj_guid not in visited:
                                queue.append(parent_obj_guid)
            
            # Also check inputs - their sources are dependencies
            for input_key, input_info in comp_info.get('inputs', {}).items():
                for source in input_info.get('sources', []):
                    source_guid = source.get('source_guid')
                    if source_guid and source_guid not in visited:
                        queue.append(source_guid)
                    # If source is output param, also add parent
                    if source_guid in output_params:
                        parent_obj_guid = output_params[source_guid]['obj'].get('instance_guid')
                        if parent_obj_guid and parent_obj_guid not in visited:
                            queue.append(parent_obj_guid)
        else:
            # For output params, check reverse connections
            for conn in reverse_conn.get(current, []):
                source_guid = conn['source']
                if source_guid not in visited:
                    queue.append(source_guid)
                if source_guid in output_params:
                    parent_obj_guid = output_params[source_guid]['obj'].get('instance_guid')
                    if parent_obj_guid and parent_obj_guid not in visited:
                        queue.append(parent_obj_guid)
    
    return graph

# Build graph backwards from target
graph = build_complete_dependency_graph(panel_source_guid)

# Also ensure all components in Rotatingslats group are included
# Some components might not be on the path to final output but are still needed
print("\nChecking for missing components in Rotatingslats group...")
for obj_key, obj in data['group_objects'].items():
    obj_guid = obj.get('instance_guid') or obj.get('guid')
    if obj_guid and obj_guid not in graph:
        # Check if this component has connections to components already in the graph
        # or if it's connected to components that should be in the graph
        should_add = False
        
        # Check if any of its outputs are used by components in the graph
        for param_key, param_info in obj.get('params', {}).items():
            if param_key.startswith('param_output'):
                param_guid = param_info.get('data', {}).get('InstanceGuid')
                if param_guid:
                    # Check if this output parameter is used by any component
                    for conn in data['connections']:
                        if conn['source'] == param_guid:
                            target_guid = conn['target']
                            # Check if target is in graph or in group_objects
                            if target_guid in graph or target_guid in data['group_objects']:
                                should_add = True
                                break
                    if should_add:
                        break
        
        # Also check if it's a Series component (they're often needed)
        if obj.get('type') == 'Series':
            should_add = True
        
        if should_add:
            comp_info = get_component_full_info(obj_guid)
            if comp_info:
                graph[obj_guid] = comp_info
                print(f"Added missing component: {comp_info['obj'].get('type')} '{comp_info['obj'].get('nickname')}' ({obj_guid[:8]}...)")
                
                # Also add its dependencies recursively
                def add_dependencies(comp_guid):
                    if comp_guid not in graph:
                        return
                    comp_info = graph[comp_guid]
                    if comp_info['type'] == 'component':
                        for input_key, input_info in comp_info.get('inputs', {}).items():
                            for source in input_info.get('sources', []):
                                source_guid = source.get('source_guid')
                                if source_guid and source_guid in output_params:
                                    source_info = output_params[source_guid]
                                    parent_obj_guid = source_info['obj'].get('instance_guid')
                                    if parent_obj_guid and parent_obj_guid not in graph:
                                        parent_comp_info = get_component_full_info(parent_obj_guid)
                                        if parent_comp_info:
                                            graph[parent_obj_guid] = parent_comp_info
                                            print(f"  Added dependency: {parent_comp_info['obj'].get('type')} ({parent_obj_guid[:8]}...)")
                                            add_dependencies(parent_obj_guid)
                
                add_dependencies(obj_guid)

# Also add components that are sources for Number components
# (Number components can have Source connections that aren't captured by reverse connections)
try:
    with open('number_component_sources.json', 'r') as f:
        number_sources = json.load(f)
    
    # For each Number component source, ensure the source component is in the graph
    for num_guid, info in number_sources.items():
        source_guid = info['source_guid']
        
        # Check if source is an output parameter
        if source_guid in output_params:
            source_info = output_params[source_guid]
            parent_obj_guid = source_info['obj'].get('instance_guid')
            
            # If parent component is not in graph, add it
            if parent_obj_guid and parent_obj_guid not in graph:
                comp_info = get_component_full_info(parent_obj_guid)
                if comp_info:
                    graph[parent_obj_guid] = comp_info
                    print(f"Added missing component: {comp_info['obj'].get('type')} '{comp_info['obj'].get('nickname')}' ({parent_obj_guid[:8]}...)")
                    
                    # Also add its dependencies
                    if comp_info['type'] == 'component':
                        for input_key, input_info in comp_info.get('inputs', {}).items():
                            for source in input_info.get('sources', []):
                                source_guid_conn = source.get('source_guid')
                                if source_guid_conn and source_guid_conn not in graph:
                                    # Try to add the source component
                                    if source_guid_conn in output_params:
                                        source_param_info = output_params[source_guid_conn]
                                        source_obj_guid = source_param_info['obj'].get('instance_guid')
                                        if source_obj_guid and source_obj_guid not in graph:
                                            source_comp_info = get_component_full_info(source_obj_guid)
                                            if source_comp_info:
                                                graph[source_obj_guid] = source_comp_info
                                                print(f"  Added dependency: {source_comp_info['obj'].get('type')} ({source_obj_guid[:8]}...)")
        
        # Also check if source_guid is itself a Number component (from number_sources)
        # This handles cases where Number components source from other Number components
        elif source_guid in number_sources:
            # The source is another Number component - ensure it's in the graph
            if source_guid not in graph:
                # Check if it's in group_objects or external_objects
                source_obj = None
                if source_guid in data['group_objects']:
                    source_obj = data['group_objects'][source_guid]
                elif source_guid in data['external_objects']:
                    source_obj = data['external_objects'][source_guid]
                
                if source_obj:
                    comp_info = get_component_full_info(source_guid)
                    if comp_info:
                        graph[source_guid] = comp_info
                        print(f"Added missing Number component: '{comp_info['obj'].get('nickname')}' ({source_guid[:8]}...)")
                        
                        # Recursively add its source
                        source_num_source_guid = number_sources[source_guid]['source_guid']
                        if source_num_source_guid in output_params:
                            source_num_source_info = output_params[source_num_source_guid]
                            source_num_source_obj_guid = source_num_source_info['obj'].get('instance_guid')
                            if source_num_source_obj_guid and source_num_source_obj_guid not in graph:
                                source_num_comp_info = get_component_full_info(source_num_source_obj_guid)
                                if source_num_comp_info:
                                    graph[source_num_source_obj_guid] = source_num_comp_info
                                    print(f"  Added dependency: {source_num_comp_info['obj'].get('type')} ({source_num_source_obj_guid[:8]}...)")
        
        # Also check if source_guid is an output parameter - ensure its parent component is in the graph
        elif source_guid in output_params:
            source_info = output_params[source_guid]
            parent_obj_guid = source_info['obj'].get('instance_guid')
            if parent_obj_guid and parent_obj_guid not in graph:
                comp_info = get_component_full_info(parent_obj_guid)
                if comp_info:
                    graph[parent_obj_guid] = comp_info
                    print(f"Added missing component (from output param): {comp_info['obj'].get('type')} '{comp_info['obj'].get('nickname')}' ({parent_obj_guid[:8]}...)")
                    
                    # Register output parameters for this component
                    obj = comp_info['obj']
                    for param_key, param_info in obj.get('params', {}).items():
                        if param_key.startswith('param_output'):
                            param_guid = param_info.get('data', {}).get('InstanceGuid')
                            if param_guid:
                                output_params[param_guid] = {
                                    'obj_key': parent_obj_guid,
                                    'obj': obj,
                                    'param_key': param_key,
                                    'param_info': param_info
                                }
                    
                    # Also add its dependencies recursively
                    def add_deps_recursive(comp_guid):
                        if comp_guid not in graph:
                            return
                        comp_info = graph[comp_guid]
                        if comp_info['type'] == 'component':
                            for input_key, input_info in comp_info.get('inputs', {}).items():
                                for source in input_info.get('sources', []):
                                    source_guid_conn = source.get('source_guid')
                                    if source_guid_conn and source_guid_conn not in graph:
                                        # Try to add the source component
                                        if source_guid_conn in output_params:
                                            source_param_info = output_params[source_guid_conn]
                                            source_obj_guid = source_param_info['obj'].get('instance_guid')
                                            if source_obj_guid and source_obj_guid not in graph:
                                                source_comp_info = get_component_full_info(source_obj_guid)
                                                if source_comp_info:
                                                    graph[source_obj_guid] = source_comp_info
                                                    print(f"  Added dependency: {source_comp_info['obj'].get('type')} ({source_obj_guid[:8]}...)")
                                                    
                                                    # Register output parameters for this component too
                                                    source_obj = source_comp_info['obj']
                                                    for param_key, param_info in source_obj.get('params', {}).items():
                                                        if param_key.startswith('param_output'):
                                                            param_guid = param_info.get('data', {}).get('InstanceGuid')
                                                            if param_guid:
                                                                output_params[param_guid] = {
                                                                    'obj_key': source_obj_guid,
                                                                    'obj': source_obj,
                                                                    'param_key': param_key,
                                                                    'param_info': param_info
                                                                }
                                                    
                                                    add_deps_recursive(source_obj_guid)
                    
                    add_deps_recursive(parent_obj_guid)
except FileNotFoundError:
    pass

# Also add components that are sources for Panels
# Panels can have Source connections to output parameters
try:
    with open('rotatingslats_data.json', 'r') as f:
        data = json.load(f)
    
    all_objects = {**data['group_objects'], **data['external_objects']}
    
    # Find all Panels with Source connections
    for key, obj in all_objects.items():
        if obj.get('type') == 'Panel':
            # Check if Panel has a Source item (in GHX, not in our JSON structure)
            # We need to check connections or trace from Panel GUID
            pass
    
    # Load external components if needed
    try:
        import os
        external_component_files = [
            'external_division_component.json',
            'external_subtraction_e2671ced.json',
            'external_subtraction_components.json',
            # 'external_vector_xyz_component.json',  # Removed - Vector XYZ component removed from GHX
            'external_vector_d0668a07_component.json',
            'external_vector_2pt_1f794702_component.json',
            'external_mirror_component.json',
            'external_rotate_component.json',
            'external_polygon_component.json',
            'external_area_component.json'
        ]
        
        for file_path in external_component_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    external_data = json.load(f)
                
                # Handle both single component and dict of components
                if isinstance(external_data, dict):
                    if 'instance_guid' in external_data:
                        # Single component
                        components = [external_data]
                    else:
                        # Dict of components
                        components = list(external_data.values())
                else:
                    components = []
                
                for comp in components:
                    if comp and 'instance_guid' in comp:
                        comp_guid = comp['instance_guid']
                        all_objects[comp_guid] = comp
                        
                        # Add output parameters to output_params
                        for param_key, param_info in comp.get('params', {}).items():
                            if param_key.startswith('param_output'):
                                param_guid = param_info.get('data', {}).get('InstanceGuid')
                                if param_guid:
                                    output_params[param_guid] = {
                                        'obj_key': comp_guid,
                                        'obj': comp,
                                        'param_key': param_key,
                                        'param_info': param_info
                                    }
                        
                        # If this external component's output parameters are referenced, add it to the graph
                        comp_added = False
                        try:
                            with open('number_component_sources.json', 'r') as f:
                                number_sources = json.load(f)
                            
                            for param_key, param_info in comp.get('params', {}).items():
                                if param_key.startswith('param_output'):
                                    param_guid = param_info.get('data', {}).get('InstanceGuid')
                                    if param_guid:
                                        # Check if this output parameter is referenced by any Number component
                                        if param_guid in [info['source_guid'] for info in number_sources.values()]:
                                            # This output parameter is referenced - add the component to graph
                                            if comp_guid not in graph:
                                                comp_info = get_component_full_info(comp_guid)
                                                if comp_info:
                                                    graph[comp_guid] = comp_info
                                                    print(f"Added external component to graph: {comp.get('type')} '{comp.get('nickname')}' ({comp_guid[:8]}...)")
                                                    comp_added = True
                                                    break
                        except FileNotFoundError:
                            pass
                        
                        if not comp_added:
                            print(f"Loaded external component: {comp.get('type')} '{comp.get('nickname')}' ({comp_guid[:8]}...)")
    except Exception as e:
        print(f"Warning: Could not load external components: {e}")
        import traceback
        traceback.print_exc()
    
    # Find all output parameters that are sources for Panels or Number components
    # and ensure their parent components are in the graph
    panel_source_guids = [
        "20f5465a-8288-49ad-acd1-2eb24e1f8765",  # Panel "Distance between slats" source
    ]
    
    for panel_source_guid in panel_source_guids:
        # Check if it's an output parameter
        if panel_source_guid in output_params:
            source_info = output_params[panel_source_guid]
            parent_obj_guid = source_info['obj'].get('instance_guid')
            
            # If parent component is not in graph, add it
            if parent_obj_guid and parent_obj_guid not in graph:
                comp_info = get_component_full_info(parent_obj_guid)
                if comp_info:
                    graph[parent_obj_guid] = comp_info
                    print(f"Added Panel source component: {comp_info['obj'].get('type')} '{comp_info['obj'].get('nickname')}' ({parent_obj_guid[:8]}...)")
                    
                    # Also add its dependencies recursively
                    if comp_info['type'] == 'component':
                        for input_key, input_info in comp_info.get('inputs', {}).items():
                            for source in input_info.get('sources', []):
                                source_guid_conn = source.get('source_guid')
                                if source_guid_conn and source_guid_conn not in graph:
                                    # Try to add the source component
                                    if source_guid_conn in output_params:
                                        source_param_info = output_params[source_guid_conn]
                                        source_obj_guid = source_param_info['obj'].get('instance_guid')
                                        if source_obj_guid and source_obj_guid not in graph:
                                            source_comp_info = get_component_full_info(source_obj_guid)
                                            if source_comp_info:
                                                graph[source_obj_guid] = source_comp_info
                                                print(f"  Added dependency: {source_comp_info['obj'].get('type')} ({source_obj_guid[:8]}...)")
except Exception as e:
    print(f"Error adding Panel source components: {e}")

# Also add components whose output parameters are sources for components in the graph
# This ensures Vector XYZ, Amplitude, and Vector 2Pt components are included
try:
    # Find all output parameters that are sources for components in the graph
    # Do multiple passes to catch all dependencies
    max_passes = 5
    for pass_num in range(max_passes):
        added_any = False
        for comp_id, comp_info in list(graph.items()):
            if comp_info['type'] == 'component':
                for input_key, input_info in comp_info.get('inputs', {}).items():
                    for source in input_info.get('sources', []):
                        source_guid_conn = source.get('source_guid') or source.get('guid')
                        if source_guid_conn:
                            # Check if it's an output parameter
                            if source_guid_conn in output_params:
                                # Debug for Amplitude component Vector input
                                if comp_id == 'f54babb4-b955-42d1-aeb1-3b2192468fed' and input_key == 'param_input_0':
                                    print(f"DEBUG: Amplitude Vector input source: {source_guid_conn[:8]}...")
                                    print(f"  In output_params: True")
                                    parent_guid = output_params[source_guid_conn]['obj'].get('instance_guid')
                                    print(f"  Parent component: {parent_guid[:8] if parent_guid else 'N/A'}...")
                                    print(f"  Parent in graph: {parent_guid in graph if parent_guid else False}")
                                # This is an output parameter - get its parent component
                                source_param_info = output_params[source_guid_conn]
                                parent_obj_guid = source_param_info['obj'].get('instance_guid')
                                if parent_obj_guid and parent_obj_guid not in graph:
                                    # Add the parent component
                                    parent_comp_info = get_component_full_info(parent_obj_guid)
                                    if parent_comp_info:
                                        graph[parent_obj_guid] = parent_comp_info
                                        print(f"Added source component: {parent_comp_info['obj'].get('type')} '{parent_comp_info['obj'].get('nickname')}' ({parent_obj_guid[:8]}...)")
                                        added_any = True
                                        
                                        # Recursively add its dependencies
                                        if parent_comp_info['type'] == 'component':
                                            for parent_input_key, parent_input_info in parent_comp_info.get('inputs', {}).items():
                                                for parent_source in parent_input_info.get('sources', []):
                                                    parent_source_guid = parent_source.get('source_guid') or parent_source.get('guid')
                                                    if parent_source_guid and parent_source_guid in output_params:
                                                        parent_source_param_info = output_params[parent_source_guid]
                                                        parent_source_obj_guid = parent_source_param_info['obj'].get('instance_guid')
                                                        if parent_source_obj_guid and parent_source_obj_guid not in graph:
                                                            parent_source_comp_info = get_component_full_info(parent_source_obj_guid)
                                                            if parent_source_comp_info:
                                                                graph[parent_source_obj_guid] = parent_source_comp_info
                                                                print(f"  Added dependency: {parent_source_comp_info['obj'].get('type')} ({parent_source_obj_guid[:8]}...)")
                                                                added_any = True
                            else:
                                # Check if source_guid_conn is a component instance_guid directly
                                # (some sources point directly to components, not output params)
                                for key, obj in all_objects.items():
                                    if obj.get('instance_guid') == source_guid_conn and source_guid_conn not in graph:
                                        comp_info_source = get_component_full_info(source_guid_conn)
                                        if comp_info_source:
                                            graph[source_guid_conn] = comp_info_source
                                            print(f"Added direct source component: {comp_info_source['obj'].get('type')} '{comp_info_source['obj'].get('nickname')}' ({source_guid_conn[:8]}...)")
                                            added_any = True
                                            break
                                
                                # Also check if source_guid_conn is an output parameter GUID
                                # and add its parent component if not in graph
                                if source_guid_conn in output_params:
                                    source_param_info = output_params[source_guid_conn]
                                    parent_obj_guid = source_param_info['obj'].get('instance_guid')
                                    if parent_obj_guid and parent_obj_guid not in graph:
                                        parent_comp_info = get_component_full_info(parent_obj_guid)
                                        if parent_comp_info:
                                            graph[parent_obj_guid] = parent_comp_info
                                            print(f"Added parent of output param: {parent_comp_info['obj'].get('type')} '{parent_comp_info['obj'].get('nickname')}' ({parent_obj_guid[:8]}...)")
                                            added_any = True
        if not added_any:
            break  # No more components to add
except Exception as e:
    print(f"Error adding source components: {e}")
    import traceback
    traceback.print_exc()

# Special case: Point On Curve has Container-level Source that wasn't parsed
# Manually add List Item component (d89d47e0...) that produces output 8e8b33cf...
# Also ensure Deconstruct Brep (c78ea9c5...) is added as it's needed by List Item
try:
    point_on_curve_guid = '6ce8bcba-18ea-46fc-a145-b1c1b45c304f'
    list_item_output_guid = '8e8b33cf-5b52-4e6f-aca9-d798fd82b943'
    list_item_guid = 'd89d47e0-f858-44d9-8427-fdf2e3230954'
    deconstruct_brep_guid = 'c78ea9c5-07c7-443b-b188-078a6056dae8'
    edges_output_guid = '2ee35645-82e7-4c57-9c4e-2a801befbb03'
    
    if point_on_curve_guid in graph and list_item_guid not in graph:
        if list_item_output_guid in output_params:
            list_item_comp_info = get_component_full_info(list_item_guid)
            if list_item_comp_info:
                graph[list_item_guid] = list_item_comp_info
                print(f"Added List Item component for Point On Curve: {list_item_guid[:8]}...")
    
    # Ensure Deconstruct Brep is in graph (needed by List Item)
    if list_item_guid in graph and deconstruct_brep_guid not in graph:
        if edges_output_guid in output_params:
            deconstruct_brep_comp_info = get_component_full_info(deconstruct_brep_guid)
            if deconstruct_brep_comp_info:
                graph[deconstruct_brep_guid] = deconstruct_brep_comp_info
                print(f"Added Deconstruct Brep component for List Item: {deconstruct_brep_guid[:8]}...")
    
    # Ensure Mirror component is in graph (needed by Deconstruct Brep)
    mirror_output_guid = 'db399c50-741a-4670-a140-bd7eb7859fea'
    mirror_comp_guid = '47650d42-5fa9-44b3-b970-9f28b94bb031'  # Known Mirror instance_guid
    if deconstruct_brep_guid in graph:
        if mirror_output_guid in output_params:
            mirror_info = output_params[mirror_output_guid]
            mirror_comp_guid_from_param = mirror_info['obj'].get('instance_guid')
            if mirror_comp_guid_from_param and mirror_comp_guid_from_param not in graph:
                mirror_comp_info = get_component_full_info(mirror_comp_guid_from_param)
                if mirror_comp_info:
                    graph[mirror_comp_guid_from_param] = mirror_comp_info
                    print(f"Added Mirror component for Deconstruct Brep: {mirror_comp_guid_from_param[:8]}...")
        elif mirror_comp_guid in all_objects and mirror_comp_guid not in graph:
            # Mirror component is in all_objects but not in graph - add it directly
            mirror_comp_info = get_component_full_info(mirror_comp_guid)
            if mirror_comp_info:
                graph[mirror_comp_guid] = mirror_comp_info
                print(f"Added Mirror component for Deconstruct Brep (direct): {mirror_comp_guid[:8]}...")
        else:
            # Mirror output not in output_params - try to find Mirror component directly
            # Search for component that produces this output
            mirror_comp_guid_found = None
            for key, obj in all_objects.items():
                for param_key, param_info in obj.get('params', {}).items():
                    if param_key.startswith('param_output'):
                        param_guid = param_info.get('data', {}).get('InstanceGuid')
                        if param_guid == mirror_output_guid:
                            mirror_comp_guid_found = obj.get('instance_guid')
                            if mirror_comp_guid_found and mirror_comp_guid_found not in graph:
                                mirror_comp_info = get_component_full_info(mirror_comp_guid_found)
                                if mirror_comp_info:
                                    graph[mirror_comp_guid_found] = mirror_comp_info
                                    print(f"Added Mirror component for Deconstruct Brep (found in all_objects): {mirror_comp_guid_found[:8]}...")
                                    break
                if mirror_comp_guid_found and mirror_comp_guid_found in graph:
                    break
    
    # Ensure Rotate component is in graph (needed by Mirror)
    rotate_output_guid = '3560b89d-9e35-4df7-8bf6-1be7f9ab2e19'
    rotate_comp_guid = '5a77f108-b5a1-429b-9d22-0a14d7945abd'  # Known Rotate instance_guid
    if mirror_comp_guid in graph or (mirror_comp_guid in all_objects and '47650d42-5fa9-44b3-b970-9f28b94bb031' in graph):
        if rotate_output_guid in output_params:
            rotate_info = output_params[rotate_output_guid]
            rotate_comp_guid_from_param = rotate_info['obj'].get('instance_guid')
            if rotate_comp_guid_from_param and rotate_comp_guid_from_param not in graph:
                rotate_comp_info = get_component_full_info(rotate_comp_guid_from_param)
                if rotate_comp_info:
                    graph[rotate_comp_guid_from_param] = rotate_comp_info
                    print(f"Added Rotate component for Mirror: {rotate_comp_guid_from_param[:8]}...")
        elif rotate_comp_guid in all_objects and rotate_comp_guid not in graph:
            # Rotate component is in all_objects but not in graph - add it directly
            rotate_comp_info = get_component_full_info(rotate_comp_guid)
            if rotate_comp_info:
                graph[rotate_comp_guid] = rotate_comp_info
                print(f"Added Rotate component for Mirror (direct): {rotate_comp_guid[:8]}...")
        else:
            # Rotate output not in output_params - try to find Rotate component directly
            rotate_comp_guid_found = None
            for key, obj in all_objects.items():
                for param_key, param_info in obj.get('params', {}).items():
                    if param_key.startswith('param_output'):
                        param_guid = param_info.get('data', {}).get('InstanceGuid')
                        if param_guid == rotate_output_guid:
                            rotate_comp_guid_found = obj.get('instance_guid')
                            if rotate_comp_guid_found and rotate_comp_guid_found not in graph:
                                rotate_comp_info = get_component_full_info(rotate_comp_guid_found)
                                if rotate_comp_info:
                                    graph[rotate_comp_guid_found] = rotate_comp_info
                                    print(f"Added Rotate component for Mirror (found in all_objects): {rotate_comp_guid_found[:8]}...")
                                    break
                if rotate_comp_guid_found and rotate_comp_guid_found in graph:
                    break
    
    # Ensure Polygon component is in graph (needed by Rotate)
    polygon_output_guid = 'b94e42e9-9be1-439d-ad2e-9496cd8f4671'
    polygon_comp_guid = 'a2151ddb-9077-4065-90f3-e337cd983593'  # Known Polygon instance_guid
    if rotate_comp_guid in graph or (rotate_comp_guid in all_objects and '5a77f108-b5a1-429b-9d22-0a14d7945abd' in graph):
        if polygon_output_guid in output_params:
            polygon_info = output_params[polygon_output_guid]
            polygon_comp_guid_from_param = polygon_info['obj'].get('instance_guid')
            if polygon_comp_guid_from_param and polygon_comp_guid_from_param not in graph:
                polygon_comp_info = get_component_full_info(polygon_comp_guid_from_param)
                if polygon_comp_info:
                    graph[polygon_comp_guid_from_param] = polygon_comp_info
                    print(f"Added Polygon component for Rotate: {polygon_comp_guid_from_param[:8]}...")
        elif polygon_comp_guid in all_objects and polygon_comp_guid not in graph:
            # Polygon component is in all_objects but not in graph - add it directly
            polygon_comp_info = get_component_full_info(polygon_comp_guid)
            if polygon_comp_info:
                graph[polygon_comp_guid] = polygon_comp_info
                print(f"Added Polygon component for Rotate (direct): {polygon_comp_guid[:8]}...")
        else:
            # Polygon output not in output_params - try to find Polygon component directly
            polygon_comp_guid_found = None
            for key, obj in all_objects.items():
                for param_key, param_info in obj.get('params', {}).items():
                    if param_key.startswith('param_output'):
                        param_guid = param_info.get('data', {}).get('InstanceGuid')
                        if param_guid == polygon_output_guid:
                            polygon_comp_guid_found = obj.get('instance_guid')
                            if polygon_comp_guid_found and polygon_comp_guid_found not in graph:
                                polygon_comp_info = get_component_full_info(polygon_comp_guid_found)
                                if polygon_comp_info:
                                    graph[polygon_comp_guid_found] = polygon_comp_info
                                    print(f"Added Polygon component for Rotate (found in all_objects): {polygon_comp_guid_found[:8]}...")
                                    break
                if polygon_comp_guid_found and polygon_comp_guid_found in graph:
                    break
except Exception as e:
    print(f"Warning: Could not add components for Point On Curve chain: {e}")

# Topological sort
def topological_sort(graph: OrderedDict) -> list:
    """Sort components by dependency order."""
    # Build dependency map
    deps = {}
    for comp_id, comp in graph.items():
        deps[comp_id] = set()
        if comp['type'] == 'component':
            for input_key, input_info in comp.get('inputs', {}).items():
                for source in input_info.get('sources', []):
                    source_guid_conn = source.get('source_guid')
                    if source_guid_conn in graph:
                        deps[comp_id].add(source_guid_conn)
                    # Also add parent if source is output param
                    if source_guid_conn in output_params:
                        parent_obj_guid = output_params[source_guid_conn]['obj'].get('instance_guid')
                        if parent_obj_guid in graph:
                            deps[comp_id].add(parent_obj_guid)
    
    # Topological sort
    sorted_list = []
    remaining = set(graph.keys())
    
    while remaining:
        # Find nodes with no dependencies
        ready = [node for node in remaining if not deps.get(node, set()) & remaining]
        if not ready:
            # Circular dependency or missing deps - add remaining
            sorted_list.extend(remaining)
            break
        sorted_list.extend(ready)
        remaining -= set(ready)
    
    return sorted_list

sorted_components = topological_sort(graph)

print("=" * 80)
print("REBUILT COMPLETE COMPONENT GRAPH")
print("=" * 80)
print(f"\nTotal components: {len(graph)}")
print(f"Evaluation order: {len(sorted_components)} components\n")

# Save to file
with open('complete_component_graph.json', 'w') as f:
    graph_serializable = {}
    for comp_id, comp in graph.items():
        graph_serializable[comp_id] = comp
    json.dump({
        'components': graph_serializable,
        'sorted_order': sorted_components
    }, f, indent=2, default=str)

print("Saved to complete_component_graph.json")

# Print summary
print("\nComponent types in graph:")
types = set()
for comp_id, comp in graph.items():
    if comp['type'] == 'component':
        types.add(comp['obj']['type'])
    else:
        types.add('output_param')
print(f"  {', '.join(sorted(types))}")

