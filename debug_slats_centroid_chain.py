"""
Debug script to trace the full Slats Centroid chain:
Polar Array → List Item → Move "Slats original" → Area → Centroid (10 values)
"""

import json

# Component GUIDs
POLAR_ARRAY_GUID = '7ad636cc-e506-4f77-bb82-4a86ba2a3fea'
LIST_ITEM_GUID = '27933633-dbab-4dc0-a4a2-cfa309c03c45'
MOVE_SLATS_ORIGINAL_GUID = '0532cbdf-875b-4db9-8c88-352e21051436'
AREA_GUID = '3bd2c1d3-149d-49fb-952c-8db272035f9e'
CENTROID_OUTPUT_GUID = '01fd4f89-2b73-4e61-a51f-9c3df0c876fa'

# Output parameter GUIDs
POLAR_ARRAY_OUTPUT = '1a00d7ad-1003-4dfa-a933-6a7a60dfb0b1'
LIST_ITEM_OUTPUT = 'a72418c4-eb29-4226-9dea-f076720da34f'
MOVE_GEOMETRY_OUTPUT = '4218a4e5-b5a7-477b-b7e2-dfc59ff7b896'

def load_data():
    """Load component graph and data"""
    with open('complete_component_graph.json', 'r') as f:
        graph = json.load(f)
    return graph

def trace_chain():
    """Trace the complete chain"""
    graph = load_data()
    
    print("=" * 80)
    print("TRACING SLATS CENTROID CHAIN (10 values)")
    print("=" * 80)
    print()
    
    # 1. Polar Array
    print("1. POLAR ARRAY")
    print("-" * 80)
    polar_comp = graph.get(POLAR_ARRAY_GUID, {})
    polar_obj = polar_comp.get('obj', {})
    print(f"   Component GUID: {POLAR_ARRAY_GUID}")
    print(f"   Type: {polar_obj.get('type')}")
    polar_params = polar_obj.get('params', {})
    print(f"   Count: 10 (from GHX)")
    print(f"   Angle: 2*pi (6.283185307179586)")
    print(f"   Output Geometry: {POLAR_ARRAY_OUTPUT[:8]}...")
    print(f"   Expected: List of 10 geometries")
    print()
    
    # 2. List Item
    print("2. LIST ITEM")
    print("-" * 80)
    list_comp = graph.get(LIST_ITEM_GUID, {})
    list_obj = list_comp.get('obj', {})
    print(f"   Component GUID: {LIST_ITEM_GUID}")
    print(f"   Type: {list_obj.get('type')}")
    list_params = list_obj.get('params', {}).get('ParameterData', {})
    if isinstance(list_params, dict):
        input_params = list_params.get('InputParam', {})
        if isinstance(input_params, dict):
            for idx in sorted([k for k in input_params.keys() if k.isdigit()]):
                param = input_params[idx]
                param_data = param.get('data', {})
                sources = param.get('sources', [])
                persistent = param.get('persistent_values', [])
                print(f"     {param_data.get('Name')}:")
                if sources:
                    for src in sources:
                        print(f"       -> Source: {src.get('guid', '')[:8]}...")
                if persistent:
                    print(f"       -> Persistent: {persistent}")
    print(f"   Output: {LIST_ITEM_OUTPUT[:8]}...")
    print(f"   Index: 0, Wrap: true")
    print()
    
    # 3. Move "Slats original"
    print("3. MOVE (Slats original)")
    print("-" * 80)
    move_comp = graph.get(MOVE_SLATS_ORIGINAL_GUID, {})
    move_obj = move_comp.get('obj', {})
    print(f"   Component GUID: {MOVE_SLATS_ORIGINAL_GUID}")
    print(f"   Type: {move_obj.get('type')}")
    print(f"   NickName: {move_obj.get('nickname')}")
    move_params = move_obj.get('params', {})
    print(f"   Inputs:")
    for key in sorted(move_params.keys()):
        if key.startswith('param_input'):
            param = move_params[key]
            param_data = param.get('data', {})
            sources = param.get('sources', [])
            persistent = param.get('persistent_values', [])
            print(f"     {param_data.get('Name')}:")
            if sources:
                for src in sources:
                    print(f"       -> Source: {src.get('guid', '')[:8]}...")
            if persistent:
                print(f"       -> Persistent: {persistent}")
    print(f"   Output Geometry: {MOVE_GEOMETRY_OUTPUT[:8]}...")
    print()
    
    # 4. Area
    print("4. AREA")
    print("-" * 80)
    area_comp = graph.get(AREA_GUID, {})
    area_obj = area_comp.get('obj', {})
    print(f"   Component GUID: {AREA_GUID}")
    print(f"   Type: {area_obj.get('type')}")
    area_params = area_obj.get('params', {}).get('ParameterData', {})
    if isinstance(area_params, dict):
        input_params = area_params.get('InputParam', {})
        if isinstance(input_params, dict):
            for idx in sorted([k for k in input_params.keys() if k.isdigit()]):
                param = input_params[idx]
                param_data = param.get('data', {})
                sources = param.get('sources', [])
                print(f"     {param_data.get('Name')}:")
                if sources:
                    for src in sources:
                        print(f"       -> Source: {src.get('guid', '')[:8]}...")
    print(f"   Output Centroid: {CENTROID_OUTPUT_GUID[:8]}...")
    print()
    
    print("=" * 80)
    print("CHAIN SUMMARY")
    print("=" * 80)
    print("Polar Array (10 geometries) -> List Item (Index=0) -> Move (Slats original) -> Area -> Centroid")
    print()
    print("Expected Centroid values (10):")
    print("  {11.32743, -27.416834, 3.8}")
    print("  {11.32743, -27.416834, 3.722222}")
    print("  {11.32743, -27.416834, 3.644444}")
    print("  ...")
    print("  {11.32743, -27.416834, 3.1}")
    print()
    print("Key observation: All have same X, Y but different Z values")
    print("Z values decrease by ~0.077777 each (3.8 -> 3.1 in 9 steps)")
    print()

if __name__ == '__main__':
    trace_chain()

