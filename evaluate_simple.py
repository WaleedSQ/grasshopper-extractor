"""
Simple Evaluation: Evaluate all components together without group complexity
- Load inputs.json, components.json, wires.json
- Evaluate all components in one pass
- Save results
"""

import json
from gh_evaluator_wired import evaluate_graph
from gh_components_rotatingslats import *  # Register all components


def evaluate_simple():
    """Evaluate all components together without group complexity."""
    
    print("=" * 80)
    print("SIMPLE EVALUATION: Evaluate all components")
    print("=" * 80)
    print()
    
    # ========================================================================
    # STEP 1: Load data
    # ========================================================================
    print("STEP 1: Loading data...")
    print()
    
    with open('inputs.json', 'r') as f:
        inputs_raw = json.load(f)
    
    with open('components.json', 'r') as f:
        components = json.load(f)
    
    with open('wires.json', 'r') as f:
        wires = json.load(f)
    
    print(f"  Inputs: {len(inputs_raw)}")
    print(f"  Components: {len(components)}")
    print(f"  Wires: {len(wires)}")
    print()
    
    # ========================================================================
    # STEP 2: Convert inputs to external_inputs format
    # ========================================================================
    print("STEP 2: Preparing external inputs...")
    print()
    
    from gh_evaluator_core import DataTree
    
    external_inputs = {}
    for guid, input_data in inputs_raw.items():
        if input_data.get('data'):
            data = input_data['data']
            # Convert to DataTree
            if isinstance(data, list):
                tree = DataTree.from_list(data)
            else:
                tree = DataTree.from_scalar(data)
            
            # Map by component GUID (which is also the parameter GUID for sliders)
            external_inputs[guid] = tree
            
            # Also map parameter GUID if available
            # For sliders, the GUID itself is the output parameter GUID
            external_inputs[guid] = tree
    
    print(f"  External inputs prepared: {len(external_inputs)}")
    print("  Input values:")
    for guid, input_data in inputs_raw.items():
        nickname = input_data.get('nickname', 'Unknown')
        data = input_data.get('data')
        if data:
            print(f"    {nickname}: {data}")
    print()
    
    # ========================================================================
    # STEP 3: Evaluate all components
    # ========================================================================
    print("STEP 3: Evaluating components...")
    print()
    
    results = evaluate_graph(components, wires, external_inputs)
    
    print(f"  Components evaluated: {len(results)}")
    print()
    
    # ========================================================================
    # STEP 4: Save results
    # ========================================================================
    print("STEP 4: Saving results...")
    print()
    
    components_dict = {c['guid']: c for c in components}
    results_json = {}
    
    for comp_guid, outputs in results.items():
        comp = components_dict.get(comp_guid, {})
        results_json[comp_guid] = {
            'component_info': {
                'guid': comp_guid,
                'type': comp.get('type_name', 'Unknown'),
                'nickname': comp.get('nickname', 'Unknown'),
                'position': comp.get('position', {'x': 0, 'y': 0})
            },
            'outputs': {}
        }
        for output_name, output_tree in outputs.items():
            results_json[comp_guid]['outputs'][output_name] = {
                'branches': {str(path): items for path, items in output_tree.data.items()},
                'branch_count': output_tree.branch_count(),
                'item_count': output_tree.item_count()
            }
    
    with open('evaluation_results.json', 'w') as f:
        json.dump(results_json, f, indent=2)
    print("[OK] Saved evaluation_results.json")
    
    print()
    print("=" * 80)
    print("SIMPLE EVALUATION COMPLETE")
    print("=" * 80)
    print()
    print(f"Evaluated {len(results)} components successfully")
    print()
    
    # Summary by component type
    type_counts = {}
    for comp_guid, outputs in results.items():
        comp = components_dict.get(comp_guid, {})
        comp_type = comp.get('type_name', 'Unknown')
        type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
    
    print("Evaluated component types:")
    for comp_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {comp_type}: {count}")


if __name__ == '__main__':
    evaluate_simple()

