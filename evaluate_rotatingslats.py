"""
Graph-based evaluator for Rotatingslats computation chain.
Uses topological sort to evaluate components in dependency order.
"""
import json
import math
from collections import defaultdict, OrderedDict
from typing import Dict, List, Any, Optional, Union
import gh_components


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
                       graph: Optional[Dict] = None) -> Any:
    """
    Resolve the input value for a component parameter.
    Handles constants, external inputs, and connections from other components.
    """
    if param_info is None:
        param_info = comp_info['obj'].get('params', {}).get(param_key, {})
    param_guid = param_info.get('data', {}).get('InstanceGuid')
    
    # Check for sources FIRST - if there's a source connection, it overrides persistent values
    sources = param_info.get('sources', [])
    
    # Check external_inputs by parameter GUID first (before persistent_values/values)
    # This allows overriding default/placeholder values with real values
    # BUT: For Plane parameters, we'll check PersistentData first since it has the correct plane structure
    external_inputs = get_external_inputs()
    param_name = param_info.get('data', {}).get('NickName', '') or param_info.get('data', {}).get('Name', '')
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
            
            # Try to extract plane from PersistentData directly
            # Check if param_info has PersistentData with gh_plane type
            # This requires parsing the GHX XML, so we'll need to check the parsed data structure
            # For now, check if we can get it from the component's params structure
            # The PersistentData might be stored in the param_info structure
            # If not available, we'll use default plane in the component evaluation
    
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
    
    # Check for sources (connections) - already checked above, but now process them
    if sources:
        # Handle multiple sources - resolve all and combine if needed
        resolved_values = []
        for source in sources:
            # Try both 'guid' and 'source_guid' keys
            # The inputs structure uses 'source_guid', obj.params uses 'guid'
            source_guid = source.get('source_guid') or source.get('guid')
            if not source_guid:
                # Debug for Move component
                if comp_id == 'dfbbd4a2-021a-4c74-ac63-8939e6ac5429' and param_key == 'param_input_1':
                    print(f"DEBUG: Source has no guid or source_guid: {source}")
                continue
            
            # Resolve this source using the same logic as before
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
                    if source_obj_guid in evaluated:
                        comp_outputs = evaluated.get(source_obj_guid, {})
                        if isinstance(comp_outputs, dict):
                            source_param_name = source_info['param_info'].get('data', {}).get('NickName', '')
                            # Check if source component is MD Slider - if so, get the full point value
                            source_obj = source_info.get('obj', {})
                            source_comp_type = source_obj.get('type', '')
                            if source_comp_type == 'MD Slider' and 'Point' in comp_outputs:
                                # MD Slider with point3d - return the full point
                                source_value = comp_outputs['Point']
                            # For Polar Array and similar components, prioritize 'Geometry' key
                            # This ensures correct extraction when output param name is 'Geometry'
                            elif source_param_name == 'Geometry' and 'Geometry' in comp_outputs:
                                source_value = comp_outputs['Geometry']
                            else:
                                for key in [source_param_name, 'Geometry', 'Result', 'Value', 'Output', 'Vector', 'Point']:
                                    if key in comp_outputs:
                                        source_value = comp_outputs[key]
                                        break
                                if source_value is None and comp_outputs:
                                    source_value = list(comp_outputs.values())[0]
                        else:
                            source_value = comp_outputs
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
                                        # Debug for Amplitude component
                                        if comp_guid == 'f54babb4-b955-42d1-aeb1-3b2192468fed':
                                            print(f"DEBUG: Failed to evaluate Amplitude: {eval_err}")
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
            else:
                # Debug: check why source wasn't resolved
                if comp_id == 'be907c11-5a37-4cf5-9736-0f3c61ba7014' and param_key in ['param_input_0', 'param_input_1']:
                    print(f"DEBUG resolve_input_value: source_guid {source_guid[:8]}... not resolved")
                    print(f"  source_guid in evaluated: {source_guid in evaluated}")
                    print(f"  source_guid in output_params: {source_guid in output_params}")
                    print(f"  source_guid in external_inputs: {source_guid in get_external_inputs()}")
                    # Check if it's a component
                    for key, obj in all_objects.items():
                        if obj.get('instance_guid') == source_guid:
                            print(f"  Found as component: {obj.get('type')} '{obj.get('nickname')}'")
                            break
                # Debug for Move component Motion input
                elif comp_id == 'dfbbd4a2-021a-4c74-ac63-8939e6ac5429' and param_key == 'param_input_1':
                    print(f"DEBUG: Failed to resolve source {source_guid[:8]}... for Move Motion input")
                    print(f"  Source in output_params: {source_guid in output_params}")
                    print(f"  Source in evaluated: {source_guid in evaluated}")
                    # Check if it's an output parameter GUID
                    found_in_output_params = False
                    for out_param_guid, out_info in output_params.items():
                        if out_param_guid == source_guid:
                            found_in_output_params = True
                            parent_guid = out_info['obj'].get('instance_guid')
                            print(f"  Found as output param, parent: {parent_guid[:8] if parent_guid else 'N/A'}...")
                            print(f"  Parent in evaluated: {parent_guid in evaluated if parent_guid else False}")
                            break
                    if not found_in_output_params:
                        print(f"  Not found in output_params. Checking if it's a component...")
                        for obj_key, obj in all_objects.items():
                            if obj.get('instance_guid') == source_guid:
                                print(f"  Found as component: {obj.get('type')} '{obj.get('nickname')}'")
                                print(f"  Component in evaluated: {source_guid in evaluated}")
                                break
                # Debug for "Targets" Move component Motion input
                elif comp_id == 'b38a38f1-ced5-4600-a687-4ebc4d73e6ff' and param_key == 'param_input_1':
                    print(f"DEBUG Targets Move Motion: Failed to resolve source {source_guid[:8]}...")
                    print(f"  Source in output_params: {source_guid in output_params}")
                    print(f"  Source in evaluated: {source_guid in evaluated}")
                    if source_guid in output_params:
                        out_info = output_params[source_guid]
                        parent_guid = out_info['obj'].get('instance_guid')
                        print(f"  Found as output param, parent: {parent_guid[:8] if parent_guid else 'N/A'}...")
                        print(f"  Parent in evaluated: {parent_guid in evaluated if parent_guid else False}")
                        if parent_guid in evaluated:
                            parent_output = evaluated[parent_guid]
                            print(f"  Parent output type: {type(parent_output).__name__}")
                            if isinstance(parent_output, dict):
                                print(f"  Parent output keys: {list(parent_output.keys())}")
        
        # Return appropriate value based on number of sources
        if len(resolved_values) == 0:
            # Debug for Move component
            if comp_id == 'dfbbd4a2-021a-4c74-ac63-8939e6ac5429' and param_key == 'param_input_1':
                print(f"DEBUG: No resolved values for Move Motion input (had {len(sources)} sources)")
            return None
        elif len(resolved_values) == 1:
            # Single source - check if it's Amplitude component
            # For "Targets" Move component, if source is Amplitude, ignore PersistentData
            # (screenshot shows Motion = Amplitude value without PersistentData)
            is_amplitude_source = False
            if sources and len(sources) == 1:
                source_obj_guid = sources[0].get('source_obj_guid')
                if source_obj_guid:
                    comp = graph.get(source_obj_guid) if graph else None
                    if not comp:
                        for obj_key, obj in all_objects.items():
                            if obj.get('instance_guid') == source_obj_guid:
                                comp = {'obj': obj, 'inputs': {}, 'outputs': {}}
                                if graph:
                                    for cid, cdata in graph.items():
                                        if isinstance(cdata, dict) and cdata.get('obj', {}).get('instance_guid') == source_obj_guid:
                                            comp = cdata
                                            break
                                break
                    if comp and comp.get('obj', {}).get('type') == 'Amplitude':
                        is_amplitude_source = True
            
            # Only add PersistentData if source is NOT Amplitude
            persistent_vector = None
            if not is_amplitude_source and persistent_values:
                for pv in persistent_values:
                    if isinstance(pv, str):
                        pv_stripped = pv.strip()
                        if pv_stripped.startswith('[') and pv_stripped.endswith(']'):
                            try:
                                persistent_vector = json.loads(pv_stripped)
                                if isinstance(persistent_vector, list) and len(persistent_vector) == 3:
                                    break
                            except (json.JSONDecodeError, ValueError):
                                pass
            
            result = resolved_values[0]
            # Add persistent vector if present and result is a vector (and not Amplitude source)
            if persistent_vector and isinstance(result, list) and len(result) == 3 and all(isinstance(x, (int, float)) for x in result):
                result = [result[i] + persistent_vector[i] for i in range(3)]
            return result
        else:
            # Multiple sources - for Move component Motion input
            # Since Vector XYZ has been removed from the GHX file, we should only have Amplitude now
            # The screenshot shows Motion = {11.32743, -27.346834, 0} which is exactly Amplitude's output
            # Check if we have an Amplitude source - if so, try to evaluate it and use it
            amplitude_source_guid = None
            amplitude_value = None
            
            # Find Amplitude source
            for source in sources:
                source_obj_guid = source.get('source_obj_guid')
                if source_obj_guid:
                    # Check if this is Amplitude component
                    comp = graph.get(source_obj_guid) if graph else None
                    if not comp:
                        for obj_key, obj in all_objects.items():
                            if obj.get('instance_guid') == source_obj_guid:
                                comp = {'obj': obj, 'inputs': {}, 'outputs': {}}
                                # Try to get full comp from graph
                                if graph:
                                    for cid, cdata in graph.items():
                                        if isinstance(cdata, dict) and cdata.get('obj', {}).get('instance_guid') == source_obj_guid:
                                            comp = cdata
                                            break
                                break
                    if comp and comp.get('obj', {}).get('type') == 'Amplitude':
                        amplitude_source_guid = source.get('source_guid')
                        # Try to evaluate Amplitude if not already evaluated
                        if source_obj_guid not in evaluated:
                            # Use recursive evaluation to get Amplitude
                            try:
                                # This will be handled by the recursive evaluation in resolve_input_value
                                # But we can try to evaluate it here too
                                result = evaluate_component(source_obj_guid, comp, evaluated, all_objects, output_params, graph=graph)
                                evaluated[source_obj_guid] = result
                            except Exception:
                                pass
                        # Check if Amplitude was evaluated
                        if source_obj_guid in evaluated:
                            amp_result = evaluated[source_obj_guid]
                            if isinstance(amp_result, dict):
                                amplitude_value = amp_result.get('Vector')
                            elif isinstance(amp_result, list) and len(amp_result) == 3:
                                amplitude_value = amp_result
                        break
            
            # If Amplitude is available, use it directly (Vector XYZ has been removed)
            # Screenshot shows Amplitude value without PersistentData (Z is 0, not 10)
            if amplitude_value is not None:
                return amplitude_value
            
            # Otherwise, combine all vectors (original behavior)
            # Also check if there's PersistentData to add
            persistent_vector = None
            if persistent_values:
                for pv in persistent_values:
                    if isinstance(pv, str):
                        pv_stripped = pv.strip()
                        if pv_stripped.startswith('[') and pv_stripped.endswith(']'):
                            try:
                                persistent_vector = json.loads(pv_stripped)
                                if isinstance(persistent_vector, list) and len(persistent_vector) == 3:
                                    break
                            except (json.JSONDecodeError, ValueError):
                                pass
            
            # Check if all values are single vectors (list of 3 numbers)
            all_are_single_vectors = all(isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) for x in v) for v in resolved_values)
            # Check if all values are lists of vectors (list of lists)
            all_are_lists_of_vectors = all(isinstance(v, list) and len(v) > 0 and isinstance(v[0], list) for v in resolved_values)
            
            if all_are_single_vectors:
                # Combine vectors by adding them
                combined = [sum(components) for components in zip(*resolved_values)]
                # Add persistent vector if present
                if persistent_vector:
                    combined = [combined[i] + persistent_vector[i] for i in range(3)]
                return combined
            elif all_are_lists_of_vectors:
                # Both are lists of vectors - combine pairwise
                min_len = min(len(v) for v in resolved_values)
                combined = []
                for i in range(min_len):
                    vec_sum = [0.0, 0.0, 0.0]
                    for v in resolved_values:
                        if i < len(v) and isinstance(v[i], list) and len(v[i]) >= 3:
                            vec_sum[0] += v[i][0] if isinstance(v[i][0], (int, float)) else 0.0
                            vec_sum[1] += v[i][1] if isinstance(v[i][1], (int, float)) else 0.0
                            vec_sum[2] += v[i][2] if isinstance(v[i][2], (int, float)) else 0.0
                    combined.append(vec_sum)
                return combined
            else:
                # Mixed: one is a list of vectors, one is a single vector
                # Find which is which and broadcast
                list_of_vectors = None
                single_vector = None
                for v in resolved_values:
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], list):
                        list_of_vectors = v
                    elif isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) for x in v):
                        single_vector = v
                
                if list_of_vectors and single_vector:
                    # Broadcast single vector to match list length
                    combined = [[v[0] + single_vector[0], v[1] + single_vector[1], v[2] + single_vector[2]] 
                               for v in list_of_vectors]
                    return combined
                else:
                    # Return as list for components that accept multiple inputs
                    return resolved_values
    
    # Check external inputs by component GUID
    external_inputs = get_external_inputs()
    if comp_id in external_inputs:
        return external_inputs[comp_id]
    
    # Default: return None (will cause error if required)
    return None


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
        if comp_type == 'Angle':
            vectorA = inputs.get('Vector A')
            vectorB = inputs.get('Vector B')
            plane = inputs.get('Plane')
            if vectorA is None or vectorB is None:
                raise ValueError(f"Angle component missing inputs: Vector A={vectorA}, Vector B={vectorB}")
            # Convert vectors to lists if they're dicts or other types
            if isinstance(vectorA, dict):
                vectorA = vectorA.get('Vector', vectorA.get('Normal', [0.0, 0.0, 0.0]))
            if isinstance(vectorB, dict):
                vectorB = vectorB.get('Vector', vectorB.get('Normal', [0.0, 0.0, 0.0]))
            if not isinstance(vectorA, list):
                vectorA = [0.0, 0.0, 0.0]
            if not isinstance(vectorB, list):
                vectorB = [0.0, 0.0, 0.0]
            angle, reflex = func(vectorA, vectorB, plane)
            return {'Angle': angle, 'Reflex': reflex}
        
        elif comp_type == 'Degrees':
            radians = inputs.get('Radians')
            if radians is None:
                raise ValueError(f"Degrees component missing Radians input")
            degrees = func(radians)
            return {'Degrees': degrees}
        
        elif comp_type == 'Line':
            start = inputs.get('Start Point') or inputs.get('Start') or inputs.get('Point A')
            end = inputs.get('End Point') or inputs.get('End') or inputs.get('Point B')
            if start is None or end is None:
                raise ValueError(f"Line component missing inputs: Start={start}, End={end}")
            line = func(start, end)
            
            # Handle both single line and list of lines
            if isinstance(line, list):
                # List of lines
                return {
                    'Line': line,
                    'Start': [l.get('start') for l in line],
                    'End': [l.get('end') for l in line],
                    'Direction': [l.get('direction', [0, 0, 0]) for l in line],
                    'Length': [l.get('length', 0.0) for l in line]
                }
            else:
                # Single line
                return {
                    'Line': line,
                    'Start': line.get('start') if isinstance(line, dict) else start,
                    'End': line.get('end') if isinstance(line, dict) else end,
                    'Direction': line.get('direction', [0, 0, 0]) if isinstance(line, dict) else [0, 0, 0],
                    'Length': line.get('length', 0.0) if isinstance(line, dict) else 0.0
                }
        
        elif comp_type == 'Plane':
            # Default plane
            plane = func()
            return {'Plane': plane}
        
        elif comp_type == 'Construct Plane':
            origin = inputs.get('Origin', [0, 0, 0])
            x_axis = inputs.get('X Axis', [1, 0, 0])
            y_axis = inputs.get('Y Axis', [0, 1, 0])
            plane = func(origin, x_axis, y_axis)
            return {'Plane': plane}
        
        elif comp_type == 'Plane Normal':
            # Plane Normal has Origin and Z-Axis inputs, not Plane
            origin = inputs.get('Origin')
            z_axis = inputs.get('Z-Axis') or inputs.get('Normal')
            # If we have both, construct a plane dict
            if origin is not None and z_axis is not None:
                plane = {'origin': origin, 'normal': z_axis, 'z_axis': z_axis}
            else:
                # Try to get Plane input (some components might use this)
                plane = inputs.get('Plane')
                if plane is None:
                    # If we have at least origin, use default normal
                    if origin is not None:
                        plane = {'origin': origin, 'normal': [0.0, 0.0, 1.0], 'z_axis': [0.0, 0.0, 1.0]}
                    else:
                        raise ValueError(f"Plane Normal component missing inputs: Origin={origin}, Z-Axis={z_axis}")
            normal = func(plane)
            return {'Normal': normal, 'Plane': plane}
        
        elif comp_type == 'Vector 2Pt':
            pointA = inputs.get('Point A') or inputs.get('Start Point')
            pointB = inputs.get('Point B') or inputs.get('End Point')
            unitize = inputs.get('Unitize', False)
            
            if pointA is None or pointB is None:
                raise ValueError(f"Vector 2Pt component missing inputs: Point A={pointA}, Point B={pointB}")
            
            # Ensure unitize is a boolean
            if not isinstance(unitize, bool):
                if isinstance(unitize, str):
                    unitize = unitize.lower() in ['true', '1', 'yes']
                else:
                    unitize = bool(unitize)
            
            # Handle list inputs - Vector 2Pt can process lists
            # If pointA or pointB is a list of vectors, pass it directly to the function
            # The function will handle the list matching logic
            vector, length = func(pointA, pointB, unitize)
            
            # Debug output for Vector 2Pt component
            if comp_id == 'ea032caa-ddff-403c-ab58-8ab6e24931ac':
                print(f"  Vector 2Pt {comp_id[:8]}...:")
                print(f"    Point A type: {type(pointA)}, value: {pointA[:3] if isinstance(pointA, list) and len(pointA) > 3 and not isinstance(pointA[0], list) else (pointA[0] if isinstance(pointA, list) and len(pointA) > 0 else pointA)}")
                print(f"    Point B type: {type(pointB)}, value: {pointB[:3] if isinstance(pointB, list) and len(pointB) > 3 and not isinstance(pointB[0], list) else (pointB[0] if isinstance(pointB, list) and len(pointB) > 0 else pointB)}")
                print(f"    Unitize: {unitize}")
                if isinstance(vector, list) and len(vector) > 0:
                    if isinstance(vector[0], list):
                        print(f"    Vector output: {len(vector)} vectors, first: {vector[0]}, last: {vector[-1]}")
                    else:
                        print(f"    Vector output: {vector}")
                else:
                    print(f"    Vector output: {vector}")
            
            return {'Vector': vector, 'Length': length}
        
        elif comp_type == 'Unitize':
            vector = inputs.get('Vector')
            if vector is None:
                raise ValueError(f"Unitize component missing Vector input")
            unit = func(vector)
            return {'Vector': unit}
        
        elif comp_type == 'Vector XYZ':
            x = inputs.get('X component') or inputs.get('X') or 0.0
            y = inputs.get('Y component') or inputs.get('Y') or 0.0
            z = inputs.get('Z component') or inputs.get('Z') or 0.0
            # Convert to float if they're strings (from persistent_values)
            try:
                x = float(x) if not isinstance(x, (int, float)) else x
                y = float(y) if not isinstance(y, (int, float)) else y
                z = float(z) if not isinstance(z, (int, float)) else z
            except (ValueError, TypeError):
                x = y = z = 0.0
            vector = func(x, y, z)
            return {'Vector': vector}
        
        elif comp_type == 'Amplitude':
            vector = inputs.get('Vector')
            amplitude = inputs.get('Amplitude')
            if vector is None or amplitude is None:
                raise ValueError(f"Amplitude component missing inputs: Vector={vector is not None}, Amplitude={amplitude is not None}")
            # Convert amplitude to float if it's a string
            try:
                amplitude = float(amplitude) if not isinstance(amplitude, (int, float)) else amplitude
            except (ValueError, TypeError):
                amplitude = 1.0
            result = func(vector, amplitude)
            return {'Vector': result}
        
        elif comp_type == 'Unit Y':
            factor = inputs.get('Factor', 1.0)
            # Handle both single values and lists (like Negative component)
            if isinstance(factor, list):
                # Factor is a list - process each value to get list of vectors
                unit_y = func(factor)
            else:
                # Single value - ensure it's a float
                if not isinstance(factor, (int, float)):
                    try:
                        factor = float(factor)
                    except (ValueError, TypeError):
                        factor = 1.0
                unit_y = func(factor)
            return {'Vector': unit_y, 'Unit vector': unit_y}
        
        elif comp_type == 'Unit Z':
            factor = inputs.get('Factor', 1.0)
            # Handle both single values and lists (like Negative component)
            if isinstance(factor, list):
                # Factor is a list - process each value to get list of vectors
                unit_z = func(factor)
            else:
                # Single value - ensure it's a float
                if not isinstance(factor, (int, float)):
                    try:
                        factor = float(factor)
                    except (ValueError, TypeError):
                        factor = 1.0
                unit_z = func(factor)
            return {'Vector': unit_z, 'Unit vector': unit_z}
        
        elif comp_type == 'Construct Point':
            x = inputs.get('X coordinate', 0.0)
            y = inputs.get('Y coordinate', 0.0)
            z = inputs.get('Z coordinate', 0.0)
            point = func(x, y, z)
            return {'Point': point}
        
        elif comp_type == 'Addition':
            a = inputs.get('A') or inputs.get('First')
            b = inputs.get('B') or inputs.get('Second')
            if a is None or b is None:
                raise ValueError(f"Addition component missing inputs: A={a}, B={b}")
            result = func(a, b)
            return {'Result': result}
        
        elif comp_type == 'Subtraction':
            a = inputs.get('A') or inputs.get('First')
            b = inputs.get('B') or inputs.get('Second')
            if a is None or b is None:
                # Debug for Subtraction components
                if comp_id in ['d055df7d-4a48-4ccd-b770-433bbaa60269', 'e2671ced-ddeb-4187-8048-66f3d519cefb']:
                    print(f"DEBUG Subtraction {comp_id[:8]}... inputs: {inputs}")
                    print(f"  Input A: {a}")
                    print(f"  Input B: {b}")
                    # Check param_info for persistent_values
                    for param_key, input_info in comp_info.get('inputs', {}).items():
                        param_info_from_obj = comp_info['obj'].get('params', {}).get(param_key, {})
                        print(f"  {param_key} persistent_values in data: {param_info_from_obj.get('data', {}).get('persistent_values')}")
                raise ValueError(f"Subtraction component missing inputs: A={a}, B={b}")
            result = func(a, b)
            # Also store result in output_params if this component has output parameters
            comp_obj = comp_info.get('obj', {})
            for param_key, param_info in comp_obj.get('params', {}).items():
                if param_key.startswith('param_output'):
                    param_guid = param_info.get('data', {}).get('InstanceGuid')
                    if param_guid:
                        output_params[param_guid] = {
                            'obj': comp_obj,
                            'param_key': param_key,
                            'param_info': param_info
                        }
            return {'Result': result}
        
        elif comp_type == 'Negative':
            value = inputs.get('Value')
            if value is None:
                value = inputs.get('Number')
            # Debug
            if comp_id == "a69d2e4a-b63b-40d0-838f-dff4d90a83ce":
                print(f"DEBUG Negative component: inputs={inputs}, value={value}")
            if value is None:
                raise ValueError(f"Negative component missing Value input")
            result = func(value)
            return {'Result': result}
        
        elif comp_type == 'Multiply':
            a = inputs.get('A') or inputs.get('First')
            b = inputs.get('B') or inputs.get('Second')
            if a is None or b is None:
                raise ValueError(f"Multiply component missing inputs: A={a}, B={b}")
            result = func(a, b)
            return {'Result': result}
        
        elif comp_type == 'Division':
            a = inputs.get('A') or inputs.get('First')
            b = inputs.get('B') or inputs.get('Second')
            if a is None or b is None:
                raise ValueError(f"Division component missing inputs: A={a}, B={b}")
            result = func(a, b)
            # Also store result in output_params if this component has output parameters
            comp_obj = comp_info.get('obj', {})
            for param_key, param_info in comp_obj.get('params', {}).items():
                if param_key.startswith('param_output'):
                    param_guid = param_info.get('data', {}).get('InstanceGuid')
                    if param_guid:
                        output_params[param_guid] = {
                            'obj': comp_obj,
                            'param_key': param_key,
                            'param_info': param_info
                        }
            return {'Result': result}
        
        elif comp_type == 'Series':
            start = inputs.get('Start', 0.0)
            count = inputs.get('Count', 0)
            step = inputs.get('Step', 1.0)
            series = func(start, count, step)
            return {'Series': series}
        
        elif comp_type == 'List Item':
            list_data = inputs.get('List')
            index = inputs.get('Index', 0)
            wrap = inputs.get('Wrap', False)
            if list_data is None:
                raise ValueError(f"List Item component missing List input")
            
            # In Grasshopper, if a single value is connected to List Item, it's automatically wrapped in a list
            # Convert single values (dicts, lists with one item, etc.) to a list
            if not isinstance(list_data, list):
                # Wrap single value in a list
                list_data = [list_data]
            
            # Ensure index is an integer
            if not isinstance(index, (int, float)):
                try:
                    index = int(index)
                except (ValueError, TypeError):
                    index = 0
            
            # Handle wrap behavior
            if wrap and isinstance(list_data, list) and len(list_data) > 0:
                # Wrap index to list bounds (handles both positive and negative indices)
                index = index % len(list_data)
                # For negative indices, modulo gives a positive result, but we need to handle it correctly
                # Python's % operator already handles negatives correctly (e.g., -1 % 5 = 4)
                # So this should work as-is
            
            item = func(list_data, int(index))
            return {'Item': item}
        
        elif comp_type == 'Value List':
            # Value List might have values stored in its parameters
            values = inputs.get('Values') or inputs.get('List')
            if values is None:
                # Check if component has stored values in its params
                param_info = comp_info['obj'].get('params', {})
                for param_key, param_data in param_info.items():
                    if param_key.startswith('param_input'):
                        persistent_values = param_data.get('persistent_values', [])
                        param_values = param_data.get('values', [])
                        if persistent_values:
                            # Try to parse as list
                            try:
                                values = [float(v) if '.' in str(v) else int(v) for v in persistent_values if v and str(v).strip()]
                                break
                            except (ValueError, TypeError):
                                pass
                        elif param_values:
                            try:
                                values = [float(v) if '.' in str(v) else int(v) for v in param_values if v and str(v).strip()]
                                break
                            except (ValueError, TypeError):
                                pass
                
                # Check external inputs
                if values is None:
                    external_inputs = get_external_inputs()
                    if comp_id in external_inputs:
                        ext_value = external_inputs[comp_id]
                        # Value List can have selected value (single number) or all values (list)
                        # If it's a single number, wrap it in a list
                        if isinstance(ext_value, list):
                            values = ext_value
                        elif isinstance(ext_value, (int, float)):
                            # Selected value from Value List - use it directly
                            values = [ext_value]
                        else:
                            values = [ext_value] if ext_value is not None else []
                
                # If still None, check if it has sources (might be getting values from another component)
                if values is None:
                    has_sources = False
                    for param_key, param_data in param_info.items():
                        if param_key.startswith('param_input'):
                            sources = param_data.get('sources', [])
                            if sources:
                                has_sources = True
                                break
                    if not has_sources:
                        # No sources - might be external input, return placeholder
                        print(f"Warning: Value List component {comp_id[:8]}... has no inputs - treating as external (needs values from GHX or screenshots)")
                        # For now, return empty list - this will need to be filled from screenshots
                        return {'Values': []}
            
            if values is None:
                raise ValueError(f"Value List component missing Values input")
            result = func(values)
            return {'Values': result}
        
        elif comp_type == 'Number':
            value = inputs.get('Value') or inputs.get('Number')
            if value is None:
                # Number component might have a constant value stored
                # Check if it's in external inputs or has a default
                external_inputs = get_external_inputs()
                if comp_id in external_inputs:
                    value = external_inputs[comp_id]
                else:
                    # Check if component has a stored value in its params
                    param_info = comp_info['obj'].get('params', {})
                    for param_key, param_data in param_info.items():
                        if param_key.startswith('param_input'):
                            persistent_values = param_data.get('persistent_values', [])
                            values = param_data.get('values', [])
                            if persistent_values:
                                try:
                                    value = float(persistent_values[0])
                                    break
                                except (ValueError, IndexError):
                                    pass
                            elif values:
                                try:
                                    value = float(values[0])
                                    break
                                except (ValueError, IndexError):
                                    pass
                
                # If still None, check if Number component has a Source connection
                # (Number components can get values from other components via Source item in GHX)
                if value is None:
                    # Load number component sources mapping
                    try:
                        with open('number_component_sources.json', 'r') as f:
                            number_sources = json.load(f)
                        
                        if comp_id in number_sources:
                            source_guid = number_sources[comp_id]['source_guid']
                            
                            # Check if source is in external inputs
                            if source_guid in external_inputs:
                                source_value = external_inputs[source_guid]['value']
                                value = source_value
                            # Check if source is already evaluated
                            elif source_guid in evaluated:
                                source_result = evaluated[source_guid]
                                # If it's a dict, try to get Result or first value
                                if isinstance(source_result, dict):
                                    value = source_result.get('Result') or list(source_result.values())[0] if source_result else None
                                else:
                                    value = source_result
                            # Check if source is an output parameter
                            elif source_guid in output_params:
                                source_info = output_params[source_guid]
                                source_obj_guid = source_info['obj'].get('instance_guid')
                                if source_obj_guid in evaluated:
                                    source_outputs = evaluated[source_obj_guid]
                                    if isinstance(source_outputs, dict):
                                        param_name = source_info['param_info'].get('data', {}).get('NickName', '')
                                        value = source_outputs.get(param_name) or list(source_outputs.values())[0] if source_outputs else None
                                    else:
                                        value = source_outputs
                                else:
                                    # Parent component not yet evaluated - this is a dependency issue
                                    # The component should be evaluated first, but if it's not in the graph,
                                    # we can't resolve it. For now, skip and let it fail with a clear message
                                    print(f"Warning: Number component {comp_id[:8]}... source component {source_obj_guid[:8]}... not yet evaluated")
                    except FileNotFoundError:
                        pass
                
                if value is None:
                    # Check if source_guid is an output parameter directly (not through Panel)
                    # Sometimes Number components can connect directly to output parameters
                    if source_guid in output_params:
                        source_info = output_params[source_guid]
                        source_obj_guid = source_info['obj'].get('instance_guid')
                        if source_obj_guid and source_obj_guid in evaluated:
                            # Get the output from the source component
                            comp_outputs = evaluated.get(source_obj_guid, {})
                            if isinstance(comp_outputs, dict):
                                source_param_name = source_info['param_info'].get('data', {}).get('NickName', '')
                                for key in [source_param_name, 'Result', 'Value', 'Output']:
                                    if key in comp_outputs:
                                        value = comp_outputs[key]
                                        break
                                if value is None and comp_outputs:
                                    value = list(comp_outputs.values())[0]
                            elif comp_outputs is not None:
                                value = comp_outputs
                    
                    # If still None, check if source is a Panel that has its own Source connection
                    if value is None:
                        source_obj = None
                        for key, obj in all_objects.items():
                            if obj.get('instance_guid') == source_guid:
                                source_obj = obj
                                break
                        
                        if source_obj and source_obj.get('type') == 'Panel':
                            # Panel has a Source connection - need to trace it
                            try:
                                import os
                                if os.path.exists('panel_sources.json'):
                                    with open('panel_sources.json', 'r') as f:
                                        panel_sources = json.load(f)
                                    
                                    panel_source_guid = panel_sources.get(source_guid, {}).get('source_guid')
                                    if panel_source_guid:
                                        # Panel's source is an output parameter - resolve it
                                        if panel_source_guid in output_params:
                                            source_info = output_params[panel_source_guid]
                                            source_obj_guid = source_info['obj'].get('instance_guid')
                                            if source_obj_guid:
                                                if source_obj_guid in evaluated:
                                                    # Get the output from the source component
                                                    comp_outputs = evaluated.get(source_obj_guid, {})
                                                    if isinstance(comp_outputs, dict):
                                                        source_param_name = source_info['param_info'].get('data', {}).get('NickName', '')
                                                        for key in [source_param_name, 'Result', 'Value', 'Output']:
                                                            if key in comp_outputs:
                                                                value = comp_outputs[key]
                                                                break
                                                        if value is None and comp_outputs:
                                                            value = list(comp_outputs.values())[0]
                                                    elif comp_outputs is not None:
                                                        value = comp_outputs
                                
                                # If panel_sources.json doesn't have it, check if Panel's source is a Number component
                                # Panels can source from Number components (from GHX Source item)
                                # Check number_component_sources.json to find the Panel's source Number component
                                if value is None:
                                    try:
                                        with open('number_component_sources.json', 'r') as f:
                                            number_sources = json.load(f)
                                        
                                        # Check if Panel's source (source_guid) is a Number component in number_sources
                                        # The Panel's Source item in GHX points to a Number component GUID
                                        if source_guid in number_sources:
                                            # Panel sources from this Number component
                                            # Get the Number component's source
                                            panel_num_source_guid = number_sources[source_guid]['source_guid']
                                            
                                            # Resolve the Number component's source (output parameter or component)
                                            if panel_num_source_guid in output_params:
                                                panel_num_source_info = output_params[panel_num_source_guid]
                                                panel_num_source_obj_guid = panel_num_source_info['obj'].get('instance_guid')
                                                if panel_num_source_obj_guid and panel_num_source_obj_guid in evaluated:
                                                    panel_num_comp_outputs = evaluated.get(panel_num_source_obj_guid, {})
                                                    if isinstance(panel_num_comp_outputs, dict):
                                                        panel_num_param_name = panel_num_source_info['param_info'].get('data', {}).get('NickName', '')
                                                        for key in [panel_num_param_name, 'Result', 'Value', 'Output']:
                                                            if key in panel_num_comp_outputs:
                                                                value = panel_num_comp_outputs[key]
                                                                break
                                                        if value is None and panel_num_comp_outputs:
                                                            value = list(panel_num_comp_outputs.values())[0]
                                                    elif panel_num_comp_outputs is not None:
                                                        value = panel_num_comp_outputs
                                    except FileNotFoundError:
                                        pass
                                
                                # Also check if Panel's source is directly a Number component (from GHX)
                                # Panels can source from Number components directly (Source item in GHX)
                                if value is None:
                                    # Check if Panel's source is a Number component that's been evaluated
                                    panel_source_obj = None
                                    for key, obj in all_objects.items():
                                        if obj.get('instance_guid') == source_guid:
                                            panel_source_obj = obj
                                            break
                                    
                                    # If Panel source is a Number component, get its value
                                    if panel_source_obj and panel_source_obj.get('type') == 'Number':
                                        # Check if this Number component has been evaluated
                                        if source_guid in evaluated:
                                            num_result = evaluated[source_guid]
                                            if isinstance(num_result, dict):
                                                value = num_result.get('Value') or list(num_result.values())[0] if num_result else None
                                            else:
                                                value = num_result
                                        else:
                                            # Number component not yet evaluated - try to resolve it
                                            # Check if it has a source connection in number_component_sources.json
                                            try:
                                                with open('number_component_sources.json', 'r') as f:
                                                    number_sources = json.load(f)
                                                
                                                if source_guid in number_sources:
                                                    num_source_guid = number_sources[source_guid]['source_guid']
                                                    # Recursively resolve the Number component's source
                                                    # Check if it's an output parameter
                                                    if num_source_guid in output_params:
                                                        num_source_info = output_params[num_source_guid]
                                                        num_source_obj_guid = num_source_info['obj'].get('instance_guid')
                                                        if num_source_obj_guid and num_source_obj_guid in evaluated:
                                                            num_comp_outputs = evaluated.get(num_source_obj_guid, {})
                                                            if isinstance(num_comp_outputs, dict):
                                                                num_param_name = num_source_info['param_info'].get('data', {}).get('NickName', '')
                                                                for key in [num_param_name, 'Result', 'Value', 'Output']:
                                                                    if key in num_comp_outputs:
                                                                        value = num_comp_outputs[key]
                                                                        break
                                                                if value is None and num_comp_outputs:
                                                                    value = list(num_comp_outputs.values())[0]
                                                            elif num_comp_outputs is not None:
                                                                value = num_comp_outputs
                                            except FileNotFoundError:
                                                pass
                            except Exception as e:
                                # Silently fail - will be handled by other resolution paths
                                pass
                    
                    # Also check external_inputs by object_guid
                    if value is None:
                        external_inputs = get_external_inputs()
                        for key, ext_val in external_inputs.items():
                            if isinstance(ext_val, dict) and ext_val.get('object_guid') == source_guid:
                                value = ext_val.get('value', ext_val)
                                break
                
                if value is None:
                    raise ValueError(f"Number component missing Value input (source: {source_guid[:8] if 'source_guid' in locals() else 'unknown'}...)")
            result = func(value)
            return {'Value': result}
        
        elif comp_type == 'Number Slider':
            value = inputs.get('Value') or inputs.get('Number')
            if value is None:
                # Slider might have a default value - check external inputs
                external_inputs = get_external_inputs()
                if comp_id in external_inputs:
                    ext_value = external_inputs[comp_id]
                    if isinstance(ext_value, dict):
                        value = ext_value.get('value', ext_value)
                    else:
                        value = ext_value
                else:
                    # Check by object_guid in external_inputs
                    for key, ext_val in external_inputs.items():
                        if isinstance(ext_val, dict) and ext_val.get('object_guid') == comp_id:
                            value = ext_val.get('value', ext_val)
                            break
                    if value is None:
                        raise ValueError(f"Number Slider component missing Value input")
            result = func(value)
            return {'Value': result}
        
        elif comp_type == 'Surface':
            geometry = inputs.get('Geometry') or inputs.get('Surface')
            if geometry is None:
                # Surface component has Source at Container level (not in param_input)
                # Check Container-level Source: dbc236d4... (Rectangle output from Rectangle 2Pt)
                source_guid = 'dbc236d4-a2fe-48a8-a86e-eebfb04b1053'
                if source_guid in output_params:
                    source_info = output_params[source_guid]
                    source_obj_guid = source_info['obj'].get('instance_guid')
                    if source_obj_guid in evaluated:
                        comp_outputs = evaluated.get(source_obj_guid, {})
                        if isinstance(comp_outputs, dict):
                            source_param_name = source_info['param_info'].get('data', {}).get('NickName', '')
                            for key in [source_param_name, 'Rectangle', 'Result', 'Value', 'Output', 'Geometry']:
                                if key in comp_outputs:
                                    geometry = comp_outputs[key]
                                    break
                            if geometry is None and comp_outputs:
                                geometry = list(comp_outputs.values())[0]
                        else:
                            geometry = comp_outputs
                
                # If still no geometry, check param_input sources
                if geometry is None:
                    param_info = comp_info['obj'].get('params', {})
                    for param_key, param_data in param_info.items():
                        if param_key.startswith('param_input'):
                            sources = param_data.get('sources', [])
                            if sources:
                                # Try to resolve from sources
                                for source in sources:
                                    source_guid_conn = source.get('source_guid') or source.get('guid')
                                    if source_guid_conn in output_params:
                                        source_info = output_params[source_guid_conn]
                                        source_obj_guid = source_info['obj'].get('instance_guid')
                                        if source_obj_guid in evaluated:
                                            comp_outputs = evaluated.get(source_obj_guid, {})
                                            if isinstance(comp_outputs, dict):
                                                for key in ['Rectangle', 'Result', 'Value', 'Output', 'Geometry']:
                                                    if key in comp_outputs:
                                                        geometry = comp_outputs[key]
                                                        break
                                                if geometry is None and comp_outputs:
                                                    geometry = list(comp_outputs.values())[0]
                                            else:
                                                geometry = comp_outputs
                                            break
                                break
                
                # If still no geometry, treat as external input
                if geometry is None:
                    print(f"Warning: Surface component {comp_id[:8]}... has no inputs - treating as external")
                    geometry = {'surface': 'external_surface_placeholder'}
            
            result = func(geometry)
            return {'Surface': result, 'Geometry': result}
        
        elif comp_type == 'Area':
            geometry = inputs.get('Geometry')
            if geometry is None:
                raise ValueError(f"Area component missing Geometry input")
            
            result = func(geometry)
            # Area component returns dict with 'Area' and 'Centroid'
            if isinstance(result, dict):
                return result
            else:
                # Fallback for old return format
                return {'Area': result, 'Centroid': [0.0, 0.0, 0.0]}
        
        elif comp_type == 'Move':
            geometry = inputs.get('Geometry')
            motion = inputs.get('Motion')
            
            # Special case: "New Sun" component Motion input
            comp_nickname = comp_info['obj'].get('nickname') or comp_info['obj'].get('NickName', '')
            if comp_nickname == 'New Sun':
                # GHX has PersistentData value [0, 0, 10], but we override with SUN_VECTOR
                # This allows using the actual sun vector instead of the placeholder in GHX
                if motion is None or motion == "\n                                      " or (isinstance(motion, str) and not motion.strip()):
                    motion = SUN_VECTOR
                    print(f"New Sun: Using SUN_VECTOR (fallback): {motion}")
                elif isinstance(motion, list) and len(motion) == 3:
                    # Check if it's the GHX default value [0, 0, 10] - if so, override with SUN_VECTOR
                    if motion == [0.0, 0.0, 10.0]:
                        motion = SUN_VECTOR
                        print(f"New Sun: Overriding GHX default [0, 0, 10] with SUN_VECTOR: {motion}")
                    else:
                        print(f"New Sun: Motion input resolved from GHX: {motion}")
                else:
                    print(f"Warning: New Sun Motion input invalid: {motion}, using SUN_VECTOR")
                    motion = SUN_VECTOR
            
            # Handle multiple Motion sources (vector addition)
            # If motion is a list of vectors (from multiple sources), combine them
            # BUT: if motion is a list of vectors and geometry is a single point,
            # we want to keep the list of vectors to create multiple moved points
            motion_is_list_of_vectors = isinstance(motion, list) and len(motion) > 0 and isinstance(motion[0], list)
            
            if motion_is_list_of_vectors:
                # Motion is a list of vectors
                # Check if we have multiple sources (need to combine) or single source (keep as list)
                # For now, if it's a list of vectors, check if geometry is a single point
                # If so, keep the list to create multiple moved points
                if isinstance(geometry, list) and len(geometry) == 3 and all(isinstance(x, (int, float)) for x in geometry):
                    # Single point with list of motion vectors - keep list to create multiple points
                    # Don't combine, just pass through
                    pass
                else:
                    # Multiple vectors with multiple geometries or other cases - combine by adding
                    if all(isinstance(v, list) and len(v) >= 3 for v in motion):
                        # Combine all vectors element-wise
                        combined = [0.0, 0.0, 0.0]
                        for vec in motion:
                            if len(vec) >= 3:
                                combined[0] += vec[0] if isinstance(vec[0], (int, float)) else 0.0
                                combined[1] += vec[1] if isinstance(vec[1], (int, float)) else 0.0
                                combined[2] += vec[2] if isinstance(vec[2], (int, float)) else 0.0
                        motion = combined
                    else:
                        # Take first vector if structure is unexpected
                        motion = motion[0] if len(motion[0]) >= 3 else [0.0, 0.0, 0.0]
            
            # Geometry is optional in Move component - if None, return None or placeholder
            if geometry is None:
                # For external Surface components, allow None geometry
                # Return a placeholder geometry
                geometry = {'surface': 'placeholder_surface'}
            if motion is None:
                raise ValueError(f"Move component missing Motion input: Motion={motion}")
            
            # Ensure motion is a list of 3 floats (only if it's not already a list of vectors)
            if not motion_is_list_of_vectors:
                if not isinstance(motion, list):
                    # Try to convert
                    if isinstance(motion, (int, float)):
                        motion = [0.0, 0.0, float(motion)]
                    else:
                        motion = [0.0, 0.0, 0.0]
                elif len(motion) != 3 or not all(isinstance(x, (int, float)) for x in motion):
                    # Pad or truncate to 3 elements
                    motion = list(motion[:3]) + [0.0] * (3 - len(motion))
            
            moved_geometry, transform = func(geometry, motion)
            return {'Geometry': moved_geometry, 'Transform': transform}
        
        elif comp_type == 'Polar Array':
            geometry = inputs.get('Geometry') or inputs.get('Base')
            plane = inputs.get('Plane')
            count = inputs.get('Count', 1)
            angle = inputs.get('Angle', 0.0)
            
            if geometry is None:
                raise ValueError(f"Polar Array component missing Geometry input")
            
            # Validate and fix plane input
            # Plane should be a dict with 'origin', 'x_axis', 'y_axis', 'z_axis'
            # If it's not a valid plane dict, use default
            if plane is None or not isinstance(plane, dict) or 'origin' not in plane:
                # Check param_input_1 (Plane input) parameter GUID
                plane_param = comp_info['obj'].get('params', {}).get('param_input_1', {})
                plane_param_guid = plane_param.get('data', {}).get('InstanceGuid')
                
                # Try external_inputs first
                if plane_param_guid:
                    external_inputs = get_external_inputs()
                    if plane_param_guid in external_inputs:
                        ext_value = external_inputs[plane_param_guid]
                        if isinstance(ext_value, dict):
                            plane_value = ext_value.get('value', ext_value)
                            # Check if it's a valid plane dict
                            if isinstance(plane_value, dict) and 'origin' in plane_value:
                                plane = plane_value
                            else:
                                plane = None
                        else:
                            plane = None
                
                # If still None or invalid, use default plane (XY plane at origin)
                # This matches the GHX PersistentData: Ox=0, Oy=0, Oz=0, Xx=1, Xy=0, Xz=0, Yx=0, Yy=1, Yz=0
                if plane is None or not isinstance(plane, dict) or 'origin' not in plane:
                    plane = {'origin': [0.0, 0.0, 0.0], 'x_axis': [1.0, 0.0, 0.0], 
                            'y_axis': [0.0, 1.0, 0.0], 'z_axis': [0.0, 0.0, 1.0], 'normal': [0.0, 0.0, 1.0]}
            
            # Ensure count is an integer
            if not isinstance(count, (int, float)):
                try:
                    count = int(count)
                except (ValueError, TypeError):
                    count = 1
            
            # Ensure angle is a float
            if not isinstance(angle, (int, float)):
                try:
                    angle = float(angle)
                except (ValueError, TypeError):
                    angle = 0.0
            
            result = func(geometry, plane, int(count), float(angle))
            return {'Geometry': result}
        
        elif comp_type == 'MD Slider':
            value = inputs.get('Value') or inputs.get('Number')
            if value is None:
                # Check external inputs
                external_inputs = get_external_inputs()
                if comp_id in external_inputs:
                    ext_value = external_inputs[comp_id]
                    # MD Slider might return a point3d [x, y, z] or a single value
                    if isinstance(ext_value, dict):
                        ext_val = ext_value.get('value', ext_value)
                        if isinstance(ext_val, list):
                            # If it's a point3d, return the whole point for downstream components
                            # But for the component's own Value output, use first coordinate
                            value = ext_val[0] if len(ext_val) > 0 else 0.0
                            # Store full point for source resolution
                            result = ext_val
                        else:
                            value = ext_val
                            result = value
                    elif isinstance(ext_value, list):
                        # If it's a point3d, return the whole point for downstream components
                        value = ext_value[0] if len(ext_value) > 0 else 0.0
                        result = ext_value
                    else:
                        value = ext_value
                        result = value
                else:
                    # MD Slider might not have a value stored - treat as external input
                    param_info = comp_info['obj'].get('params', {})
                    has_sources = False
                    for param_key, param_data in param_info.items():
                        if param_key.startswith('param_input'):
                            sources = param_data.get('sources', [])
                            if sources:
                                has_sources = True
                                break
                    if not has_sources:
                        print(f"Warning: MD Slider component {comp_id[:8]}... has no value - treating as external (defaulting to 0.0)")
                        value = 0.0
                        result = value
                    else:
                        raise ValueError(f"MD Slider component missing Value input")
            else:
                result = func(value)
            # Return both Value (for component output) and the full point (for source resolution)
            # If result is a list, it's a point3d - return it as-is for downstream components
            if isinstance(result, list):
                return {'Value': result[0] if len(result) > 0 else 0.0, 'Point': result}
            return {'Value': result}
        
        elif comp_type == 'Box 2Pt':
            # Box 2Pt uses "Point A" and "Point B" as input names
            corner1 = inputs.get('Point A') or inputs.get('Corner 1') or inputs.get('Corner A')
            corner2 = inputs.get('Point B') or inputs.get('Corner 2') or inputs.get('Corner B')
            if corner1 is None or corner2 is None:
                raise ValueError(f"Box 2Pt component missing inputs (Point A: {corner1 is not None}, Point B: {corner2 is not None})")
            result = func(corner1, corner2)
            # Debug output to confirm Box 2Pt is working
            if comp_id == 'b908d823-e613-4684-9e94-65a0f60f19b7':
                print(f"  Successfully evaluated Box 2Pt {comp_id[:8]}..., outputs: {result}")
            return {'Box': result}
        
        elif comp_type == 'Rectangle 2Pt':
            plane = inputs.get('Plane')
            pointA = inputs.get('Point A') or inputs.get('Corner A') or inputs.get('Corner 1')
            pointB = inputs.get('Point B') or inputs.get('Corner B') or inputs.get('Corner 2')
            radius = inputs.get('Radius', 0.0)
            
            if pointA is None or pointB is None:
                raise ValueError(f"Rectangle 2Pt component missing inputs: Point A={pointA}, Point B={pointB}")
            
            # Ensure radius is a float
            if not isinstance(radius, (int, float)):
                try:
                    radius = float(radius)
                except (ValueError, TypeError):
                    radius = 0.0
            
            # If plane is None, use default XY plane
            if plane is None:
                plane = {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis': [0, 1, 0], 'z_axis': [0, 0, 1]}
            
            rectangle, length = func(plane, pointA, pointB, radius)
            return {'Rectangle': rectangle, 'Length': length}
        
        elif comp_type == 'PolyLine':
            points = inputs.get('Points') or inputs.get('Vertices')
            closed = inputs.get('Closed', False)
            if points is None:
                raise ValueError(f"PolyLine component missing Points input")
            result = func(points, closed)
            return {'PolyLine': result}
        
        elif comp_type == 'Polygon':
            plane = inputs.get('Plane')
            radius = inputs.get('Radius', 1.0)
            segments = inputs.get('Segments', 3)
            fillet_radius = inputs.get('Fillet Radius', 0.0)
            # Convert to appropriate types
            try:
                radius = float(radius) if not isinstance(radius, (int, float)) else radius
            except (ValueError, TypeError):
                radius = 1.0
            try:
                segments = int(segments) if not isinstance(segments, int) else segments
            except (ValueError, TypeError):
                segments = 3
            try:
                fillet_radius = float(fillet_radius) if not isinstance(fillet_radius, (int, float)) else fillet_radius
            except (ValueError, TypeError):
                fillet_radius = 0.0
            result = func(plane, radius, segments, fillet_radius)
            return {'Polygon': result}
        
        elif comp_type == 'Rotate':
            geometry = inputs.get('Geometry')
            angle = inputs.get('Angle', 0.0)
            plane = inputs.get('Plane')
            if geometry is None:
                raise ValueError(f"Rotate component missing Geometry input")
            # Convert angle to float if it's a string
            try:
                angle = float(angle) if not isinstance(angle, (int, float)) else angle
            except (ValueError, TypeError):
                angle = 0.0
            # Default to XY plane at origin if plane is None
            if plane is None:
                plane = {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis': [0, 1, 0], 'z_axis': [0, 0, 1]}
            result = func(geometry, angle, plane)
            return {'Geometry': result}
        
        elif comp_type == 'Mirror':
            geometry = inputs.get('Geometry')
            plane = inputs.get('Plane')
            if geometry is None:
                # Geometry is optional, but if it's connected, we need it
                # For now, if it's None and has no sources, return None
                raise ValueError(f"Mirror component missing Geometry input")
            # Default to YZ plane at origin if plane is None (common mirror plane)
            if plane is None:
                plane = {'origin': [0, 0, 0], 'x_axis': [0, 1, 0], 'y_axis': [0, 0, 1], 'z_axis': [1, 0, 0]}
            result = func(geometry, plane)
            return {'Geometry': result}
        
        elif comp_type == 'Deconstruct Brep':
            brep = inputs.get('Brep') or inputs.get('Geometry')
            if brep is None:
                raise ValueError(f"Deconstruct Brep component missing Brep input")
            result = func(brep)
            # Deconstruct Brep outputs Faces, Edges, and Vertices
            # Result is already a dict with Faces, Edges, Vertices
            if isinstance(result, dict):
                return result
            # Fallback for old format
            return {'Faces': result, 'Edges': result if isinstance(result, list) else [result], 'Vertices': []}
        
        elif comp_type == 'Point On Curve':
            # Point On Curve has Source and parameter at Container level, not in param_input
            curve = inputs.get('Curve')
            parameter = inputs.get('Parameter')
            
            # Check for Container-level Source and parameter (stored in params as special entries)
            obj_params = comp_info['obj'].get('params', {})
            container_source_entry = obj_params.get('_container_source', {})
            container_parameter_entry = obj_params.get('_container_parameter', {})
            
            # Extract sources and parameter from special entries
            container_sources = container_source_entry.get('sources', []) if isinstance(container_source_entry, dict) else []
            container_parameter = container_parameter_entry.get('value') if isinstance(container_parameter_entry, dict) else None
            
            # Resolve curve from Container-level Source
            if curve is None and container_sources:
                # Use the first source (Point On Curve typically has one source)
                source_info = container_sources[0]
                source_guid = source_info.get('guid')
                if source_guid:
                    if source_guid in output_params:
                        # Resolve the source
                        source_param_info = output_params[source_guid]
                        source_obj_guid = source_param_info['obj'].get('instance_guid')
                        if source_obj_guid in evaluated:
                            comp_outputs = evaluated.get(source_obj_guid, {})
                            if isinstance(comp_outputs, dict):
                                source_param_name = source_param_info['param_info'].get('data', {}).get('NickName', '')
                                for key in [source_param_name, 'Item', 'Result', 'Value', 'Output', 'Edge', 'Curve']:
                                    if key in comp_outputs:
                                        curve = comp_outputs[key]
                                        break
                                if curve is None and comp_outputs:
                                    curve = list(comp_outputs.values())[0]
                            else:
                                curve = comp_outputs
                        else:
                            # Source component not evaluated yet
                            print(f"Warning: Point On Curve source component {source_obj_guid[:8] if source_obj_guid else 'N/A'}... not yet evaluated")
                    else:
                        # Try to resolve as component instance_guid
                        for key, obj in all_objects.items():
                            if obj.get('instance_guid') == source_guid:
                                if source_guid in evaluated:
                                    curve = evaluated[source_guid]
                                    if isinstance(curve, dict):
                                        curve = list(curve.values())[0] if curve else None
                                break
            
            # Get parameter value - use Container-level parameter if available
            if parameter is None:
                if container_parameter is not None:
                    parameter = container_parameter
                else:
                    # Check persistent_values in any param
                    for param_key, param_data in obj_params.items():
                        if param_key.startswith('_'):
                            continue  # Skip special entries
                        if 'persistent_values' in param_data:
                            pv = param_data['persistent_values']
                            if pv and len(pv) > 0:
                                try:
                                    parameter = float(pv[0])
                                    break
                                except (ValueError, TypeError):
                                    pass
                        # Also check in data.persistent_values
                        if 'data' in param_data:
                            pv = param_data['data'].get('persistent_values', [])
                            if pv and len(pv) > 0:
                                try:
                                    parameter = float(pv[0])
                                    break
                                except (ValueError, TypeError):
                                    pass
                    if parameter is None:
                        parameter = 0.0  # Default to 0 (from GHX for this component)
            
            if curve is None:
                raise ValueError(f"Point On Curve component missing Curve input")
            result = func(curve, parameter)
            return {'Point': result}
        
        elif comp_type == 'Point':
            # Point component - passes through or creates a point
            point = inputs.get('Point') or inputs.get('Geometry') or inputs.get('Coordinate')
            if point is None:
                # Check if it has a source connection
                param_info = comp_info['obj'].get('params', {})
                has_sources = False
                for param_key, param_data in param_info.items():
                    if param_key.startswith('param_input'):
                        sources = param_data.get('sources', [])
                        if sources:
                            has_sources = True
                            break
                if not has_sources:
                    # No sources - might be external input, return placeholder point
                    print(f"Warning: Point component {comp_id[:8]}... has no inputs - treating as external")
                    return {'Point': [0.0, 0.0, 0.0]}  # Return placeholder point instead of None
                raise ValueError(f"Point component missing Point input (has sources but couldn't resolve)")
            result = func(point)
            return {'Point': result}
        
        elif comp_type == 'Evaluate Surface':
            surface = inputs.get('Surface')
            point = inputs.get('Point')
            if surface is None:
                raise ValueError(f"Evaluate Surface component missing Surface input")
            if point is None:
                raise ValueError(f"Evaluate Surface component missing Point input")
            # Point can be a list [u, v] or a point [x, y, z]
            # For Evaluate Surface, we need u and v parameters
            # If point is from MD Slider, it might be a point3d [x, y, z] or [u, v, w]
            # MD Slider typically provides [u, v, w] where u and v are the UV coordinates
            if isinstance(point, list):
                if len(point) >= 2:
                    u, v = float(point[0]), float(point[1])
                else:
                    u, v = 0.0, 0.0
            elif isinstance(point, dict):
                # If point is a dict, try to extract value
                point_val = point.get('Value', point.get('value', [0.5, 0.5]))
                if isinstance(point_val, list) and len(point_val) >= 2:
                    u, v = float(point_val[0]), float(point_val[1])
                else:
                    u, v = 0.5, 0.5  # Default UV coordinates
            else:
                u, v = 0.5, 0.5  # Default UV coordinates
            
            result = func(surface, u, v)
            # result is now a dict with 'point' and 'normal' keys
            if isinstance(result, dict):
                normal = result.get('normal', [0.0, 0.0, 1.0])
                return {
                    'Point': result.get('point', [u, v, 0.0]),
                    'Normal': normal,
                    'Frame': None
                }
            else:
                # Fallback for old return format
                return {'Point': result, 'Normal': [0.0, 0.0, 1.0], 'Frame': None}
        
        elif comp_type == 'Divide Length':
            curve = inputs.get('Curve') or inputs.get('Geometry')
            length = inputs.get('Length')
            if curve is None:
                raise ValueError(f"Divide Length component missing Curve input")
            if length is None:
                raise ValueError(f"Divide Length component missing Length input")
            # Convert length to float if needed
            try:
                length = float(length) if not isinstance(length, (int, float)) else length
            except (ValueError, TypeError):
                raise ValueError(f"Divide Length component Length input must be a number, got: {type(length)}")
            result = func(curve, length)
            return {'Points': result, 'Parameters': []}  # Simplified outputs
        
        elif comp_type == 'Project':
            curve = inputs.get('Curve') or inputs.get('Geometry') or inputs.get('Points')
            target = inputs.get('Brep') or inputs.get('Target') or inputs.get('Surface')
            direction = inputs.get('Direction')
            if curve is None:
                raise ValueError(f"Project component missing Curve input")
            if target is None:
                raise ValueError(f"Project component missing Brep/Target input")
            result = func(curve, target, direction)
            return {'Curve': result, 'Geometry': result, 'Points': result if isinstance(result, list) else [result]}
        
        elif comp_type == 'Panel':
            # Panel is a pass-through component - it doesn't need evaluation
            # Panels just display values from their Source connection
            # If a component sources from a Panel, we should resolve the Panel's source instead
            # For now, return None or a placeholder - Panel values should be resolved via their Source
            return None
        
        else:
            raise ValueError(f"Component type {comp_type} not yet implemented in evaluator")
    except Exception as e:
        raise ValueError(f"Error evaluating {comp_type} component ({comp_id[:8]}...): {e}")


def topological_sort(graph: Dict, all_objects: Dict, output_params: Dict) -> List[str]:
    """
    Topological sort of components by dependency order.
    Returns list of component GUIDs in evaluation order.
    """
    # Build dependency map: comp_id -> set of dependency GUIDs
    deps = {}
    for comp_id, comp_info in graph['components'].items():
        deps[comp_id] = set()
        
        if comp_info['type'] == 'component':
            # Dependencies are sources of inputs
            for param_key, input_info in comp_info.get('inputs', {}).items():
                for source in input_info.get('sources', []):
                    source_guid = source.get('source_guid')
                    if source_guid:
                        # If source is output param, add parent component
                        if source_guid in output_params:
                            parent_obj_guid = output_params[source_guid]['obj'].get('instance_guid')
                            if parent_obj_guid and parent_obj_guid in graph['components']:
                                deps[comp_id].add(parent_obj_guid)
                        elif source_guid in graph['components']:
                            deps[comp_id].add(source_guid)
            
            # Special case: Point On Curve depends on List Item output
            # Point On Curve has Container-level Source (8e8b33cf...) that wasn't parsed into inputs
            if comp_id == '6ce8bcba-18ea-46fc-a145-b1c1b45c304f':  # Point On Curve
                list_item_guid = 'd89d47e0-f858-44d9-8427-fdf2e3230954'  # List Item
                if list_item_guid in graph['components']:
                    deps[comp_id].add(list_item_guid)
                    print(f"DEBUG topological_sort: Added dependency {list_item_guid[:8]}... (List Item) to Point On Curve component {comp_id[:8]}...")
            
            # Special handling for Number components with Source connections
            if comp_info['obj'].get('type') == 'Number':
                try:
                    with open('number_component_sources.json', 'r') as f:
                        number_sources = json.load(f)
                    
                    if comp_id in number_sources:
                        source_guid = number_sources[comp_id]['source_guid']
                        # Check if source is a Panel - if so, trace its source
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
                                    if panel_source_guid:
                                        # Panel's source is an output parameter - add its parent component
                                        if panel_source_guid in output_params:
                                            parent_obj_guid = output_params[panel_source_guid]['obj'].get('instance_guid')
                                            if parent_obj_guid and parent_obj_guid in graph['components']:
                                                deps[comp_id].add(parent_obj_guid)
                                                # Debug output for Number component dependency
                                                if comp_id == '06d478b1-5fdf-4861-8f0e-1772b5bbf067':
                                                    print(f"DEBUG topological_sort: Added dependency {parent_obj_guid[:8]}... (Division) to Number component {comp_id[:8]}...")
                            except Exception as e:
                                if comp_id == '06d478b1-5fdf-4861-8f0e-1772b5bbf067':
                                    print(f"DEBUG topological_sort: Exception tracing Panel source: {e}")
                                pass
                        # If source is an output parameter, add its parent component
                        elif source_guid in output_params:
                            parent_obj_guid = output_params[source_guid]['obj'].get('instance_guid')
                            if parent_obj_guid and parent_obj_guid in graph['components']:
                                deps[comp_id].add(parent_obj_guid)
                        # If source is a component directly
                        elif source_guid in graph['components']:
                            deps[comp_id].add(source_guid)
                except FileNotFoundError:
                    pass
        
        elif comp_info['type'] == 'output_param':
            # Output param depends on its parent component
            parent_obj_guid = comp_info['obj'].get('instance_guid')
            if parent_obj_guid and parent_obj_guid in graph['components']:
                deps[comp_id] = {parent_obj_guid}
    
    # Debug: Check dependencies for key components
    num_id = '06d478b1-5fdf-4861-8f0e-1772b5bbf067'
    div_id = 'f9a68fee-bd6c-477a-9d8e-ae9e35697ab1'
    if num_id in deps:
        print(f"DEBUG topological_sort: Number component {num_id[:8]}... dependencies: {sorted(deps[num_id])}")
    if div_id in deps:
        print(f"DEBUG topological_sort: Division component {div_id[:8]}... dependencies: {sorted(deps[div_id])}")
        # Check Division inputs
        div_comp = graph['components'][div_id]
        div_inputs = div_comp.get('inputs', {})
        print(f"DEBUG topological_sort: Division has {len(div_inputs)} inputs")
        for input_key, input_info in div_inputs.items():
            sources = input_info.get('sources', [])
            print(f"  {input_key}: {len(sources)} sources")
            for source in sources:
                source_guid = source.get('source_guid')
                source_obj_guid = source.get('source_obj_guid')
                if source_guid in output_params:
                    parent_guid = output_params[source_guid]['obj'].get('instance_guid')
                    parent_str = parent_guid[:8] if parent_guid else 'N/A'
                    in_deps = parent_guid in deps.get(div_id, set()) if parent_guid else False
                    print(f"    Source {source_guid[:8]}... -> parent {parent_str}... (in deps: {in_deps})")
    
    # Topological sort
    sorted_list = []
    remaining = set(graph['components'].keys())
    
    while remaining:
        # Find nodes with no unresolved dependencies
        ready = [node for node in remaining 
                if not (deps.get(node, set()) & remaining)]
        
        if not ready:
            # Circular dependency or missing deps - add remaining
            sorted_list.extend(remaining)
            break
        
        sorted_list.extend(ready)
        remaining -= set(ready)
    
    return sorted_list


def evaluate_graph(graph: Dict, all_objects: Dict, output_params: Dict,
                   external_inputs: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Evaluate the complete component graph.
    Returns dict mapping component GUIDs to their outputs.
    """
    if external_inputs is None:
        external_inputs = get_external_inputs()
    
    # Get evaluation order
    eval_order = topological_sort(graph, all_objects, output_params)
    
    # Store evaluated results
    evaluated = {}
    
    # Evaluate each component in order
    for comp_id in eval_order:
        comp_info = graph['components'][comp_id]
        
        if comp_info['type'] == 'output_param':
            # Output parameter - get value from parent component
            parent_obj_guid = comp_info['obj'].get('instance_guid')
            if parent_obj_guid in evaluated:
                # Get the specific output parameter
                parent_outputs = evaluated[parent_obj_guid]
                param_key = comp_info['param_key']
                # Map param_key to output name
                param_name = comp_info['param_info'].get('data', {}).get('NickName', param_key)
                if isinstance(parent_outputs, dict):
                    evaluated[comp_id] = parent_outputs.get(param_name)
                else:
                    # Single output value
                    evaluated[comp_id] = parent_outputs
            else:
                raise ValueError(f"Parent component {parent_obj_guid[:8]}... not yet evaluated for output param {comp_id[:8]}...")
        else:
            # Regular component - evaluate it
            try:
                # Debug: print component being evaluated for key components
                if comp_id in ['d055df7d-4a48-4ccd-b770-433bbaa60269', 'e2671ced-ddeb-4187-8048-66f3d519cefb', 'f9a68fee-bd6c-477a-9d8e-ae9e35697ab1', '06d478b1-5fdf-4861-8f0e-1772b5bbf067']:
                    print(f"Evaluating component {comp_id[:8]}... ({comp_info['obj']['type']})")
                outputs = evaluate_component(comp_id, comp_info, evaluated,
                                           all_objects, output_params)
                evaluated[comp_id] = outputs
                if comp_id in ['d055df7d-4a48-4ccd-b770-433bbaa60269', 'e2671ced-ddeb-4187-8048-66f3d519cefb', 'f9a68fee-bd6c-477a-9d8e-ae9e35697ab1']:
                    print(f"  Successfully evaluated {comp_id[:8]}..., outputs: {outputs}")
                    # Check if output params were added
                    comp_obj = comp_info.get('obj', {})
                    for param_key, param_info in comp_obj.get('params', {}).items():
                        if param_key.startswith('param_output'):
                            param_guid = param_info.get('data', {}).get('InstanceGuid')
                            if param_guid:
                                print(f"  Output param {param_guid[:8]}... in output_params: {param_guid in output_params}")
            except Exception as e:
                print(f"Error evaluating component {comp_id[:8]}... ({comp_info['obj']['type']}): {e}")
                raise
    
    return evaluated


if __name__ == '__main__':
    print("Loading component graph...")
    graph = load_component_graph()
    
    print(f"Loaded {len(graph['components'])} components")
    print(f"Evaluation order: {len(graph.get('sorted_order', []))} components")
    
    # Load all objects for reference
    with open('rotatingslats_data.json', 'r') as f:
        data = json.load(f)
    
    all_objects = {**data['group_objects'], **data['external_objects']}
    
    # Load external components from JSON files and add to all_objects
    external_component_files = [
        'external_division_component.json',
        'external_subtraction_e2671ced.json',
        'external_subtraction_components.json',
        'external_vector_d0668a07_component.json',
        'external_vector_2pt_1f794702_component.json',
        'external_mirror_component.json',
        'external_rotate_component.json',
        'external_polygon_component.json',
        'external_area_component.json'
    ]
    
    for ext_file in external_component_files:
        try:
            import os
            if os.path.exists(ext_file):
                with open(ext_file, 'r') as f:
                    comp = json.load(f)
                    comp_guid = comp.get('instance_guid') or comp.get('guid')
                    if comp_guid:
                        all_objects[comp_guid] = comp
        except Exception as e:
            pass  # Ignore missing files
    
    # Build output params map
    output_params = {}
    for key, obj in all_objects.items():
        for param_key, param_info in obj.get('params', {}).items():
            param_guid = param_info.get('data', {}).get('InstanceGuid')
            if param_guid:
                output_params[param_guid] = {
                    'obj': obj,
                    'param_key': param_key,
                    'param_info': param_info
                }
    
    print("\nEvaluating computation chain...")
    try:
        results = evaluate_graph(graph, all_objects, output_params)
        
        # Find final output (Degrees output parameter)
        final_output_guid = "4d5670e5-1abc-417e-b9ce-3cf7878b98c2"
        
        # Generate markdown report with ordered results
        sorted_order = graph.get('sorted_order', [])
        md_lines = []
        md_lines.append("# Rotatingslats Evaluation Results")
        md_lines.append("")
        md_lines.append("## Evaluation Chain (Topological Order)")
        md_lines.append("")
        md_lines.append("Components evaluated in dependency order, from early inputs to final outputs.")
        md_lines.append("")
        md_lines.append("| # | Component GUID | Type | Name/NickName | Output |")
        md_lines.append("|---|----------------|------|---------------|--------|")
        
        # Track which components have been printed
        printed_components = set()
        
        # Print in topological order
        for idx, comp_id in enumerate(sorted_order, 1):
            if comp_id in results:
                # Check if this is an output parameter or a component
                if comp_id in output_params:
                    # It's an output parameter - get parent component info
                    param_info = output_params[comp_id]
                    parent_obj = param_info.get('obj', {})
                    parent_guid = parent_obj.get('instance_guid')
                    param_name = param_info.get('param_info', {}).get('data', {}).get('NickName') or param_info.get('param_info', {}).get('data', {}).get('Name', '')
                    comp_type = parent_obj.get('type', 'Unknown')
                    nickname = parent_obj.get('nickname') or parent_obj.get('NickName', '')
                    name = parent_obj.get('name') or parent_obj.get('Name', '')
                    display_name = nickname if nickname else name
                    if param_name:
                        display_name = f"{display_name}.{param_name}" if display_name else param_name
                else:
                    # It's a component
                    comp_obj = all_objects.get(comp_id, {})
                    nickname = comp_obj.get('nickname') or comp_obj.get('NickName', '')
                    name = comp_obj.get('name') or comp_obj.get('Name', '')
                    comp_type = comp_obj.get('type', 'Unknown')
                    display_name = nickname if nickname else name
                
                output = results[comp_id]
                # Format output for markdown (truncate if too long)
                output_str = str(output)
                if len(output_str) > 100:
                    output_str = output_str[:97] + "..."
                output_str = output_str.replace('|', '\\|')  # Escape pipes
                
                if display_name:
                    md_lines.append(f"| {idx} | `{comp_id[:8]}...` | {comp_type} | `{display_name}` | `{output_str}` |")
                else:
                    md_lines.append(f"| {idx} | `{comp_id[:8]}...` | {comp_type} | - | `{output_str}` |")
                
                printed_components.add(comp_id)
        
        # Add any remaining results not in sorted_order
        remaining = [comp_id for comp_id in results.keys() if comp_id not in printed_components]
        if remaining:
            md_lines.append("")
            md_lines.append("## Additional Results (Not in Main Chain)")
            md_lines.append("")
            md_lines.append("| Component GUID | Type | Name/NickName | Output |")
            md_lines.append("|---|----------------|------|---------------|--------|")
            for comp_id in remaining:
                comp_obj = all_objects.get(comp_id, {})
                nickname = comp_obj.get('nickname') or comp_obj.get('NickName', '')
                name = comp_obj.get('name') or comp_obj.get('Name', '')
                comp_type = comp_obj.get('type', 'Unknown')
                display_name = nickname if nickname else name
                
                output = results[comp_id]
                output_str = str(output)
                if len(output_str) > 100:
                    output_str = output_str[:97] + "..."
                output_str = output_str.replace('|', '\\|')
                
                if display_name:
                    md_lines.append(f"| `{comp_id[:8]}...` | {comp_type} | `{display_name}` | `{output_str}` |")
                else:
                    md_lines.append(f"| `{comp_id[:8]}...` | {comp_type} | - | `{output_str}` |")
        
        # Final output summary
        md_lines.append("")
        md_lines.append("## Final Output")
        md_lines.append("")
        if final_output_guid in results:
            final_angles = results[final_output_guid]
            # Get parent component info
            if final_output_guid in output_params:
                param_info = output_params[final_output_guid]
                parent_obj = param_info.get('obj', {})
                parent_guid = parent_obj.get('instance_guid')
                parent_type = parent_obj.get('type', 'Unknown')
                parent_name = parent_obj.get('nickname') or parent_obj.get('NickName', '') or parent_obj.get('name') or parent_obj.get('Name', '')
                param_name = param_info.get('param_info', {}).get('data', {}).get('NickName') or param_info.get('param_info', {}).get('data', {}).get('Name', '')
                md_lines.append(f"**Degrees Output** (`{final_output_guid[:8]}...`)")
                md_lines.append("")
                md_lines.append(f"- **Parent Component**: `{parent_guid[:8] if parent_guid else 'N/A'}...` ({parent_type}) '{parent_name}'")
                md_lines.append(f"- **Output Parameter**: `{param_name}`")
                md_lines.append(f"- **Value**: `{final_angles}`")
            else:
                md_lines.append(f"**Degrees Output** (`{final_output_guid[:8]}...`): `{final_angles}`")
        else:
            # Try to find Degrees component output
            degrees_comp_guid = "fa0ba5a6-7dd9-43f4-a82a-cf02841d0f58"
            if degrees_comp_guid in results:
                degrees_output = results[degrees_comp_guid]
                if isinstance(degrees_output, dict) and 'Degrees' in degrees_output:
                    final_angles = degrees_output['Degrees']
                    md_lines.append(f"**Degrees Output** (from Degrees component `{degrees_comp_guid[:8]}...`): `{final_angles}`")
                else:
                    md_lines.append(f"**Degrees Output** (from Degrees component `{degrees_comp_guid[:8]}...`): `{degrees_output}`")
            else:
                md_lines.append(f"Final output parameter `{final_output_guid[:8]}...` not found in results.")
                md_lines.append("")
                md_lines.append("### Summary")
                md_lines.append(f"- Total components evaluated: {len(results)}")
                md_lines.append(f"- Components in topological order: {len(printed_components)}")
                md_lines.append(f"- Additional results: {len(remaining)}")
        
        # Write to markdown file
        md_content = "\n".join(md_lines)
        with open('evaluation_results.md', 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"\n[OK] Evaluation results saved to evaluation_results.md")
        print(f"  Total components: {len(results)}")
        print(f"  Components in order: {len(printed_components)}")
        
        # Also print to console (summary)
        if final_output_guid in results:
            final_angles = results[final_output_guid]
            print(f"\nFinal output (Degrees): {final_angles}")
        else:
            print(f"\nFinal output not found. See evaluation_results.md for full results.")
    
    except Exception as e:
        print(f"\nEvaluation error: {e}")
        import traceback
        traceback.print_exc()

