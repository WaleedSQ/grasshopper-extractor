#!/usr/bin/env python3
"""Trace the centroid Y mismatch - find where -0.07 difference occurs."""

import json
import sys
from evaluate_rotatingslats import load_component_graph, resolve_input_value, evaluate_component, get_external_inputs

# Load graph
graph_data = load_component_graph('complete_component_graph.json')
# Handle different graph structures
if isinstance(graph_data, dict) and 'components' in graph_data:
    graph = graph_data['components']
else:
    graph = graph_data

all_objects = {}
for comp_id, comp_data in graph.items():
    if isinstance(comp_data, dict) and 'obj' in comp_data:
        all_objects[comp_id] = comp_data['obj']

# Build output_params
output_params = {}
for comp_id, comp_data in graph.items():
    if isinstance(comp_data, dict) and 'obj' in comp_data:
        obj = comp_data['obj']
        params = obj.get('params', {})
        for param_key, param_info in params.items():
            if param_key.startswith('param_output'):
                param_guid = param_info.get('data', {}).get('InstanceGuid')
                if param_guid:
                    output_params[param_guid] = {
                        'obj': obj,
                        'param_key': param_key,
                        'param_info': param_info
                    }

evaluated = {}

print("=" * 80)
print("TRACING CENTROID Y MISMATCH")
print("=" * 80)
print(f"Expected centroid Y: -27.416834")
print(f"Actual centroid Y: -27.486834")
print(f"Difference: -0.07 (matches Vector 2Pt Y component)")
print()

# 1. Check geometry input to second Move (should have Y=0.0)
print("1. GEOMETRY INPUT TO SECOND MOVE (0532cbdf):")
print("-" * 80)
second_move_guid = None
for comp_id, comp_data in graph.items():
    if isinstance(comp_data, dict):
        obj = comp_data.get('obj', {})
        if obj.get('instance_guid') == '0532cbdf-875b-4db9-8c88-352e21051436':
            second_move_guid = comp_id
            break

if second_move_guid:
    print(f"   Found second Move component: {second_move_guid[:8]}...")
    comp_info = graph[second_move_guid]
    try:
        # First, evaluate all dependencies
        from evaluate_rotatingslats import topological_sort
        sorted_components = topological_sort(graph)
        
        # Evaluate components in order
        for comp_id in sorted_components:
            if comp_id not in evaluated and comp_id in graph:
                try:
                    comp_data = graph[comp_id]
                    if isinstance(comp_data, dict) and 'obj' in comp_data:
                        evaluate_component(comp_id, comp_data, evaluated, all_objects, output_params, graph=graph)
                except Exception as e:
                    pass  # Skip errors for now
        
        geometry_value = resolve_input_value(second_move_guid, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"   Geometry type: {type(geometry_value).__name__}")
        if geometry_value is None:
            print(f"   WARNING: Geometry value is None!")
        elif isinstance(geometry_value, list) and len(geometry_value) > 0:
            first_geom = geometry_value[0]
            if isinstance(first_geom, dict) and 'corners' in first_geom:
                corners = first_geom.get('corners', [])
                if corners:
                    print(f"   First rectangle first corner: {corners[0]}")
                    print(f"   Expected Y: 0.0 (after Polar Array and List Item)")
                    actual_y = corners[0][1] if len(corners[0]) > 1 else None
                    if actual_y is not None:
                        print(f"   Actual Y: {actual_y}")
                        print(f"   Y Difference: {actual_y - 0.0}")
            else:
                print(f"   First geometry type: {type(first_geom).__name__}, keys: {list(first_geom.keys()) if isinstance(first_geom, dict) else 'N/A'}")
        else:
            print(f"   Geometry value: {geometry_value}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"   ERROR: Second Move component not found in graph!")

# 2. Check motion vector input to second Move
print("\n2. MOTION VECTOR INPUT TO SECOND MOVE (0532cbdf):")
print("-" * 80)
if second_move_guid:
    comp_info = graph[second_move_guid]
    try:
        motion_value = resolve_input_value(second_move_guid, 'param_input_1', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"   Motion type: {type(motion_value).__name__}")
        if isinstance(motion_value, list) and len(motion_value) > 0:
            if isinstance(motion_value[0], list):
                print(f"   Motion: list of {len(motion_value)} vectors")
                print(f"   First vector: {motion_value[0]}")
                print(f"   Expected: [11.32743, -27.416834, 3.8]")
                if len(motion_value[0]) > 1:
                    actual_y = motion_value[0][1]
                    print(f"   Actual Y: {actual_y}")
                    print(f"   Expected Y: -27.416834")
                    print(f"   Y Difference: {actual_y - (-27.416834)}")
            else:
                print(f"   Motion: single vector {motion_value}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

# 3. Check second Move output
print("\n3. SECOND MOVE OUTPUT (0532cbdf):")
print("-" * 80)
if second_move_guid:
    comp_info = graph[second_move_guid]
    try:
        result = evaluate_component(second_move_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[second_move_guid] = result
        moved_geometry = result.get('Geometry', [])
        if isinstance(moved_geometry, list) and len(moved_geometry) > 0:
            first_geom = moved_geometry[0]
            if isinstance(first_geom, dict) and 'corners' in first_geom:
                corners = first_geom.get('corners', [])
                if corners:
                    print(f"   First rectangle first corner after Move: {corners[0]}")
                    print(f"   Expected: [11.32743, -27.416834, 3.8]")
                    if len(corners[0]) > 1:
                        actual_y = corners[0][1]
                        print(f"   Actual Y: {actual_y}")
                        print(f"   Expected Y: -27.416834")
                        print(f"   Y Difference: {actual_y - (-27.416834)}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

# 4. Check Area component output
print("\n4. AREA COMPONENT OUTPUT (3bd2c1d3):")
print("-" * 80)
area_guid = None
for comp_id, comp_data in graph.items():
    if isinstance(comp_data, dict):
        obj = comp_data.get('obj', {})
        if obj.get('instance_guid') == '3bd2c1d3-149d-49fb-952c-8db272035f9e':
            area_guid = comp_id
            break

if area_guid:
    comp_info = graph[area_guid]
    try:
        result = evaluate_component(area_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[area_guid] = result
        centroid = result.get('Centroid', [])
        if isinstance(centroid, list) and len(centroid) > 0:
            print(f"   Centroid count: {len(centroid)}")
            print(f"   First centroid: {centroid[0]}")
            print(f"   Expected: [11.32743, -27.416834, 3.8]")
            if len(centroid[0]) > 1:
                actual_y = centroid[0][1]
                print(f"   Actual Y: {actual_y}")
                print(f"   Expected Y: -27.416834")
                print(f"   Y Difference: {actual_y - (-27.416834)}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("Check each step above to identify where the -0.07 Y difference is introduced.")

