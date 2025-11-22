"""
PHASE 5: Wired Topological Evaluation

Complete evaluation engine that:
1. Performs topological sort of component graph
2. Resolves input wires
3. Handles persistent data
4. Evaluates components in order
5. Caches results
"""

import json
from collections import defaultdict, deque
from typing import Dict, List, Set
from gh_evaluator_core import DataTree, EvaluationContext, COMPONENT_REGISTRY
from gh_components_rotatingslats import *  # Register all components


# ============================================================================
# TOPOLOGICAL SORT
# ============================================================================

def topological_sort(components: List[dict], wires: List[dict]) -> List[str]:
    """
    Perform topological sort on component graph.
    
    Args:
        components: List of component dicts
        wires: List of wire dicts
    
    Returns:
        List of component GUIDs in evaluation order
    
    Raises:
        ValueError: If graph contains cycles
    """
    # Build adjacency list and in-degree map
    adjacency = defaultdict(list)
    in_degree = defaultdict(int)
    
    # Initialize all components with 0 in-degree
    for comp in components:
        in_degree[comp['guid']] = 0
    
    # Build parameter -> component mapping
    param_to_component = {}
    for comp in components:
        for param in comp['params']:
            param_to_component[param['param_guid']] = comp['guid']
    
    # Build graph from wires
    for wire in wires:
        # After fix to isolate_rotatingslats.py, wire['from_component'] is now component GUID
        from_comp_guid = wire['from_component']
        to_comp_guid = wire['to_component']
        
        # Skip if we couldn't resolve the source (external input)
        if from_comp_guid is None:
            continue
        
        # Skip if same component (shouldn't happen)
        if from_comp_guid == to_comp_guid:
            continue
        
        # Skip if not a valid component
        if from_comp_guid not in in_degree or to_comp_guid not in in_degree:
            continue
        
        # Add edge: from_comp -> to_comp
        adjacency[from_comp_guid].append(to_comp_guid)
        in_degree[to_comp_guid] += 1
    
    # Kahn's algorithm for topological sort
    queue = deque()
    
    # Start with all nodes that have no dependencies
    for comp_guid, degree in in_degree.items():
        if degree == 0:
            queue.append(comp_guid)
    
    sorted_order = []
    
    while queue:
        current = queue.popleft()
        sorted_order.append(current)
        
        # Reduce in-degree for all neighbors
        for neighbor in adjacency[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # Check for cycles
    if len(sorted_order) != len(components):
        raise ValueError("Graph contains cycles - cannot evaluate")
    
    return sorted_order


# ============================================================================
# INPUT RESOLUTION
# ============================================================================

def resolve_input(param: dict, context: EvaluationContext, 
                  external_inputs: Dict[str, any]) -> DataTree:
    """
    Resolve input for a parameter.
    
    Priority:
    1. Wire connection (from upstream component)
    2. Persistent data (from GHX)
    3. External input (from sliders/panels)
    4. Default value
    
    Args:
        param: Parameter dict
        context: Evaluation context
        external_inputs: Dictionary of external input values
    
    Returns:
        DataTree containing the resolved input
    """
    param_guid = param['param_guid']
    param_name = param['name']
    
    # 1. Check for wire connections
    sources = param.get('sources', [])
    if sources:
        # Get data from first source (GH uses first wire if multiple)
        source_param_guid = sources[0]
        
        # First check if source is an external input (slider/panel outside group)
        if source_param_guid in external_inputs:
            data = external_inputs[source_param_guid]
            if isinstance(data, list):
                return DataTree.from_list(data)
            else:
                return DataTree.from_scalar(data)
        
        # Find which component owns this output parameter
        for comp_guid, comp in context.components.items():
            for out_param in comp['params']:
                if out_param['param_guid'] == source_param_guid:
                    # Found the source component
                    if context.is_evaluated(comp_guid):
                        # Get the output from this component
                        outputs = context.get_result(comp_guid)
                        # Match output parameter name
                        output_name = out_param['name']
                        if output_name in outputs:
                            return outputs[output_name]
                    break
    
    # 2. Check for persistent data in parameter
    persistent_data = param.get('persistent_data', [])
    if persistent_data:
        # Convert persistent data to DataTree
        if isinstance(persistent_data, list):
            return DataTree.from_list(persistent_data)
        else:
            return DataTree.from_scalar(persistent_data)
    
    # 3. Check external inputs
    if param_guid in external_inputs:
        data = external_inputs[param_guid]
        if isinstance(data, list):
            return DataTree.from_list(data)
        else:
            return DataTree.from_scalar(data)
    
    # 4. Default value based on parameter name
    defaults = {
        'X': 0,
        'Y': 0,
        'Z': 0,
        'A': 0,
        'B': 1,
        'Factor': 1,
        'Start': 0,
        'Step': 1,
        'Count': 10,
        'Index': 0,
        'Wrap': True,
        'Closed': False,
        'Length': 1,
        'Angle': 0,
    }
    
    default_value = defaults.get(param_name, 0)
    return DataTree.from_scalar(default_value)


# ============================================================================
# COMPONENT EVALUATION
# ============================================================================

def evaluate_component_wired(comp_guid: str, context: EvaluationContext,
                             external_inputs: Dict[str, any]) -> Dict[str, DataTree]:
    """
    Evaluate a single component with wire resolution.
    
    Args:
        comp_guid: Component GUID
        context: Evaluation context
        external_inputs: External input data
    
    Returns:
        Dictionary mapping output parameter names to DataTrees
    """
    # Check cache
    if context.is_evaluated(comp_guid):
        return context.get_result(comp_guid)
    
    # Get component
    comp = context.get_component(comp_guid)
    if not comp:
        raise ValueError(f"Component {comp_guid} not found")
    
    type_name = comp['type_name']
    
    # Check if component type is registered
    if not COMPONENT_REGISTRY.is_registered(type_name):
        print(f"WARNING: Component type '{type_name}' not implemented, skipping")
        # Return empty outputs
        outputs = {}
        for param in comp['params']:
            if param['type'] == 'output':
                outputs[param['name']] = DataTree()
        context.set_result(comp_guid, outputs)
        return outputs
    
    # Resolve all input parameters
    inputs = {}
    for param in comp['params']:
        if param['type'] == 'input':
            param_name = param['name']
            resolved_data = resolve_input(param, context, external_inputs)
            inputs[param_name] = resolved_data
    
    # Evaluate component
    outputs = COMPONENT_REGISTRY.evaluate(type_name, inputs)
    
    # Cache result
    context.set_result(comp_guid, outputs)
    
    return outputs


# ============================================================================
# GRAPH EVALUATION
# ============================================================================

def evaluate_graph(components: List[dict], wires: List[dict],
                   external_inputs: Dict[str, any]) -> Dict[str, Dict[str, DataTree]]:
    """
    Evaluate entire component graph.
    
    Args:
        components: List of component dicts
        wires: List of wire dicts
        external_inputs: External input data (from sliders, panels, etc.)
    
    Returns:
        Dictionary mapping component GUID to its outputs
    """
    # Perform topological sort
    print("Performing topological sort...")
    try:
        eval_order = topological_sort(components, wires)
        print(f"  Evaluation order: {len(eval_order)} components")
    except ValueError as e:
        print(f"ERROR: {e}")
        return {}
    
    # Create evaluation context
    context = EvaluationContext(components, wires)
    
    # Evaluate components in order
    print()
    print("Evaluating components...")
    
    results = {}
    
    for i, comp_guid in enumerate(eval_order):
        comp = context.get_component(comp_guid)
        type_name = comp['type_name']
        nickname = comp['nickname']
        
        print(f"  [{i+1}/{len(eval_order)}] {type_name}: {nickname}")
        
        try:
            outputs = evaluate_component_wired(comp_guid, context, external_inputs)
            results[comp_guid] = outputs
            
            # Print output summary
            for output_name, output_tree in outputs.items():
                branch_count = output_tree.branch_count()
                item_count = output_tree.item_count()
                print(f"      {output_name}: {branch_count} branches, {item_count} items")
                
        except Exception as e:
            print(f"      ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    return results


# ============================================================================
# MAIN EVALUATION FUNCTION
# ============================================================================

def evaluate_rotatingslats():
    """
    Main function to evaluate Rotatingslats group.
    """
    print("=" * 80)
    print("PHASE 5: Wired Topological Evaluation")
    print("=" * 80)
    print()
    
    # Load Rotatingslats graph
    print("Loading Rotatingslats graph...")
    with open('rotatingslats_graph.json', 'r') as f:
        graph = json.load(f)
    
    components = graph['components']
    internal_wires = graph['internal_wires']
    external_wires = graph['external_wires']
    
    print(f"  Components: {len(components)}")
    print(f"  Internal wires: {len(internal_wires)}")
    print(f"  External wires: {len(external_wires)}")
    print()
    
    # Load external inputs
    print("Loading external inputs...")
    with open('rotatingslats_inputs.json', 'r') as f:
        external_inputs_raw = json.load(f)
    
    # Convert external inputs to simple dict
    # Map both component GUID and output parameter GUIDs to data
    external_inputs = {}
    for guid, input_data in external_inputs_raw.items():
        if input_data['data']:
            # For sliders/panels, the GUID itself is both component AND parameter GUID
            # Map the GUID (which is the slider's output parameter GUID)
            external_inputs[input_data['guid']] = input_data['data']
            
            # Also map the key GUID if different (for compatibility)
            if guid != input_data['guid']:
                external_inputs[guid] = input_data['data']
            
            # If there are params (for complex components), map those too
            for param in input_data.get('params', []):
                if param.get('type') == 'output':
                    param_guid = param.get('param_guid')
                    if param_guid:
                        external_inputs[param_guid] = input_data['data']
    
    print(f"  External inputs: {len(external_inputs)}")
    print()
    
    # Print external input values
    print("External input values:")
    for guid, input_data in external_inputs_raw.items():
        nickname = input_data['nickname']
        data = input_data['data']
        if data:
            print(f"  {nickname}: {data}")
    print()
    
    # Combine internal and external wires
    all_wires = internal_wires + external_wires
    
    # Evaluate graph
    results = evaluate_graph(components, all_wires, external_inputs)
    
    print()
    print("=" * 80)
    print("PHASE 5 COMPLETE")
    print("=" * 80)
    print()
    print(f"Evaluated {len(results)} components successfully")
    
    # Save results
    print()
    print("Saving evaluation results...")
    
    # Convert results to JSON-serializable format with component metadata
    # Create component lookup dict
    components_dict = {c['guid']: c for c in components}
    
    results_json = {}
    for comp_guid, outputs in results.items():
        # Find component info
        comp = components_dict.get(comp_guid, {})
        
        # Create enhanced structure with component metadata
        results_json[comp_guid] = {
            'component_info': {
                'guid': comp_guid,
                'type': comp.get('type_name', 'Unknown'),
                'nickname': comp.get('nickname', 'Unknown'),
                'position': comp.get('position', {'x': 0, 'y': 0})
            },
            'outputs': {}
        }
        
        # Add output data
        for output_name, output_tree in outputs.items():
            results_json[comp_guid]['outputs'][output_name] = {
                'branches': {str(path): items for path, items in output_tree.data.items()},
                'branch_count': output_tree.branch_count(),
                'item_count': output_tree.item_count()
            }
    
    with open('rotatingslats_evaluation_results.json', 'w') as f:
        json.dump(results_json, f, indent=2)
    
    print("[OK] Saved rotatingslats_evaluation_results.json")
    print()
    print("Ready for PHASE 6: Result verification")


if __name__ == '__main__':
    evaluate_rotatingslats()

