"""
Graph-based evaluator for Rotatingslats computation chain.
Uses topological sort to evaluate components in dependency order.
"""
import json
import math
from collections import defaultdict, OrderedDict
from typing import Dict, List, Any, Optional, Union
import gh_components
from gh_data_tree import DataTree, to_tree, from_tree, is_tree


# Hard-coded sun values as specified
SUN_VECTOR = [33219.837229, -61164.521016, 71800.722722]


def load_component_graph(filename: str = 'complete_component_graph.json') -> Dict:
    """Load the component dependency graph."""
    with open(filename, 'r') as f:
        return json.load(f)


def get_external_inputs() -> Dict[str, Any]:
    """
    Get external inputs (sliders, panels, constants).
    Load from external_inputs.json if available.
    """
    try:
        with open('external_inputs.json', 'r') as f:
            external_data = json.load(f)
        # Convert to simple GUID -> value mapping
        inputs = {}
        for param_guid, info in external_data.items():
            inputs[param_guid] = info['value']
            # Also map by object GUID
            obj_guid = info.get('object_guid')
            if obj_guid:
                inputs[obj_guid] = info['value']
        return inputs
    except FileNotFoundError:
        return {}


def resolve_input_value(comp_id: str, param_key: str, comp_info: Dict, 
                       evaluated: Dict[str, Any], 
                       all_objects: Dict, output_params: Dict, param_info: Optional[Dict] = None,
                       graph: Optional[Dict] = None, _visited: Optional[set] = None) -> Any:
    """
    Resolve the input value for a component parameter.
    Handles constants, external inputs, and connections from other components.
    """
    # Prevent infinite recursion
    if _visited is None:
        _visited = set()
    visit_key = (comp_id, param_key)
    if visit_key in _visited:
        return None  # Circular dependency detected - return None to break cycle
    _visited.add(visit_key)
    
    try:
        if param_info is None:
            param_info = comp_info['obj'].get('params', {}).get(param_key, {})
        param_guid = param_info.get('data', {}).get('InstanceGuid')
        
        # Check for sources FIRST - if there's a source connection, it overrides everything
        # This is critical: sources must be checked and FULLY resolved before external_inputs by parameter GUID
        sources = param_info.get('sources', [])
    
        # Special case: List Item Index parameter - if source is Value List, check if we need conversion
        # Some Value Lists output selected value, but when used as Index, might need length-1 conversion
        param_name = param_info.get('data', {}).get('NickName', '') or param_info.get('data', {}).get('Name', '')
        is_index_param = (param_name == 'Index')
        
        # If there are sources, resolve them COMPLETELY (including output_params) FIRST
        # This ensures source connections take priority over PersistentData and external_inputs by param GUID
        resolved_values = []  # Initialize outside if block to avoid UnboundLocalError
        if sources:
            # Handle multiple sources - resolve all and combine if needed
            for source in sources:
                # Try both 'guid' and 'source_guid' keys
                # The inputs structure uses 'source_guid', obj.params uses 'guid'
                source_guid = source.get('source_guid') or source.get('guid')
                if not source_guid:
                    continue
                
                # Resolve this source completely
                source_value = None
                # First check if source is an external input (slider, panel, etc.)
                external_inputs = get_external_inputs()
                
                if source_guid in external_inputs:
                    ext_value = external_inputs[source_guid]
                    if isinstance(ext_value, dict):
                        source_value = ext_value.get('value', ext_value)
                    else:
                        source_value = ext_value
                else:
                    # Also check by object_guid in external_inputs
                    for key, ext_val in external_inputs.items():
                        if isinstance(ext_val, dict) and ext_val.get('object_guid') == source_guid:
                            source_value = ext_val.get('value', ext_val)
                            break
                    # Also check if source_guid matches any key (case-insensitive or partial match)
                    if source_value is None:
                        for key, ext_val in external_inputs.items():
                            if key.lower() == source_guid.lower() or key == source_guid:
                                if isinstance(ext_val, dict):
                                    source_value = ext_val.get('value', ext_val)
                                else:
                                    source_value = ext_val
                                break
                
                # If not found in external inputs, check output params and evaluated components
                if source_value is None:
                    # Check if source is a Panel that has its own Source connection
                    source_obj = None
                    for key, obj in all_objects.items():
                        if obj.get('instance_guid') == source_guid:
                            source_obj = obj
                            break
                    
                    if source_obj and source_obj.get('type') == 'Panel':
                        # Panel has a Source connection - trace it
                        try:
                            import os
                            if os.path.exists('panel_sources.json'):
                                with open('panel_sources.json', 'r') as f:
                                    panel_sources = json.load(f)
                                
                                panel_source_guid = panel_sources.get(source_guid, {}).get('source_guid')
                                if panel_source_guid and panel_source_guid in output_params:
                                    source_info = output_params[panel_source_guid]
                                    source_obj_guid = source_info['obj'].get('instance_guid')
                                    if source_obj_guid and source_obj_guid in evaluated:
                                        comp_outputs = evaluated.get(source_obj_guid, {})
                                        if isinstance(comp_outputs, dict):
                                            source_param_name = source_info['param_info'].get('data', {}).get('NickName', '')
                                            for key in [source_param_name, 'Result', 'Value', 'Output', 'Vector']:
                                                if key in comp_outputs:
                                                    source_value = comp_outputs[key]
                                                    break
                                            if source_value is None and comp_outputs:
                                                source_value = list(comp_outputs.values())[0]
                                        else:
                                            source_value = comp_outputs
                        except Exception:
                            pass
                
                # Check if it's an output parameter
                if source_value is None and source_guid in output_params:
                    source_info = output_params[source_guid]
                    source_obj_guid = source_info['obj'].get('instance_guid')
                    # Debug: Always show for Polygon output param
                    if source_guid[:8] == 'b94e42e9':
                        print(f"  DEBUG [RESOLVE] Found Polygon output param: source_guid={source_guid[:8]}..., source_obj_guid={source_obj_guid[:8] if source_obj_guid else 'None'}..., in_evaluated={source_obj_guid in evaluated if source_obj_guid else False}")
                    if source_obj_guid in evaluated:
                        comp_outputs = evaluated.get(source_obj_guid, {})
                        if isinstance(comp_outputs, dict):
                            source_param_name = source_info['param_info'].get('data', {}).get('NickName', '')
                            # Check if source component is MD Slider - if so, get the full point value
                            source_obj = source_info.get('obj', {})
                            source_comp_type = source_obj.get('type', '')
                            
                            # Debug: Always show for Polygon output param or when vertices are present
                            if source_guid[:8] == 'b94e42e9' or source_comp_type == 'Polygon' or 'vertices' in comp_outputs:
                                print(f"  DEBUG [RESOLVE] source_guid={source_guid[:8]}..., source_obj_guid={source_obj_guid[:8] if source_obj_guid else 'None'}..., source_comp_type='{source_comp_type}', comp_outputs keys={list(comp_outputs.keys())}, has_vertices={'vertices' in comp_outputs}, source_param_name='{source_param_name}'")
                            
                            # CRITICAL: Check if comp_outputs itself is a geometry dict FIRST
                            # This handles components like Polygon that return geometry dicts directly
                            # Must check BEFORE trying to extract specific keys, to avoid getting string values like 'polygon_geometry'
                            has_geometry_keys = 'vertices' in comp_outputs or 'points' in comp_outputs or 'corners' in comp_outputs
                            if has_geometry_keys:
                                # This is a geometry dict - use it directly (don't extract a string value)
                                # This prevents extracting 'polygon_geometry' string when Polygon component returns dict with 'vertices'
                                source_value = comp_outputs
                                # Debug output for Polygon component
                                if source_comp_type == 'Polygon':
                                    print(f"  DEBUG [RESOLVE] Polygon ({source_obj_guid[:8]}...): Using full geometry dict with {len(comp_outputs.get('vertices', []))} vertices")
                            elif source_comp_type == 'MD Slider' and 'Point' in comp_outputs:
                                # MD Slider with point3d - return the full point
                                source_value = comp_outputs['Point']
                            # For Polar Array and similar components, prioritize 'Geometry' key
                            # This ensures correct extraction when output param name is 'Geometry'
                            elif source_param_name == 'Geometry' and 'Geometry' in comp_outputs:
                                source_value = comp_outputs['Geometry']
                            else:
                                # Debug: Why didn't we use the geometry dict?
                                if source_comp_type == 'Polygon':
                                    print(f"  DEBUG [RESOLVE] Polygon ({source_obj_guid[:8]}...): has_geometry_keys=False, will try other extraction methods")
                                # Try to find the param name key or other common keys
                                for key in [source_param_name, 'Geometry', 'Result', 'Value', 'Output', 'Vector', 'Point', 'Values']:
                                    if key in comp_outputs:
                                        source_value = comp_outputs[key]
                                        break
                                # If still None, fallback to first value
                                if source_value is None and comp_outputs:
                                    source_value = list(comp_outputs.values())[0]
                            
                            # Special handling: If source is Value List and target is List Item Index
                            # Value List outputs a list like [4.0], extract the first value
                            if source_value is not None and isinstance(source_value, list) and len(source_value) > 0:
                                # Check if source component is Value List
                                source_obj = source_info.get('obj', {})
                                if source_obj.get('type') == 'Value List':
                                    # Value List outputs selected value as list, extract it
                                    source_value = source_value[0] if len(source_value) > 0 else 0
                            
                            # Convert trees to lists for components that don't handle trees
                            # EXCEPT for Polar Array, List Item, Move, and Area which need trees
                            if source_value is not None and is_tree(source_value):
                                # Check if target component needs trees
                                target_comp_type = comp_info.get('obj', {}).get('type', '')
                                if target_comp_type not in ['Polar Array', 'List Item', 'Move', 'Area']:
                                    source_value = from_tree(source_value)
                        else:
                            source_value = comp_outputs
                            # Convert trees to lists
                            # EXCEPT for Polar Array, List Item, Move, and Area which need trees
                            if is_tree(source_value):
                                target_comp_type = comp_info.get('obj', {}).get('type', '')
                                if target_comp_type not in ['Polar Array', 'List Item', 'Move', 'Area']:
                                    source_value = from_tree(source_value)
                    elif source_obj_guid:
                        # Parent component not yet evaluated - try to evaluate it now
                        # This handles cases where dependencies aren't evaluated in order
                        try:
                            # Load graph if not provided
                            if graph is None:
                                try:
                                    graph_data = load_component_graph('complete_component_graph.json')
                                    graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data
                                except Exception:
                                    graph = {}
                            
                            # Find the component in the graph or all_objects
                            parent_comp = graph.get(source_obj_guid)
                            if not parent_comp:
                                # Try to find in all_objects
                                for obj_key, obj in all_objects.items():
                                    if obj.get('instance_guid') == source_obj_guid:
                                        # Convert to graph format
                                        parent_comp = {'obj': obj, 'inputs': {}, 'outputs': {}}
                                        # Try to get inputs from graph if available
                                        if graph:
                                            for comp_id, comp_data in graph.items():
                                                if isinstance(comp_data, dict) and comp_data.get('obj', {}).get('instance_guid') == source_obj_guid:
                                                    parent_comp = comp_data
                                                    break
                                        break
                            
                            if parent_comp:
                                # Recursively evaluate the parent component (this will handle dependencies)
                                # Use a simple recursive evaluation
                                def eval_parent_recursive(comp_guid, visited=None):
                                    if visited is None:
                                        visited = set()
                                    if comp_guid in visited or comp_guid in evaluated:
                                        return
                                    visited.add(comp_guid)
                                    
                                    comp = graph.get(comp_guid)
                                    if not comp:
                                        # Try all_objects
                                        for obj_key, obj in all_objects.items():
                                            if obj.get('instance_guid') == comp_guid:
                                                comp = {'obj': obj, 'inputs': {}, 'outputs': {}}
                                                break
                                    if not comp:
                                        return
                                    
                                    # Evaluate dependencies first
                                    # Check both 'inputs' structure and 'obj.params' structure
                                    inputs_to_check = comp.get('inputs', {})
                                    if not inputs_to_check and 'obj' in comp:
                                        # Try to build inputs from obj.params
                                        obj_params = comp['obj'].get('params', {})
                                        comp['inputs'] = {}
                                        for param_key, param_data in obj_params.items():
                                            if param_key.startswith('param_input'):
                                                param_name = param_data.get('data', {}).get('NickName', '')
                                                if param_name:
                                                    comp['inputs'][param_key] = {
                                                        'name': param_name,
                                                        'sources': param_data.get('sources', [])
                                                    }
                                    inputs_to_check = comp.get('inputs', {})
                                    for input_key, input_info in inputs_to_check.items():
                                        sources = input_info.get('sources', [])
                                        if not sources and 'obj' in comp:
                                            # Try to get sources from obj.params
                                            param_data = comp['obj'].get('params', {}).get(input_key, {})
                                            sources = param_data.get('sources', [])
                                        for dep_source in sources:
                                            dep_obj_guid = dep_source.get('source_obj_guid')
                                            if dep_obj_guid and dep_obj_guid not in evaluated:
                                                eval_parent_recursive(dep_obj_guid, visited)
                                            
                                            # Also check if source_guid is an output parameter that needs parent evaluation
                                            dep_source_guid = dep_source.get('source_guid')
                                            if dep_source_guid and dep_source_guid in output_params:
                                                dep_parent_guid = output_params[dep_source_guid]['obj'].get('instance_guid')
                                                if dep_parent_guid and dep_parent_guid not in evaluated:
                                                    eval_parent_recursive(dep_parent_guid, visited)
                                    
                                    # Evaluate this component
                                    try:
                                        result = evaluate_component(comp_guid, comp, evaluated, all_objects, output_params, graph=graph)
                                        evaluated[comp_guid] = result
                                    except Exception as eval_err:
                                        pass  # If evaluation fails, continue
                                
                                eval_parent_recursive(source_obj_guid)
                                
                                # Now try to get the value again
                                if source_obj_guid in evaluated:
                                    comp_outputs = evaluated.get(source_obj_guid, {})
                                    if isinstance(comp_outputs, dict):
                                        source_param_name = source_info['param_info'].get('data', {}).get('NickName', '')
                                        for key in [source_param_name, 'Result', 'Value', 'Output', 'Vector']:
                                            if key in comp_outputs:
                                                source_value = comp_outputs[key]
                                                break
                                        if source_value is None and comp_outputs:
                                            source_value = list(comp_outputs.values())[0]
                                    else:
                                        source_value = comp_outputs
                        except Exception as e:
                            pass  # If evaluation fails, continue without this source
                
                # Check if source_guid is a component in all_objects
                if source_value is None:
                    source_component = None
                    for key, obj in all_objects.items():
                        if obj.get('instance_guid') == source_guid:
                            source_component = obj
                            break
                    
                    if source_component and source_guid in evaluated:
                        comp_outputs = evaluated[source_guid]
                        if isinstance(comp_outputs, dict):
                            for key in ['Result', 'Value', 'Output', 'Line', 'Vector', 'Point', 'Plane', 'Normal', 'Angle', 'Degrees']:
                                if key in comp_outputs:
                                    source_value = comp_outputs[key]
                                    break
                            if source_value is None and comp_outputs:
                                source_value = list(comp_outputs.values())[0]
                        else:
                            source_value = comp_outputs
                    elif source_guid in evaluated:
                        # Direct evaluation result
                        result = evaluated[source_guid]
                        if isinstance(result, dict):
                            for key in ['Result', 'Value', 'Output', 'Line', 'Vector', 'Point', 'Plane', 'Normal', 'Angle', 'Degrees']:
                                if key in result:
                                    source_value = result[key]
                                    break
                            if source_value is None and result:
                                source_value = list(result.values())[0]
                        else:
                            source_value = result
                    
                    # Final fallback: if source_guid is directly in evaluated (for Number components, etc.)
                    if source_value is None and source_guid in evaluated:
                        source_value = evaluated[source_guid]
                        # If it's a dict, extract the first value
                        if isinstance(source_value, dict):
                            for key in ['Result', 'Value', 'Output', 'Line', 'Vector', 'Point', 'Plane', 'Normal', 'Angle', 'Degrees']:
                                if key in source_value:
                                    source_value = source_value[key]
                                    break
                            if isinstance(source_value, dict) and source_value:
                                source_value = list(source_value.values())[0]
            
            if source_value is not None:
                resolved_values.append(source_value)
        
        # If we resolved any sources, return them (or combined if multiple)
        if resolved_values:
            if len(resolved_values) == 1:
                return resolved_values[0]
            else:
                # Multiple sources - combine them
                # For vectors, add them together
                if all(isinstance(v, list) and len(v) == 3 for v in resolved_values):
                    # All are 3-element vectors - add them
                    combined = [0.0, 0.0, 0.0]
                    for v in resolved_values:
                        combined[0] += v[0]
                        combined[1] += v[1]
                        combined[2] += v[2]
                    return combined
                elif len(resolved_values) > 1 and isinstance(resolved_values[0], list) and len(resolved_values[0]) == 3:
                    # First is a vector, rest might be scalars or vectors
                    single_vector = resolved_values[0]
                    list_of_vectors = resolved_values[1:]
                    if all(isinstance(v, list) and len(v) == 3 for v in list_of_vectors):
                        combined = [[v[0] + single_vector[0], v[1] + single_vector[1], v[2] + single_vector[2]] 
                                   for v in list_of_vectors]
                        return combined
                else:
                    # Return as list for components that accept multiple inputs
                    return resolved_values
        
        # Check external_inputs by parameter GUID (only if no sources or sources didn't resolve)
        # This allows overriding default/placeholder values with real values
        # BUT: For Plane parameters, we'll check PersistentData first since it has the correct plane structure
        external_inputs = get_external_inputs()
        is_plane_param = param_name == 'Plane'
        
        if param_guid and param_guid in external_inputs and not is_plane_param:
            ext_value = external_inputs[param_guid]
            if isinstance(ext_value, dict):
                ext_val = ext_value.get('value', ext_value)
            else:
                ext_val = ext_value
            # Only use external input if it's not empty/whitespace
            if ext_val is not None and not (isinstance(ext_val, str) and not ext_val.strip()):
                return ext_val
        
        # Check for constant value (from persistent_values or values) ONLY if no sources
        # persistent_values can be in param_info directly or in param_info['data']
        persistent_values = param_info.get('persistent_values', [])
        if not persistent_values and 'data' in param_info:
            persistent_values = param_info['data'].get('persistent_values', [])
        values = param_info.get('values', [])
        if not values and 'data' in param_info:
            values = param_info['data'].get('values', [])
        
        # Try to extract plane from external_inputs or PersistentData if this is a Plane parameter
        # This handles gh_plane type in PersistentData
        if (not sources or len(sources) == 0):
            param_name = param_info.get('data', {}).get('NickName', '') or param_info.get('data', {}).get('Name', '')
            if param_name == 'Plane' and param_guid:
                # Try to extract plane from external_inputs (if it was extracted from GHX)
                if param_guid in external_inputs:
                    ext_value = external_inputs[param_guid]
                    if isinstance(ext_value, dict):
                        plane_value = ext_value.get('value', ext_value)
                        # Check if it's a plane dict (has 'origin' key)
                        if isinstance(plane_value, dict) and 'origin' in plane_value:
                            return plane_value
        
        # Handle persistent_values
        persistent_vector = None
        persistent_plane = None
        if persistent_values:
            # Check if persistent_values contains a vector (JSON string) or plane (JSON object)
            for pv in persistent_values:
                if isinstance(pv, str):
                    pv_stripped = pv.strip()
                    # Check if it's a JSON array (vector)
                    if pv_stripped.startswith('[') and pv_stripped.endswith(']'):
                        try:
                            parsed = json.loads(pv_stripped)
                            if isinstance(parsed, list) and len(parsed) == 3:
                                persistent_vector = parsed
                                break
                        except (json.JSONDecodeError, ValueError):
                            pass
                    # Check if it's a JSON object (plane dict)
                    elif pv_stripped.startswith('{') and pv_stripped.endswith('}'):
                        try:
                            parsed = json.loads(pv_stripped)
                            if isinstance(parsed, dict) and 'origin' in parsed and 'x_axis' in parsed:
                                persistent_plane = parsed
                                break
                        except (json.JSONDecodeError, ValueError):
                            pass
        
        # Only use persistent_values if there are NO sources
        # IMPORTANT: Check if sources list is actually non-empty (not just truthy)
        if (not sources or len(sources) == 0) and persistent_values:
            # If we have a persistent plane, return it
            if persistent_plane:
                return persistent_plane
            # If we have a persistent vector, return it
            if persistent_vector:
                return persistent_vector
            # Otherwise, convert string to appropriate type
            val_str = persistent_values[0].strip()
            if val_str and val_str not in ['', '\n                                      ']:
                try:
                    if '.' in val_str:
                        return float(val_str)
                    else:
                        return int(val_str)
                except ValueError:
                    # Boolean or string
                    if val_str.lower() == 'true':
                        return True
                    elif val_str.lower() == 'false':
                        return False
                    return val_str
        elif (not sources or len(sources) == 0) and values:
            val_str = values[0].strip() if isinstance(values[0], str) else str(values[0]).strip()
            if val_str and val_str not in ['', '\n                                      ']:
                # Check for boolean first
                val_lower = val_str.lower()
                if val_lower == 'true':
                    return True
                elif val_lower == 'false':
                    return False
                # Then try numeric conversion
                try:
                    if '.' in val_str:
                        return float(val_str)
                    else:
                        return int(val_str)
                except ValueError:
                    # Return as string if not numeric
                    return val_str
        
        # Sources were already fully resolved above if they existed
        # If we get here, there were no sources or they couldn't be resolved
        # Continue with external_inputs by param GUID and PersistentData fallback
        
        # Check external inputs by component GUID
        external_inputs = get_external_inputs()
        if comp_id in external_inputs:
            return external_inputs[comp_id]
        
        # Default: return None (will cause error if required)
        return None
    
    finally:
        # Clean up visited set on exit to allow re-evaluation if needed
        if _visited and visit_key in _visited:
            _visited.remove(visit_key)
    
    # Default: return None (will cause error if required)
    return None


