"""
PHASE 5: Extended Wired Topological Evaluation
Evaluate both Sun and Rotatingslats groups in sequence.
"""

import json
from gh_evaluator_wired import evaluate_graph, resolve_input, EvaluationContext
from gh_evaluator_core import DataTree, COMPONENT_REGISTRY
from gh_components_rotatingslats import *  # Register all components


def evaluate_both_groups():
    """
    Main function to evaluate both Sun and Rotatingslats groups.
    """
    print("=" * 80)
    print("PHASE 5: SUN AND ROTATINGSLATS GROUP EVALUATION")
    print("=" * 80)
    print()
    
    # ========================================================================
    # STEP 1: Evaluate Sun Group
    # ========================================================================
    print("STEP 1: Evaluating Sun group...")
    print()
    
    # Load Sun group graph
    with open('sun_group_graph.json', 'r') as f:
        sun_graph = json.load(f)
    
    sun_components = sun_graph['components']
    sun_internal_wires = sun_graph['internal_wires']
    sun_external_wires = sun_graph['external_wires']
    
    print(f"  Components: {len(sun_components)}")
    print(f"  Internal wires: {len(sun_internal_wires)}")
    print(f"  External wires: {len(sun_external_wires)}")
    print()
    
    # Load Sun group external inputs
    with open('sun_group_inputs.json', 'r') as f:
        sun_inputs_raw = json.load(f)
    
    # Convert Sun external inputs
    sun_external_inputs = {}
    for guid, input_data in sun_inputs_raw.items():
        if input_data['data']:
            sun_external_inputs[input_data['guid']] = input_data['data']
            if guid != input_data['guid']:
                sun_external_inputs[guid] = input_data['data']
            for param in input_data.get('params', []):
                if param.get('type') == 'output':
                    param_guid = param.get('param_guid')
                    if param_guid:
                        sun_external_inputs[param_guid] = input_data['data']
    
    print(f"  External inputs: {len(sun_external_inputs)}")
    print("  External input values:")
    for guid, input_data in sun_inputs_raw.items():
        nickname = input_data['nickname']
        data = input_data['data']
        if data:
            print(f"    {nickname}: {data}")
    print()
    
    # Evaluate Sun group
    sun_all_wires = sun_internal_wires + sun_external_wires
    sun_results = evaluate_graph(sun_components, sun_all_wires, sun_external_inputs)
    
    print(f"  Sun group evaluated: {len(sun_results)} components")
    print()
    
    # ========================================================================
    # STEP 2: Prepare Sun group outputs for Rotatingslats group
    # ========================================================================
    print("STEP 2: Preparing Sun group outputs for Rotatingslats group...")
    print()
    
    # Load cross-group wires
    with open('cross_group_wires.json', 'r') as f:
        cross_group_info = json.load(f)
    
    cross_group_wires = cross_group_info['wires']
    print(f"  Cross-group wires: {len(cross_group_wires)}")
    
    # Build mapping of Sun group outputs to parameter GUIDs
    sun_outputs_by_param = {}
    sun_components_dict = {c['guid']: c for c in sun_components}
    
    for comp_guid, outputs in sun_results.items():
        comp = sun_components_dict.get(comp_guid, {})
        for param in comp.get('params', []):
            if param['type'] == 'output':
                param_guid = param['param_guid']
                output_name = param['name']
                if output_name in outputs:
                    sun_outputs_by_param[param_guid] = outputs[output_name]
                    # Also map component GUID for compatibility
                    sun_outputs_by_param[comp_guid] = outputs[output_name]
    
    print(f"  Sun group outputs mapped: {len(sun_outputs_by_param)} parameter GUIDs")
    print()
    
    # ========================================================================
    # STEP 3: Evaluate Rotatingslats Group
    # ========================================================================
    print("STEP 3: Evaluating Rotatingslats group...")
    print()
    
    # Load Rotatingslats group graph
    with open('rotatingslats_graph.json', 'r') as f:
        rotatingslats_graph = json.load(f)
    
    rotatingslats_components = rotatingslats_graph['components']
    rotatingslats_internal_wires = rotatingslats_graph['internal_wires']
    rotatingslats_external_wires = rotatingslats_graph['external_wires']
    
    print(f"  Components: {len(rotatingslats_components)}")
    print(f"  Internal wires: {len(rotatingslats_internal_wires)}")
    print(f"  External wires: {len(rotatingslats_external_wires)}")
    print()
    
    # Load Rotatingslats external inputs
    with open('rotatingslats_inputs.json', 'r') as f:
        rotatingslats_inputs_raw = json.load(f)
    
    # Convert Rotatingslats external inputs
    rotatingslats_external_inputs = {}
    for guid, input_data in rotatingslats_inputs_raw.items():
        if input_data['data']:
            rotatingslats_external_inputs[input_data['guid']] = input_data['data']
            if guid != input_data['guid']:
                rotatingslats_external_inputs[guid] = input_data['data']
            for param in input_data.get('params', []):
                if param.get('type') == 'output':
                    param_guid = param.get('param_guid')
                    if param_guid:
                        rotatingslats_external_inputs[param_guid] = input_data['data']
    
    # Add Sun group outputs to Rotatingslats external inputs
    # Map by parameter GUID for cross-group wires, passing full DataTree
    for wire in cross_group_wires:
        from_param_guid = wire['from_param']
        to_param_guid = wire['to_param']
        
        if from_param_guid in sun_outputs_by_param:
            tree = sun_outputs_by_param[from_param_guid]
            # Map both source and target parameter GUIDs to the full DataTree
            rotatingslats_external_inputs[from_param_guid] = tree
            rotatingslats_external_inputs[to_param_guid] = tree
    
    print(f"  External inputs: {len(rotatingslats_external_inputs)}")
    print(f"  (Including {len(sun_outputs_by_param)} from Sun group)")
    print()
    
    # Combine internal and external wires (including cross-group wires)
    rotatingslats_all_wires = rotatingslats_internal_wires + rotatingslats_external_wires + cross_group_wires
    
    # Evaluate Rotatingslats group
    rotatingslats_results = evaluate_graph(rotatingslats_components, rotatingslats_all_wires, rotatingslats_external_inputs)
    
    print(f"  Rotatingslats group evaluated: {len(rotatingslats_results)} components")
    print()
    
    # ========================================================================
    # STEP 4: Save Results
    # ========================================================================
    print("STEP 4: Saving results...")
    print()
    
    # Save Sun group results
    sun_components_dict = {c['guid']: c for c in sun_components}
    sun_results_json = {}
    for comp_guid, outputs in sun_results.items():
        comp = sun_components_dict.get(comp_guid, {})
        sun_results_json[comp_guid] = {
            'component_info': {
                'guid': comp_guid,
                'type': comp.get('type_name', 'Unknown'),
                'nickname': comp.get('nickname', 'Unknown'),
                'position': comp.get('position', {'x': 0, 'y': 0})
            },
            'outputs': {}
        }
        for output_name, output_tree in outputs.items():
            sun_results_json[comp_guid]['outputs'][output_name] = {
                'branches': {str(path): items for path, items in output_tree.data.items()},
                'branch_count': output_tree.branch_count(),
                'item_count': output_tree.item_count()
            }
    
    with open('sun_group_evaluation_results.json', 'w') as f:
        json.dump(sun_results_json, f, indent=2)
    print("[OK] Saved sun_group_evaluation_results.json")
    
    # Save Rotatingslats group results
    rotatingslats_components_dict = {c['guid']: c for c in rotatingslats_components}
    rotatingslats_results_json = {}
    for comp_guid, outputs in rotatingslats_results.items():
        comp = rotatingslats_components_dict.get(comp_guid, {})
        rotatingslats_results_json[comp_guid] = {
            'component_info': {
                'guid': comp_guid,
                'type': comp.get('type_name', 'Unknown'),
                'nickname': comp.get('nickname', 'Unknown'),
                'position': comp.get('position', {'x': 0, 'y': 0})
            },
            'outputs': {}
        }
        for output_name, output_tree in outputs.items():
            rotatingslats_results_json[comp_guid]['outputs'][output_name] = {
                'branches': {str(path): items for path, items in output_tree.data.items()},
                'branch_count': output_tree.branch_count(),
                'item_count': output_tree.item_count()
            }
    
    with open('rotatingslats_evaluation_results.json', 'w') as f:
        json.dump(rotatingslats_results_json, f, indent=2)
    print("[OK] Saved rotatingslats_evaluation_results.json")
    
    print()
    print("=" * 80)
    print("PHASE 5 COMPLETE")
    print("=" * 80)
    print()
    print(f"Sun group: {len(sun_results)} components evaluated")
    print(f"Rotatingslats group: {len(rotatingslats_results)} components evaluated")
    print()
    print("Ready for PHASE 6: Result verification")


if __name__ == '__main__':
    evaluate_both_groups()

