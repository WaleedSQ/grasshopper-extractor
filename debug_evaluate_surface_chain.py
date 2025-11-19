"""
Debug script to trace the Evaluate Surface → Normal chain:
Box 2Pt → Move (Box to project) → Polar Array → List Item → Evaluate Surface
"""

import json
import sys
from typing import Dict, Any, List

# Component GUIDs in the chain
BOX_2PT_GUID = 'b908d823-e613-4684-9e94-65a0f60f19b7'
MOVE_BOX_PROJECT_GUID = 'dfbbd4a2-021a-4c74-ac63-8939e6ac5429'
POLAR_ARRAY_GUID = 'd8f9c0ae-abe6-4e06-8893-d196ac301553'
LIST_ITEM_GUID = 'e5850abb-fae2-4960-b531-bbf73f5e3c45'
EVALUATE_SURFACE_GUID = 'd8de94de-c80f-4737-8059-5d259b78807c'
MD_SLIDER_GUID = 'c4c92669-f802-4b5f-b3fb-61b8a642dc0a'

# Output parameter GUIDs
BOX_OUTPUT_GUID = 'f12438b5-04ca-4ed7-b015-3f5310d7b57f'
MOVE_GEOMETRY_OUTPUT_GUID = '3d373d1a-a5f6-44ec-9541-37ccd8b80fe4'
POLAR_ARRAY_GEOMETRY_OUTPUT_GUID = '00d89d35-33ec-4118-8aa1-9b23334eeb99'
LIST_ITEM_OUTPUT_GUID = '7de8f856-38c3-494a-9b72-fdb4184a1b70'
EVALUATE_SURFACE_NORMAL_OUTPUT_GUID = 'e41d5eba-b018-45b1-8c10-1eff741f7a85'

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
    print("TRACING EVALUATE SURFACE -> NORMAL CHAIN")
    print("=" * 80)
    print()
    
    # 1. Box 2Pt
    print("1. BOX 2PT")
    print("-" * 80)
    box_comp = graph.get(BOX_2PT_GUID, {})
    box_obj = box_comp.get('obj', {})
    print(f"   Component GUID: {BOX_2PT_GUID}")
    print(f"   Type: {box_obj.get('type')}")
    print(f"   Inputs:")
    params = box_obj.get('params', {})
    for key in sorted(params.keys()):
        if key.startswith('param_input'):
            param = params[key]
            param_data = param.get('data', {})
            sources = param.get('sources', [])
            print(f"     {param_data.get('Name')}: {len(sources)} source(s)")
            for src in sources:
                print(f"       -> {src.get('guid', '')[:8]}...")
    print(f"   Output: {BOX_OUTPUT_GUID[:8]}...")
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
                    print(f"       → Source: {src.get('guid', '')[:8]}...")
            if persistent:
                print(f"       → Persistent: {persistent}")
    print(f"   Output Geometry: {MOVE_GEOMETRY_OUTPUT_GUID[:8]}...")
    print()
    
    # 3. Polar Array
    print("3. POLAR ARRAY")
    print("-" * 80)
    polar_comp = graph.get(POLAR_ARRAY_GUID, {})
    polar_obj = polar_comp.get('obj', {})
    print(f"   Component GUID: {POLAR_ARRAY_GUID}")
    print(f"   Type: {polar_obj.get('type')}")
    polar_params = polar_obj.get('params', {})
    print(f"   Inputs:")
    for key in sorted(polar_params.keys()):
        if key.startswith('param_input'):
            param = polar_params[key]
            param_data = param.get('data', {})
            sources = param.get('sources', [])
            persistent = param.get('persistent_values', [])
            print(f"     {param_data.get('Name')}:")
            if sources:
                for src in sources:
                    print(f"       → Source: {src.get('guid', '')[:8]}...")
            if persistent:
                print(f"       → Persistent: {persistent}")
    print(f"   Output Geometry: {POLAR_ARRAY_GEOMETRY_OUTPUT_GUID[:8]}...")
    print()
    
    # 4. List Item
    print("4. LIST ITEM")
    print("-" * 80)
    list_comp = graph.get(LIST_ITEM_GUID, {})
    list_obj = list_comp.get('obj', {})
    print(f"   Component GUID: {LIST_ITEM_GUID}")
    print(f"   Type: {list_obj.get('type')}")
    list_params = list_obj.get('params', {}).get('ParameterData', {}).get('InputParam', {})
    if isinstance(list_params, dict):
        print(f"   Inputs:")
        for idx in sorted([k for k in list_params.keys() if k.isdigit()]):
            param = list_params[idx]
            param_data = param.get('data', {})
            sources = param.get('sources', [])
            persistent = param.get('persistent_values', [])
            print(f"     {param_data.get('Name')}:")
            if sources:
                for src in sources:
                    print(f"       → Source: {src.get('guid', '')[:8]}...")
            if persistent:
                print(f"       → Persistent: {persistent}")
    print(f"   Output: {LIST_ITEM_OUTPUT_GUID[:8]}...")
    print()
    
    # 5. Evaluate Surface
    print("5. EVALUATE SURFACE")
    print("-" * 80)
    eval_comp = graph.get(EVALUATE_SURFACE_GUID, {})
    eval_obj = eval_comp.get('obj', {})
    print(f"   Component GUID: {EVALUATE_SURFACE_GUID}")
    print(f"   Type: {eval_obj.get('type')}")
    eval_params = eval_obj.get('params', {})
    print(f"   Inputs:")
    for key in sorted(eval_params.keys()):
        if key.startswith('param_input'):
            param = eval_params[key]
            param_data = param.get('data', {})
            sources = param.get('sources', [])
            print(f"     {param_data.get('Name')}:")
            for src in sources:
                print(f"       → Source: {src.get('guid', '')[:8]}...")
    print(f"   Output Normal: {EVALUATE_SURFACE_NORMAL_OUTPUT_GUID[:8]}...")
    print()
    
    # 6. MD Slider
    print("6. MD SLIDER (UV coordinates)")
    print("-" * 80)
    md_comp = graph.get(MD_SLIDER_GUID, {})
    md_obj = md_comp.get('obj', {})
    print(f"   Component GUID: {MD_SLIDER_GUID}")
    print(f"   Type: {md_obj.get('type')}")
    if MD_SLIDER_GUID in external:
        ext_val = external[MD_SLIDER_GUID]
        print(f"   External Value: {ext_val}")
    print()
    
    print("=" * 80)
    print("CHAIN SUMMARY")
    print("=" * 80)
    print("Box 2Pt -> Move (Box to project) -> Polar Array -> List Item -> Evaluate Surface")
    print("MD Slider -> Evaluate Surface (Point input)")
    print()
    print("Expected Normal: {-1, 0, 0}")
    print()

if __name__ == '__main__':
    trace_chain()

