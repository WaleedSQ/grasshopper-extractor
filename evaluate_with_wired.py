"""
PHASE 5: Wired Evaluation using gh_evaluator_wired.py
Evaluates the Rotatingslats group with proper ReverseData support.
"""
import json
import sys
from gh_evaluator_wired import evaluate_graph_wired

def main():
    print("="*80)
    print("PHASE 5: WIRED EVALUATION (with ReverseData support)")
    print("="*80)
    
    # Load the rotatingslats graph
    with open('rotatingslats_graph.json') as f:
        graph_data = json.load(f)
    
    components = graph_data['components']
    
    # Load external inputs
    with open('rotatingslats_inputs.json') as f:
        inputs_data = json.load(f)
    
    external_inputs = {}
    for slider_guid, slider_info in inputs_data.items():
        external_inputs[slider_guid] = slider_info['value']
    
    print(f"\nLoaded {len(components)} components")
    print(f"Loaded {len(external_inputs)} external inputs")
    
    # Evaluate the graph
    print("\nEvaluating...")
    try:
        results = evaluate_graph_wired(components, external_inputs)
        
        # Save results
        with open('rotatingslats_evaluation_results.json', 'w') as f:
            # Convert DataTree objects to serializable dicts
            serializable_results = {}
            for comp_guid, outputs in results.items():
                serializable_results[comp_guid] = {
                    'outputs': {
                        name: tree.to_dict() for name, tree in outputs.items()
                    }
                }
                # Add component info
                comp = next((c for c in components if c['guid'] == comp_guid), None)
                if comp:
                    serializable_results[comp_guid]['component_info'] = {
                        'type': comp['type_name'],
                        'nickname': comp['nickname'],
                        'guid': comp['guid'],
                        'position': comp['position']
                    }
            json.dump(serializable_results, f, indent=2)
        
        print("\n" + "="*80)
        print("EVALUATION COMPLETE")
        print("="*80)
        print(f"Evaluated {len(results)} components successfully")
        print(f"Results saved to: rotatingslats_evaluation_results.json")
        
        # Show a sample of key results
        print("\n" + "="*80)
        print("KEY RESULTS:")
        print("="*80)
        
        key_components = [
            ('d0dd0a5d-a421-4533-bbfc-c02fa08c5da5', 'Angle'),
            ('ebcd02a2-ac68-43a5-b02e-701fa8770206', 'Degrees'),
            ('326da981-351e-4794-9d60-77e8e87bd778', 'Plane Normal (1)'),
            ('011398ea-ce1d-412a-afeb-fe91e8fac96c', 'Plane Normal (2)'),
            ('910c335c-b5e8-41bf-bfb4-576cb17432c7', 'PolyLine (with ReverseData)'),
        ]
        
        for guid, label in key_components:
            if guid in results:
                print(f"\n{label}:")
                outputs = results[guid]
                for output_name, tree in outputs.items():
                    print(f"  {output_name}: {tree.branch_count()} branches")
                    if tree.branch_count() > 0:
                        first_branch = tree.get_branch(tree.get_paths()[0])
                        if first_branch:
                            print(f"    First item: {first_branch[0]}")
        
    except Exception as e:
        print(f"\nERROR during evaluation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