def debug_tree_structure(comp_id: str, comp_type: str, result: Any, output_key: str = 'Geometry') -> None:
    """Debug helper to print tree structure at component output."""
    from gh_data_tree import is_tree, DataTree
    
    # Get component GUID for identification
    comp_instance_guid = comp_id[:8] if len(comp_id) >= 8 else comp_id
    
    # Check if result is a dict with the output key
    if isinstance(result, dict) and output_key in result:
        value = result[output_key]
    else:
        value = result
    
    # Check if value is a tree
    if is_tree(value):
        tree = value
        paths = tree.paths()
        print(f"  DEBUG [TREE] {comp_type} ({comp_instance_guid}...): {len(paths)} branches")
        for path in sorted(paths)[:5]:  # Show first 5 branches
            items = tree.get_branch(path)
            print(f"    Path {path}: {len(items)} items")
    elif isinstance(value, list):
        print(f"  DEBUG [LIST] {comp_type} ({comp_instance_guid}...): {len(value)} items")
    else:
        print(f"  DEBUG [SCALAR] {comp_type} ({comp_instance_guid}...): {type(value).__name__}")


def evaluate_component(comp_id: str, comp_info: Dict, evaluated: Dict[str, Any],
                      all_objects: Dict, output_params: Dict, graph: Optional[Dict] = None) -> Any:
    """
    Evaluate a single component given its inputs.
    Returns the component's output(s).
    """
    comp_type = comp_info['obj']['type']
    instance_guid = comp_info.get('instance_guid') or comp_id
    
    # Handle Panel components separately (they don't need evaluation)
    if comp_type == 'Panel':
        return None
    
    # Get component function
    if comp_type not in gh_components.COMPONENT_FUNCTIONS:
        raise ValueError(f"Unknown component type: {comp_type} (GUID: {comp_id[:8]}...)")
    
    func = gh_components.COMPONENT_FUNCTIONS[comp_type]
    
    # Build inputs from obj.params if inputs key is missing
    if 'inputs' not in comp_info or not comp_info.get('inputs'):
        obj_params = comp_info['obj'].get('params', {})
        comp_info['inputs'] = {}
        for param_key, param_data in obj_params.items():
            if param_key.startswith('param_input'):
                param_name = param_data.get('data', {}).get('NickName', '') or param_data.get('data', {}).get('Name', '')
                if param_name:
                    # Convert sources from obj.params format (guid) to inputs format (source_guid)
                    sources = []
                    for src in param_data.get('sources', []):
                        if isinstance(src, dict):
                            # Convert guid to source_guid
                            source_guid = src.get('guid') or src.get('source_guid')
                            if source_guid:
                                sources.append({
                                    'source_guid': source_guid,
                                    'guid': source_guid,  # Keep both for compatibility
                                    'index': src.get('index', 0)
                                })
                    comp_info['inputs'][param_key] = {
                        'name': param_name,
                        'sources': sources
                    }
    
    # Resolve inputs
    inputs = {}
    for param_key, input_info in comp_info.get('inputs', {}).items():
        param_name = input_info['name']
        # Get param_info from both inputs structure and obj.params structure
        # The inputs structure has sources with 'source_guid', obj.params has sources with 'guid'
        param_info_from_inputs = input_info
        param_info_from_obj = comp_info['obj'].get('params', {}).get(param_key, {})
        # Merge them, but prefer sources from inputs (they have source_guid which is what we need)
        param_info = param_info_from_obj.copy()
        param_info.update(param_info_from_inputs)
        # Always use sources from inputs if available (they have source_guid)
        if 'sources' in param_info_from_inputs and param_info_from_inputs['sources']:
            param_info['sources'] = param_info_from_inputs['sources']
        # Make sure persistent_values and values from obj.params are preserved
        if 'data' in param_info_from_obj:
            data_dict = param_info_from_obj['data']
            if 'persistent_values' in data_dict:
                param_info['persistent_values'] = data_dict['persistent_values']
            if 'values' in param_info_from_obj:
                param_info['values'] = param_info_from_obj['values']
        value = resolve_input_value(instance_guid, param_key, comp_info, 
                                   evaluated, all_objects, output_params, param_info=param_info, graph=graph)
        inputs[param_name] = value
    
    # Call component function
    # Map input names to function arguments based on component type
    try:
        # Enhanced error logging wrapper
        comp_instance_guid = comp_info.get('obj', {}).get('instance_guid', '') or comp_id
        comp_nickname = comp_info.get('obj', {}).get('nickname', '')
        
        if comp_type == 'Number Slider':
            # Number Slider expects 'value' input
            value = inputs.get('Value') or inputs.get('value') or inputs.get('Number')
            if value is None:
                # Try to get from persistent_values or external_inputs
                param_info = comp_info['obj'].get('params', {}).get('param_input_0', {})
                persistent_values = param_info.get('data', {}).get('persistent_values', [])
                if persistent_values:
                    value = persistent_values[0] if isinstance(persistent_values, list) else persistent_values
                else:
                    # Check external_inputs
                    external_inputs = get_external_inputs()
                    if comp_instance_guid in external_inputs:
                        value = external_inputs[comp_instance_guid]
                    elif instance_guid in external_inputs:
                        value = external_inputs[instance_guid]
            if value is None:
                raise ValueError(f"Number Slider component missing value input. Available inputs: {list(inputs.keys())}")
            result = func(value)
            return {'Value': result} if isinstance(result, (int, float)) else {'Result': result}
        
        elif comp_type == 'Angle':
            vectorA = inputs.get('Vector A') or inputs.get('vectorA') or inputs.get('vector_a')
            vectorB = inputs.get('Vector B') or inputs.get('vectorB') or inputs.get('vector_b')
            plane = inputs.get('Plane') or inputs.get('plane')
            # Only return default if inputs are truly missing (not in inputs dict)
            has_vectorA = 'Vector A' in inputs or 'vectorA' in inputs or 'vector_a' in inputs
            has_vectorB = 'Vector B' in inputs or 'vectorB' in inputs or 'vector_b' in inputs
            if not has_vectorA and not has_vectorB:
                return {'Angle': 0.0, 'Reflex': 0.0}
            # Convert vectors to lists if they're dicts or other types
            if isinstance(vectorA, dict):
                vectorA = vectorA.get('Vector', vectorA.get('Normal', [0.0, 0.0, 0.0]))
            if isinstance(vectorB, dict):
                vectorB = vectorB.get('Vector', vectorB.get('Normal', [0.0, 0.0, 0.0]))
            if not isinstance(vectorA, list) or len(vectorA) < 3:
                vectorA = [0.0, 0.0, 0.0]
            if not isinstance(vectorB, list) or len(vectorB) < 3:
                vectorB = [0.0, 0.0, 0.0]
            angle, reflex = func(vectorA, vectorB, plane)
            return {'Angle': angle, 'Reflex': reflex}
        
        elif comp_type == 'Degrees':
            radians = inputs.get('Radians') or inputs.get('radians')
            # Only return default if input is truly missing (not in inputs dict)
            if 'Radians' not in inputs and 'radians' not in inputs:
                return {'Degrees': 0.0}
            # Use 0.0 as default if None
            if radians is None:
                radians = 0.0
            degrees = func(radians)
            return {'Degrees': degrees}
        
        elif comp_type == 'Line':
            start = inputs.get('Start Point') or inputs.get('Start') or inputs.get('Point A')
            end = inputs.get('End Point') or inputs.get('End') or inputs.get('Point B')
            # Only return None if inputs are truly missing (not in inputs dict)
            has_start = 'Start Point' in inputs or 'Start' in inputs or 'Point A' in inputs
            has_end = 'End Point' in inputs or 'End' in inputs or 'Point B' in inputs
            if not has_start and not has_end:
                return {'Line': None}
            # If only one is missing, use [0,0,0] as default
            if start is None:
                start = [0.0, 0.0, 0.0]
            if end is None:
                end = [0.0, 0.0, 0.0]
            line = func(start, end)
            return {'Line': line}
        
        elif comp_type == 'Move':
            geometry = inputs.get('Geometry')
            motion = inputs.get('Motion')
            
            # Debug logging for Move components
            move_instance_guid = comp_info.get('obj', {}).get('instance_guid', '')
            move_nickname = comp_info.get('obj', {}).get('nickname', '')
            
            # Check if inputs exist in the inputs dict
            has_geometry = 'Geometry' in inputs
            has_motion = 'Motion' in inputs
            
            # Only return None if inputs are truly missing (not in inputs dict)
            if not has_geometry and not has_motion:
                print(f"  [MOVE DEBUG] {move_nickname} ({move_instance_guid[:8]}...): No Geometry or Motion inputs found")
                return {'Geometry': None, 'Transform': None}
            
            if not has_geometry:
                print(f"  [MOVE DEBUG] {move_nickname} ({move_instance_guid[:8]}...): Geometry input missing")
                return {'Geometry': None, 'Transform': None}
            
            if not has_motion:
                print(f"  [MOVE DEBUG] {move_nickname} ({move_instance_guid[:8]}...): Motion input missing")
                return {'Geometry': None, 'Transform': None}
            
            # Log what we received
            if geometry is None:
                print(f"  [MOVE DEBUG] {move_nickname} ({move_instance_guid[:8]}...): Geometry is None (resolved but None)")
            else:
                geom_type = type(geometry).__name__
                if is_tree(geometry):
                    paths = geometry.paths()
                    print(f"  [MOVE DEBUG] {move_nickname} ({move_instance_guid[:8]}...): Geometry is DataTree with {len(paths)} branches")
                elif isinstance(geometry, list):
                    print(f"  [MOVE DEBUG] {move_nickname} ({move_instance_guid[:8]}...): Geometry is list with {len(geometry)} items")
                else:
                    print(f"  [MOVE DEBUG] {move_nickname} ({move_instance_guid[:8]}...): Geometry is {geom_type}")
            
            if motion is None:
                print(f"  [MOVE DEBUG] {move_nickname} ({move_instance_guid[:8]}...): Motion is None (resolved but None)")
            else:
                motion_type = type(motion).__name__
                if isinstance(motion, list):
                    if len(motion) > 0 and isinstance(motion[0], list):
                        print(f"  [MOVE DEBUG] {move_nickname} ({move_instance_guid[:8]}...): Motion is list of {len(motion)} vectors")
                    else:
                        print(f"  [MOVE DEBUG] {move_nickname} ({move_instance_guid[:8]}...): Motion is single vector: {motion}")
                else:
                    print(f"  [MOVE DEBUG] {move_nickname} ({move_instance_guid[:8]}...): Motion is {motion_type}: {motion}")
            
            # For first Move: convert OUTPUT flat list of rectangles to tree (one rectangle per branch)
            # This ensures Polar Array receives a tree with 10 branches (one per slat)
            first_move_guids = [
                'ddb9e6ae-7d3e-41ae-8c75-fc726c984724',  # Original GUID
                '47af807c-369d-4bd2-bbbb-d53a4605f8e6',  # Actual Move1 output GUID
                '3d373d1a-021a-4c74-ac63-8939e6ac5429',  # Alternative comp_id
                'dfbbd4a2-021a-4c74-ac63-8939e6ac5429'  # Alternative instance_guid
            ]
            is_first_move = (move_instance_guid in first_move_guids or 
                           comp_id in first_move_guids)
            
            moved, transform = func(geometry, motion)
            
            # Convert Move1 OUTPUT to tree: list of 10 rectangles → tree with 10 branches
            if is_first_move and isinstance(moved, list) and len(moved) > 0:
                # Check if it's a list of rectangles (not already a tree)
                if not is_tree(moved):
                    # Convert flat list to tree: each rectangle becomes its own branch
                    geometry_tree = DataTree()
                    for i, rect in enumerate(moved):
                        geometry_tree.set_branch((i,), [rect])
                    moved = geometry_tree
                    paths = geometry_tree.paths()
                    print(f"  DEBUG [TREE-STRUCT] Move1 ({comp_id[:8]}...): converted output list of {len(moved) if not hasattr(moved, 'paths') else 'N/A'} items to tree with {len(paths)} branches")
                elif hasattr(moved, 'paths'):
                    paths = moved.paths()
                    print(f"  DEBUG [TREE-STRUCT] Move1 ({comp_id[:8]}...): output already a tree with {len(paths)} branches")
            
            return {'Geometry': moved, 'Transform': transform}
        
        elif comp_type == 'Polar Array':
            geometry = inputs.get('Geometry')
            plane = inputs.get('Plane')
            count = inputs.get('Count')
            angle = inputs.get('Angle')
            if geometry is None:
                raise ValueError(f"Polar Array component missing Geometry input")
            if plane is None:
                raise ValueError(f"Polar Array component missing Plane input")
            if count is None:
                raise ValueError(f"Polar Array component missing Count input")
            if angle is None:
                raise ValueError(f"Polar Array component missing Angle input")
            
            # Polar Array - check if it's the Rotatingslats chain component
            pa_instance_guid = comp_info.get('obj', {}).get('instance_guid', '')
            polar_array_guid = '7ad636cc-e506-4f77-bb82-4a86ba2a3fea'
            is_rotatingslats_pa = pa_instance_guid == polar_array_guid
            
            array = func(geometry, plane, count, angle, use_tree=True)
            
            if is_rotatingslats_pa and is_tree(array):
                paths = array.paths()
                print(f"  [ROTATINGSLATS] Polar Array: output {len(paths)} branches")
            
            return {'Geometry': array}
        
        elif comp_type == 'List Item':
            list_data = inputs.get('List')
            index = inputs.get('Index')
            wrap = inputs.get('Wrap', False)
            if list_data is None:
                raise ValueError(f"List Item component missing List input")
            if index is None:
                raise ValueError(f"List Item component missing Index input")
            
            # List Item - check if it's the Rotatingslats chain component
            li_instance_guid = comp_info.get('obj', {}).get('instance_guid', '')
            list_item_guid = '27933633-dbab-4dc0-a4a2-cfa309c03c45'
            is_rotatingslats_li = li_instance_guid == list_item_guid
            
            item = func(list_data, index, wrap)
            
            if is_rotatingslats_li and is_tree(item):
                paths = item.paths()
                print(f"  [ROTATINGSLATS] List Item: output {len(paths)} branches")
            
            return {'Item': item}
        
        elif comp_type == 'Area':
            geometry = inputs.get('Geometry')
            if geometry is None:
                # Return None if Geometry is missing (allows evaluation to continue)
                return {'Area': None, 'Centroid': None}
            
            # Area - check if it's the Rotatingslats chain component
            area_instance_guid = comp_info.get('obj', {}).get('instance_guid', '')
            area_guid = '3bd2c1d3-149d-49fb-952c-8db272035f9e'
            is_rotatingslats_area = area_instance_guid == area_guid
            
            result = func(geometry)
            
            # Output summary for Rotatingslats Area component
            if is_rotatingslats_area and isinstance(result, dict):
                centroids = result.get('Centroid')
                if is_tree(centroids):
                    paths = centroids.paths()
                    print(f"  [ROTATINGSLATS] Area: output {len(paths)} centroid branches")
                    if paths:
                        first_path = sorted(paths)[0]
                        first_centroid = centroids.get_branch(first_path)
                        if first_centroid and len(first_centroid) > 0:
                            print(f"    First branch centroid Y: {first_centroid[0][1] if isinstance(first_centroid[0], list) and len(first_centroid[0]) > 1 else 'N/A'}")
                elif isinstance(centroids, list) and len(centroids) > 0:
                    print(f"  [ROTATINGSLATS] Area: output {len(centroids)} centroids, first Y: {centroids[0][1] if isinstance(centroids[0], list) and len(centroids[0]) > 1 else 'N/A'}")
            
            return result
        
        elif comp_type == 'Rectangle 2Pt':
            plane = inputs.get('Plane')
            pointA = inputs.get('Point A')
            pointB = inputs.get('Point B')
            radius = inputs.get('Radius', 0.0)
            if pointA is None or pointB is None:
                raise ValueError(f"Rectangle 2Pt component missing inputs: Point A={pointA}, Point B={pointB}")
            rectangle, length = func(plane, pointA, pointB, radius)
            return {'Rectangle': rectangle, 'Length': length}
        
        elif comp_type == 'Value List':
            values = inputs.get('Values', [])
            if not values:
                # Try to get from PersistentData
                param_info = comp_info['obj'].get('params', {}).get('param_input_0', {})
                persistent_values = param_info.get('persistent_values', [])
                if persistent_values:
                    # Parse persistent values
                    import json
                    try:
                        values = json.loads(persistent_values[0]) if isinstance(persistent_values[0], str) else persistent_values
                    except:
                        values = persistent_values
            result = func(values)
            return {'Values': result}
        
        elif comp_type == 'Amplitude':
            vector = inputs.get('Vector')
            amplitude = inputs.get('Amplitude')
            if vector is None:
                # Return None if Vector is missing (allows evaluation to continue)
                return {'Vector': None}
            if amplitude is None:
                raise ValueError(f"Amplitude component missing Amplitude input")
            result = func(vector, amplitude)
            return {'Vector': result}
        
        elif comp_type == 'Vector 2Pt':
            pointA = inputs.get('Point A') or inputs.get('PointA') or inputs.get('pointA')
            pointB = inputs.get('Point B') or inputs.get('PointB') or inputs.get('pointB')
            unitize = inputs.get('Unitize', False)
            if pointA is None or pointB is None:
                raise ValueError(f"Vector 2Pt component missing inputs: Point A={pointA}, Point B={pointB}")
            vector, length = func(pointA, pointB, unitize)
            return {'Vector': vector, 'Length': length}
        
        elif comp_type == 'Subtraction':
            # Subtraction expects 'a' and 'b', but inputs have 'A' and 'B'
            a = inputs.get('A') or inputs.get('a')
            b = inputs.get('B') or inputs.get('b')
            if a is None or b is None:
                raise ValueError(f"Subtraction component missing inputs: A={a}, B={b}")
            result = func(a, b)
            return {'Result': result}
        
        elif comp_type == 'Series':
            # Series expects 'start', 'count', 'step' (in that order), but inputs have 'Start', 'Step', 'Count'
            start = inputs.get('Start') if 'Start' in inputs else (inputs.get('start') if 'start' in inputs else None)
            step = inputs.get('Step') if 'Step' in inputs else (inputs.get('step') if 'step' in inputs else None)
            count = inputs.get('Count') if 'Count' in inputs else (inputs.get('count') if 'count' in inputs else None)
            # Check if inputs are truly missing (not just 0 or False)
            has_start = 'Start' in inputs or 'start' in inputs
            has_count = 'Count' in inputs or 'count' in inputs
            if not has_start or not has_count:
                raise ValueError(f"Series component missing inputs: Start={start} (has_start={has_start}), Count={count} (has_count={has_count})")
            # Use defaults if None
            if start is None:
                start = 0.0
            if step is None:
                step = 1.0
            if count is None:
                count = 0
            # Function signature: series_component(start: float, count: int, step: float)
            result = func(float(start), int(count), float(step))
            return {'Result': result}
        
        elif comp_type == 'Unit Y':
            # Unit Y expects 'factor', but inputs have 'Factor'
            factor = inputs.get('Factor') or inputs.get('factor')
            if factor is None:
                # Unit Y might work without factor (defaults to 1.0)
                factor = 1.0
            result = func(factor)
            return {'Vector': result}
        
        elif comp_type == 'Unit Z':
            # Unit Z expects 'factor', but inputs have 'Factor'
            factor = inputs.get('Factor') or inputs.get('factor')
            if factor is None:
                # Unit Z might work without factor (defaults to 1.0)
                factor = 1.0
            result = func(factor)
            return {'Vector': result}
        
        elif comp_type == 'Negative':
            # Negative expects 'value', but inputs have 'Value'
            value = inputs.get('Value') if 'Value' in inputs else (inputs.get('value') if 'value' in inputs else None)
            # Check if input is truly missing (not just 0 or False)
            has_value = 'Value' in inputs or 'value' in inputs
            if not has_value:
                # Try to get from persistent_values or external_inputs
                param_info = comp_info['obj'].get('params', {}).get('param_input_0', {})
                persistent_values = param_info.get('data', {}).get('persistent_values', [])
                if persistent_values:
                    try:
                        value = float(persistent_values[0]) if persistent_values[0] else 0.0
                    except (ValueError, TypeError):
                        value = 0.0
                else:
                    # Check external_inputs
                    external_inputs = get_external_inputs()
                    comp_instance_guid = comp_info.get('obj', {}).get('instance_guid', '') or comp_id
                    if comp_instance_guid in external_inputs:
                        ext_val = external_inputs[comp_instance_guid]
                        if isinstance(ext_val, dict):
                            value = ext_val.get('value', 0.0)
                        else:
                            value = ext_val
            if value is None:
                # Use 0.0 as default if None
                value = 0.0
            result = func(value)
            return {'Result': result}
        
        elif comp_type == 'Division':
            # Division expects 'a' and 'b', but inputs have 'A' and 'B'
            a = inputs.get('A') or inputs.get('a')
            b = inputs.get('B') or inputs.get('b')
            # Only return None if both are truly missing (not in inputs dict)
            if 'A' not in inputs and 'a' not in inputs and 'B' not in inputs and 'b' not in inputs:
                return {'Result': None}
            # Use 0.0 as default for missing inputs
            if a is None:
                a = 0.0
            if b is None:
                b = 0.0
            result = func(a, b)
            return {'Result': result}
        
        elif comp_type == 'Plane Normal':
            # Plane Normal expects a 'plane' dict, but inputs have 'Origin' and 'Z-Axis'
            # Need to construct a plane dict from Origin and Z-Axis
            origin = inputs.get('Origin') or inputs.get('origin')
            z_axis = inputs.get('Z-Axis') or inputs.get('ZAxis') or inputs.get('z_axis')
            # Only return default if inputs are truly missing (not in inputs dict)
            if 'Origin' not in inputs and 'origin' not in inputs and 'Z-Axis' not in inputs and 'ZAxis' not in inputs and 'z_axis' not in inputs:
                return {'Normal': [0.0, 0.0, 1.0]}
            # Construct plane dict from origin and z_axis, using defaults if needed
            plane = {
                'origin': origin if isinstance(origin, list) and len(origin) >= 3 else [0.0, 0.0, 0.0],
                'z_axis': z_axis if isinstance(z_axis, list) and len(z_axis) >= 3 else [0.0, 0.0, 1.0],
                'normal': z_axis if isinstance(z_axis, list) and len(z_axis) >= 3 else [0.0, 0.0, 1.0]
            }
            result = func(plane)
            return {'Normal': result}
        
        elif comp_type == 'Evaluate Surface':
            # Evaluate Surface expects 'surface', 'u', 'v', but inputs have 'Surface' and 'Point'
            surface = inputs.get('Surface') or inputs.get('surface')
            point = inputs.get('Point') or inputs.get('point')
            # Only return default if surface is truly missing (not in inputs dict)
            if 'Surface' not in inputs and 'surface' not in inputs:
                return {'Point': [0.0, 0.0, 0.0], 'Normal': [0.0, 0.0, 1.0], 'U': 0.0, 'V': 0.0}
            # Extract u, v from Point input (first two elements if list)
            if isinstance(point, list) and len(point) >= 2:
                u = float(point[0]) if point[0] is not None else 0.0
                v = float(point[1]) if point[1] is not None else 0.0
            else:
                u = 0.0
                v = 0.0
            result = func(surface, u, v)
            return result
        
        elif comp_type == 'Project':
            # Project expects 'geometry', 'target', 'direction', but inputs have 'Curve', 'Brep', 'Direction'
            geometry = inputs.get('Curve') or inputs.get('curve') or inputs.get('Geometry') or inputs.get('geometry')
            brep = inputs.get('Brep') or inputs.get('brep')
            direction = inputs.get('Direction') or inputs.get('direction')
            # Only return None if inputs are truly missing (not in inputs dict)
            has_geometry = 'Curve' in inputs or 'curve' in inputs or 'Geometry' in inputs or 'geometry' in inputs
            has_brep = 'Brep' in inputs or 'brep' in inputs
            if not has_geometry and not has_brep:
                return {'Curve': None}
            # Convert brep to target dict if needed
            if isinstance(brep, dict):
                target = brep
            elif brep is not None:
                target = {'brep': brep}
            else:
                target = {}
            result = func(geometry, target, direction)
            return {'Curve': result}
        
        elif comp_type == 'Construct Plane':
            # Construct Plane expects 'origin', 'x_axis', 'y_axis', but inputs have 'Origin', 'X-Axis', 'Y-Axis'
            origin = inputs.get('Origin') or inputs.get('origin')
            x_axis = inputs.get('X-Axis') or inputs.get('XAxis') or inputs.get('x_axis')
            y_axis = inputs.get('Y-Axis') or inputs.get('YAxis') or inputs.get('y_axis')
            # Only return default if inputs are truly missing (not in inputs dict)
            has_origin = 'Origin' in inputs or 'origin' in inputs
            has_x_axis = 'X-Axis' in inputs or 'XAxis' in inputs or 'x_axis' in inputs
            has_y_axis = 'Y-Axis' in inputs or 'YAxis' in inputs or 'y_axis' in inputs
            if not has_origin and not has_x_axis and not has_y_axis:
                return {'Plane': {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis': [0.0, 1.0, 0.0], 'z_axis': [0.0, 0.0, 1.0], 'normal': [0.0, 0.0, 1.0]}}
            # Use defaults for missing inputs
            if origin is None or not isinstance(origin, list) or len(origin) < 3:
                origin = [0.0, 0.0, 0.0]
            if x_axis is None or not isinstance(x_axis, list) or len(x_axis) < 3:
                x_axis = [1.0, 0.0, 0.0]
            if y_axis is None or not isinstance(y_axis, list) or len(y_axis) < 3:
                y_axis = [0.0, 1.0, 0.0]
            result = func(origin, x_axis, y_axis)
            return {'Plane': result}
        
        elif comp_type == 'MD Slider':
            # MD Slider expects 'value', but inputs may be empty (use PersistentData or default)
            value = inputs.get('Value') or inputs.get('value')
            if value is None:
                # Try to get from PersistentData
                param_info = comp_info.get('params', {}).get('inputs', {}).get('Value', {})
                persistent_data = param_info.get('PersistentData', [])
                if persistent_data:
                    value = persistent_data[0] if isinstance(persistent_data, list) else persistent_data
                else:
                    value = 0.0  # Default value
            result = func(value)
            return {'Value': result}
        
        elif comp_type == 'Point On Curve':
            # Point On Curve expects 'curve' and 'parameter', but inputs may be empty
            curve = inputs.get('Curve') or inputs.get('curve')
            parameter = inputs.get('Parameter') or inputs.get('parameter')
            if curve is None or parameter is None:
                # Return default point if inputs are missing (allows evaluation to continue)
                return {'Point': [0.0, 0.0, 0.0]}
            result = func(curve, parameter)
            return {'Point': result}
        
        elif comp_type == 'Deconstruct Brep':
            # Deconstruct Brep expects 'brep', but inputs have 'Brep'
            brep = inputs.get('Brep') or inputs.get('brep')
            if brep is None:
                # Return empty deconstruction if input is missing (allows evaluation to continue)
                return {'Faces': [], 'Edges': [], 'Vertices': []}
            result = func(brep)
            return result
        
        elif comp_type == 'Construct Point':
            # Construct Point expects 'x', 'y', 'z', but inputs have 'X coordinate', 'Y coordinate', 'Z coordinate'
            x = inputs.get('X coordinate') or inputs.get('X') or inputs.get('x')
            y = inputs.get('Y coordinate') or inputs.get('Y') or inputs.get('y')
            z = inputs.get('Z coordinate') or inputs.get('Z') or inputs.get('z')
            if x is None:
                x = 0.0
            if y is None:
                y = 0.0
            if z is None:
                z = 0.0
            result = func(x, y, z)
            return {'Point': result}
        
        elif comp_type == 'Polygon':
            # Polygon expects 'plane', 'radius', 'segments', 'fillet_radius', but inputs have 'Plane', 'Radius', 'Segments', 'Fillet Radius'
            plane = inputs.get('Plane') or inputs.get('plane')
            radius = inputs.get('Radius') or inputs.get('radius')
            segments = inputs.get('Segments') or inputs.get('segments')
            fillet_radius = inputs.get('Fillet Radius') or inputs.get('FilletRadius') or inputs.get('fillet_radius', 0.0)
            if plane is None:
                plane = {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis': [0.0, 1.0, 0.0], 'z_axis': [0.0, 0.0, 1.0]}
            if radius is None:
                radius = 1.0
            if segments is None:
                segments = 3
            result = func(plane, radius, int(segments), fillet_radius)
            return result if isinstance(result, dict) else {'Polygon': result}
        
        elif comp_type == 'Rotate':
            # Rotate expects 'geometry', 'angle', 'plane', but inputs have 'Geometry', 'Angle', 'Plane'
            geometry = inputs.get('Geometry') or inputs.get('geometry')
            angle = inputs.get('Angle') or inputs.get('angle')
            plane = inputs.get('Plane') or inputs.get('plane')
            if geometry is None:
                return {'Geometry': None}
            if angle is None:
                angle = 0.0
            if plane is None:
                plane = {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis': [0.0, 1.0, 0.0], 'z_axis': [0.0, 0.0, 1.0]}
            result = func(geometry, angle, plane)
            return {'Geometry': result}
        
        elif comp_type == 'Mirror':
            # Mirror expects 'geometry', 'plane', but inputs have 'Geometry', 'Plane'
            geometry = inputs.get('Geometry') or inputs.get('geometry')
            plane = inputs.get('Plane') or inputs.get('plane')
            if geometry is None:
                return {'Geometry': None}
            if plane is None:
                plane = {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 'y_axis': [0.0, 1.0, 0.0], 'z_axis': [0.0, 0.0, 1.0]}
            result = func(geometry, plane)
            return {'Geometry': result}
        
        elif comp_type == 'PolyLine':
            # PolyLine expects 'points', 'closed', but inputs have 'Vertices', 'Closed'
            points = inputs.get('Vertices') or inputs.get('Points') or inputs.get('points')
            closed = inputs.get('Closed') or inputs.get('closed', False)
            if points is None:
                return {'PolyLine': None}
            # Convert closed string to bool if needed
            if isinstance(closed, str):
                closed = closed.lower() == 'true'
            result = func(points, closed)
            return result if isinstance(result, dict) else {'PolyLine': result}
        
        elif comp_type == 'Divide Length':
            # Divide Length expects 'curve', 'length', but inputs have 'Curve', 'Length'
            curve = inputs.get('Curve') or inputs.get('curve')
            length = inputs.get('Length') or inputs.get('length')
            if curve is None:
                return {'Points': []}
            if length is None:
                length = 1.0
            result = func(curve, length)
            return {'Points': result} if isinstance(result, list) else {'Result': result}
        
        elif comp_type == 'Box 2Pt':
            # Box 2Pt expects 'corner1', 'corner2', but inputs have 'Point A', 'Point B'
            corner1 = inputs.get('Point A') or inputs.get('PointA') or inputs.get('corner1')
            corner2 = inputs.get('Point B') or inputs.get('PointB') or inputs.get('corner2')
            if corner1 is None or corner2 is None:
                raise ValueError(f"Box 2Pt component missing inputs: Point A={corner1}, Point B={corner2}")
            result = func(corner1, corner2)
            return result if isinstance(result, dict) else {'Box': result}
        
        else:
            # Generic component - try to call with inputs as kwargs
            result = func(**inputs)
            return result if isinstance(result, dict) else {'Result': result}
    
    except Exception as e:
        # Enhanced error logging
        comp_instance_guid = comp_info.get('obj', {}).get('instance_guid', '') or comp_id
        comp_nickname = comp_info.get('obj', {}).get('nickname', '')
        print(f"\n{'='*80}")
        print(f"ERROR evaluating component:")
        print(f"  Type: {comp_type}")
        print(f"  GUID: {comp_instance_guid}")
        print(f"  NickName: {comp_nickname}")
        print(f"  Component ID: {comp_id[:8]}...")
        print(f"  Raw inputs (repr):")
        for key, val in inputs.items():
            val_type = type(val).__name__
            if is_tree(val):
                paths = val.paths()
                print(f"    {key}: DataTree with {len(paths)} branches")
            elif isinstance(val, list):
                print(f"    {key}: list with {len(val)} items (first item type: {type(val[0]).__name__ if val else 'empty'})")
            else:
                val_repr = repr(val)[:100]  # Limit length
                print(f"    {key}: {val_type} = {val_repr}")
        print(f"  Exception: {type(e).__name__}: {e}")
        print(f"{'='*80}\n")
        raise ValueError(f"Error evaluating {comp_type} component (GUID: {comp_id[:8]}...): {e}")


def topological_sort(graph: Dict, all_objects: Dict, output_params: Dict) -> List[str]:
    """
    Perform topological sort on the component graph.
    Returns a list of component IDs in evaluation order.
    """
    # Handle graph structure: may have 'components' key or be flat
    components_dict = graph.get('components', graph) if isinstance(graph, dict) and 'components' in graph else graph
    
    # Build dependency graph
    dependencies = {}  # comp_id -> set of comp_ids it depends on
    all_comp_ids = set()
    
    # Collect all component IDs
    for comp_id, comp_info in components_dict.items():
        if isinstance(comp_info, dict) and comp_info.get('type') == 'component':
            all_comp_ids.add(comp_id)
    
    # Build dependency map
    for comp_id, comp_info in components_dict.items():
        if isinstance(comp_info, dict) and comp_info.get('type') == 'component':
            deps = set()
            # Check inputs for dependencies
            inputs = comp_info.get('inputs', {})
            if not inputs and 'obj' in comp_info:
                # Build inputs from obj.params
                obj_params = comp_info['obj'].get('params', {})
                inputs = {}
                for param_key, param_data in obj_params.items():
                    if param_key.startswith('param_input'):
                        param_name = param_data.get('data', {}).get('NickName', '') or param_data.get('data', {}).get('Name', '')
                        if param_name:
                            inputs[param_key] = {
                                'name': param_name,
                                'sources': param_data.get('sources', [])
                            }
            
            for input_key, input_info in inputs.items():
                sources = input_info.get('sources', [])
                for source in sources:
                    source_guid = source.get('source_guid') or source.get('guid')
                    if source_guid:
                        # Find the component that has this output
                        for other_comp_id, other_comp_info in components_dict.items():
                            if isinstance(other_comp_info, dict) and other_comp_info.get('type') == 'component':
                                other_obj = other_comp_info.get('obj', {})
                                other_params = other_obj.get('params', {})
                                for param_key, param_data in other_params.items():
                                    if param_key.startswith('param_output'):
                                        param_guid = param_data.get('data', {}).get('InstanceGuid')
                                        if param_guid == source_guid:
                                            deps.add(other_comp_id)
                        break
            
            dependencies[comp_id] = deps
    
    # Topological sort using Kahn's algorithm
    # Initialize in_degree for all components
    in_degree = {comp_id: 0 for comp_id in all_comp_ids}
    
    # Count dependencies: for each component, count how many components depend on it
    for comp_id, deps in dependencies.items():
        for dep in deps:
            if dep in in_degree:
                in_degree[dep] += 1
    
    # Start with components that have no dependencies (in_degree == 0)
    queue = [comp_id for comp_id in all_comp_ids if in_degree[comp_id] == 0]
    result = []
    
    while queue:
        comp_id = queue.pop(0)
        result.append(comp_id)
        
        # Reduce in-degree of components that depend on this one
        # Find all components that have comp_id as a dependency
        for other_comp_id, deps in dependencies.items():
            if comp_id in deps:
                if other_comp_id in in_degree:
                    in_degree[other_comp_id] -= 1
                    if in_degree[other_comp_id] == 0:
                        queue.append(other_comp_id)
    
    # Add any remaining components that weren't reached (shouldn't happen in a DAG, but handle gracefully)
    remaining = [comp_id for comp_id in all_comp_ids if comp_id not in result]
    if remaining:
        # These are components that weren't reachable from the initial queue
        # They might be isolated or have circular dependencies
        # For now, add them at the end (they'll be evaluated but might have issues)
        result.extend(remaining)
    
    return result


def evaluate_graph(graph: Dict, all_objects: Dict, output_params: Dict,
                   output_guids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Evaluate the entire component graph.
    Returns a dictionary mapping component GUIDs to their outputs.
    """
    evaluated = {}
    
    # Handle graph structure: may have 'components' key or be flat
    components_dict = graph.get('components', graph) if isinstance(graph, dict) and 'components' in graph else graph
    
    # Get topological sort
    sorted_components = topological_sort(graph, all_objects, output_params)
    
    # Debug: Check if Rectangle 2Pt is in sort
    rect_guid = 'a3eb185f-a7cb-4727-aeaf-d5899f934b99'
    debug_info = []
    debug_info.append(f"Total components in sort: {len(sorted_components)}")
    debug_info.append(f"Rectangle 2Pt in sort: {rect_guid in sorted_components}")
    if rect_guid in sorted_components:
        debug_info.append(f"Position: {sorted_components.index(rect_guid)}")
    debug_info.append(f"Rectangle 2Pt in components_dict: {rect_guid in components_dict}")
    if rect_guid in components_dict:
        comp_info = components_dict[rect_guid]
        debug_info.append(f"Component type: {comp_info.get('type', 'Unknown')}")
    debug_info.append(f"\nFirst 10 components in sort:")
    for i, comp_id in enumerate(sorted_components[:10]):
        debug_info.append(f"  {i}: {comp_id[:8]}...")
    debug_info.append(f"\nComponents with 'Rectangle' in name:")
    for comp_id in sorted_components:
        if comp_id in components_dict:
            comp_type = components_dict[comp_id].get('obj', {}).get('type', '')
            if 'Rectangle' in comp_type:
                debug_info.append(f"  {comp_id[:8]}...: {comp_type}")
    
    with open('debug_topological_sort.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(debug_info))
    
    if rect_guid in sorted_components:
        print(f"[DEBUG] Rectangle 2Pt is in topological sort at position {sorted_components.index(rect_guid)}")
    else:
        print(f"[DEBUG] Rectangle 2Pt is NOT in topological sort - see debug_topological_sort.txt")
    
    # Track None values for tracing
    none_trace = []
    
    # Evaluate components in order
    for comp_id in sorted_components:
        comp_info = components_dict.get(comp_id)
        if not comp_info or comp_info.get('type') != 'component':
            continue
        
        try:
            result = evaluate_component(comp_id, comp_info, evaluated, all_objects, output_params, graph=graph)
            instance_guid = comp_info.get('obj', {}).get('instance_guid') or comp_id
            evaluated[instance_guid] = result
            
            # Track None values
            if result is None:
                none_trace.append({
                    'comp_id': instance_guid,
                    'comp_type': comp_info.get('obj', {}).get('type', 'Unknown'),
                    'comp_nickname': comp_info.get('obj', {}).get('nickname', ''),
                    'output': None
                })
            elif isinstance(result, dict):
                for key, value in result.items():
                    if value is None:
                        none_trace.append({
                            'comp_id': instance_guid,
                            'comp_type': comp_info.get('obj', {}).get('type', 'Unknown'),
                            'comp_nickname': comp_info.get('obj', {}).get('nickname', ''),
                            'output_key': key,
                            'output': result
                        })
        except Exception as e:
            # Log error but continue - allow evaluation to complete even if some components fail
            # Only log errors for Rotatingslats chain components to reduce noise
            comp_type = comp_info.get('obj', {}).get('type', 'Unknown')
            instance_guid = comp_info.get('obj', {}).get('instance_guid', '')
            rotatingslats_guids = [
                'a3eb185f-a7cb-4727-aeaf-d5899f934b99',  # Rectangle2Pt
                'ddb9e6ae-7d3e-41ae-8c75-fc726c984724',  # First Move
                '7ad636cc-e506-4f77-bb82-4a86ba2a3fea',  # Polar Array
                '27933633-dbab-4dc0-a4a2-cfa309c03c45',  # List Item
                '0532cbdf-875b-4db9-8c88-352e21051436',  # Second Move
                '3bd2c1d3-149d-49fb-952c-8db272035f9e',  # Area
            ]
            if instance_guid in rotatingslats_guids:
                comp_nickname = comp_info.get('obj', {}).get('nickname', '')
                print(f"ERROR [ROTATINGSLATS] Failed {comp_type} ({comp_nickname}) {comp_id[:8]}...: {e}")
            # Store None to indicate failure (downstream components will handle None inputs)
            evaluated[instance_guid] = None
            none_trace.append({
                'comp_id': instance_guid,
                'comp_type': comp_type,
                'comp_nickname': comp_info.get('obj', {}).get('nickname', ''),
                'output': None,
                'error': str(e)
            })
            # Continue evaluation instead of raising
    
    # Write None trace to file
    if none_trace:
        with open('none_trace.json', 'w', encoding='utf-8') as f:
            json.dump(none_trace, f, indent=2)
        
        # Also write human-readable trace
        with open('none_trace.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("NONE VALUES TRACE\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Found {len(none_trace)} components with None outputs\n\n")
            
            for i, trace in enumerate(none_trace, 1):
                f.write("=" * 80 + "\n")
                f.write(f"{i}. Component: {trace['comp_id'][:8]}...\n")
                f.write(f"   Type: {trace['comp_type']}\n")
                f.write(f"   Nickname: {trace['comp_nickname']}\n")
                f.write(f"   None output: {trace.get('output_key', 'Result')}\n")
                if 'error' in trace:
                    f.write(f"   Error: {trace['error']}\n")
                f.write("\n")
                
                # Find component and trace inputs
                comp_id = trace['comp_id']
                comp_info = None
                for comp_key, comp_data in graph.items():
                    if isinstance(comp_data, dict):
                        instance_guid = comp_data.get('obj', {}).get('instance_guid')
                        if instance_guid == comp_id:
                            comp_info = comp_data
                            break
                
                if not comp_info:
                    for obj_key, obj in all_objects.items():
                        if obj.get('instance_guid') == comp_id:
                            comp_info = {'obj': obj}
                            break
                
                if comp_info:
                    f.write("   Inputs:\n")
                    obj_params = comp_info.get('obj', {}).get('params', {})
                    for param_key, param_info in obj_params.items():
                        if param_key.startswith('param_input'):
                            param_name = param_info.get('data', {}).get('NickName', '') or param_info.get('data', {}).get('Name', '')
                            sources = param_info.get('sources', [])
                            
                            f.write(f"     {param_name}:\n")
                            
                            if sources:
                                for source in sources:
                                    source_guid = source.get('guid') or source.get('source_guid')
                                    if source_guid:
                                        f.write(f"       Source GUID: {source_guid[:8]}...\n")
                                        
                                        if source_guid in output_params:
                                            source_info = output_params[source_guid]
                                            source_obj = source_info['obj']
                                            source_comp_guid = source_obj.get('instance_guid')
                                            f.write(f"         From: {source_comp_guid[:8]}... ({source_obj.get('type', 'Unknown')}, {source_obj.get('nickname', '')})\n")
                                            
                                            if source_comp_guid in evaluated:
                                                source_result = evaluated[source_comp_guid]
                                                f.write(f"         [EVALUATED] Result: {source_result}\n")
                                            else:
                                                f.write(f"         [NOT EVALUATED] Component not in evaluated dict\n")
                                        else:
                                            f.write(f"         [NOT OUTPUT PARAM]\n")
                            else:
                                persistent_values = param_info.get('persistent_values', [])
                                if persistent_values:
                                    f.write(f"       Persistent values: {persistent_values}\n")
                                else:
                                    f.write(f"       [NO SOURCE]\n")
                            f.write("\n")
                f.write("\n")
        
        print(f"\n[TRACE] Found {len(none_trace)} None values - saved to none_trace.json and none_trace.txt")
    
    return evaluated


if __name__ == '__main__':
    import json
    import sys
    
    # Load graph
    graph_data = load_component_graph('complete_component_graph.json')
    # Graph structure: { "components": { comp_id: comp_info, ... } }
    # We need to pass the full graph_data to topological_sort, but use graph.get('components', graph) for evaluation
    graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data
    # For topological_sort, pass the full graph_data (it will look for 'components' key)
    graph_for_sort = graph_data if isinstance(graph_data, dict) and 'components' in graph_data else graph
    
    # Load all objects
    with open('rotatingslats_data.json', 'r') as f:
        data = json.load(f)
        all_objects = {}
        all_objects.update(data.get('group_objects', {}))
        all_objects.update(data.get('external_objects', {}))
    
    # Build output params
    output_params = {}
    for key, obj in all_objects.items():
        for param_key, param_info in obj.get('params', {}).items():
            if param_key.startswith('param_output'):
                param_guid = param_info.get('data', {}).get('InstanceGuid')
                if param_guid:
                    output_params[param_guid] = {
                        'obj': obj,
                        'param_key': param_key,
                        'param_info': param_info
                    }
    
    # Evaluate graph
    try:
        evaluated = evaluate_graph(graph_for_sort, all_objects, output_params)
        
        # Write results
        with open('evaluation_results.md', 'w') as f:
            f.write("# Evaluation Results\n\n")
            for comp_id, result in evaluated.items():
                # Find component info to get nickname and type
                comp_info = None
                comp_nickname = ""
                comp_type = ""
                
                # Try to find in graph
                for comp_key, comp_data in graph.items():
                    if isinstance(comp_data, dict):
                        instance_guid = comp_data.get('obj', {}).get('instance_guid')
                        if instance_guid == comp_id:
                            comp_info = comp_data
                            break
                
                # If not found in graph, try all_objects
                if not comp_info:
                    for obj_key, obj in all_objects.items():
                        if obj.get('instance_guid') == comp_id:
                            comp_info = {'obj': obj}
                            break
                
                if comp_info:
                    comp_nickname = comp_info.get('obj', {}).get('nickname', '')
                    comp_type = comp_info.get('obj', {}).get('type', '')
                
                # Write component header with nickname and type
                f.write(f"## Component {comp_id[:8]}...\n")
                if comp_nickname:
                    f.write(f"**Nickname:** {comp_nickname}\n")
                if comp_type:
                    f.write(f"**Type:** {comp_type}\n")
                f.write("\n")
                
                # Write results
                if isinstance(result, dict):
                    for key, value in result.items():
                        f.write(f"- {key}: {value}\n")
                else:
                    f.write(f"- Result: {result}\n")
                f.write("\n")
        
        print("Evaluation complete. Results written to evaluation_results.md")
    
    except Exception as e:
        print(f"\nEvaluation error: {e}")
        import traceback
        traceback.print_exc()
