"""
Debug script to trace the Area → Centroid chain for "Box to project":
Box 2Pt → Move ("Box to project") → Area → Centroid
"""

import json
import sys

# Component GUIDs
BOX_2PT_GUID = 'b908d823-e613-4684-9e94-65a0f60f19b7'
MOVE_BOX_PROJECT_GUID = 'dfbbd4a2-021a-4c74-ac63-8939e6ac5429'
AREA_GUID = '77f7eddb-d54b-4280-aad9-4c4a8400a56b'
CENTROID_OUTPUT_GUID = '34529a8c-3dfd-4d96-865b-9e4cbfddad6c'

def load_data():
    """Load component graph and data"""
    with open('complete_component_graph.json', 'r') as f:
        graph = json.load(f)
    with open('rotatingslats_data.json', 'r') as f:
        data = json.load(f)
    with open('external_inputs.json', 'r') as f:
        external = json.load(f)
    return graph, data, external

def trace_chain():
    """Trace the complete chain"""
    graph, data, external = load_data()
    
    print("=" * 80)
    print("TRACING AREA -> CENTROID CHAIN (Box to project)")
    print("=" * 80)
    print()
    
    # 1. Box 2Pt
    print("1. BOX 2PT")
    print("-" * 80)
    box_comp = graph.get(BOX_2PT_GUID, {})
    box_obj = box_comp.get('obj', {})
    print(f"   Component GUID: {BOX_2PT_GUID}")
    print(f"   Type: {box_obj.get('type')}")
    print()
    
    # 2. Move (Box to project)
    print("2. MOVE (Box to project)")
    print("-" * 80)
    move_comp = graph.get(MOVE_BOX_PROJECT_GUID, {})
    move_obj = move_comp.get('obj', {})
    print(f"   Component GUID: {MOVE_BOX_PROJECT_GUID}")
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
    print(f"   Output Geometry: 3d373d1a...")
    print()
    
    # 3. Area
    print("3. AREA")
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
    print("Box 2Pt -> Move (Box to project) -> Area -> Centroid")
    print()
    print("Expected Centroid: {11.32743, -27.846834, 2.0}")
    print()

if __name__ == '__main__':
    trace_chain()

