#!/usr/bin/env python3
"""Debug script to trace the centroid chain and identify where the Y coordinate mismatch occurs."""

import json
import sys
from evaluate_rotatingslats import load_component_graph, resolve_input_value, evaluate_component, get_external_inputs

# Load graph
graph = load_component_graph('complete_component_graph.json')
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

# Expected values
expected_centroid_y = -27.416834
expected_centroid_z_first = 3.8

print("=" * 80)
print("TRACING CENTROID CHAIN")
print("=" * 80)

# 1. Check Series component (680b290d)
print("\n1. SERIES COMPONENT (680b290d):")
series_guid = None
for comp_id, comp_data in graph.items():
    if isinstance(comp_data, dict):
        obj = comp_data.get('obj', {})
        if obj.get('instance_guid') == '680b290d-e662-4a76-9b3c-e5e921230589':
            series_guid = comp_id
            break

if series_guid:
    comp_info = graph[series_guid]
    try:
        result = evaluate_component(series_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[series_guid] = result
        series_output = result.get('Series', [])
        print(f"   Series output: {series_output[:5]}... (first 5)")
        print(f"   Expected: [-0.07, 0.93, 1.93, 2.93, 3.93, ...]")
    except Exception as e:
        print(f"   Error: {e}")

# 2. Check Vector 2Pt component (ea032caa)
print("\n2. VECTOR 2PT COMPONENT (ea032caa):")
vector_2pt_guid = None
for comp_id, comp_data in graph.items():
    if isinstance(comp_data, dict):
        obj = comp_data.get('obj', {})
        if obj.get('instance_guid') == 'ea032caa-ddff-403c-ab58-8ab6e24931ac':
            vector_2pt_guid = comp_id
            break

if vector_2pt_guid:
    comp_info = graph[vector_2pt_guid]
    try:
        result = evaluate_component(vector_2pt_guid, comp_info, evaluated, all_objects, output_params, graph=graph)
        evaluated[vector_2pt_guid] = result
        vector_output = result.get('Vector', [])
        if isinstance(vector_output, list) and len(vector_output) > 0:
            print(f"   Vector 2Pt output: {len(vector_output)} vectors")
            print(f"   First vector: {vector_output[0]}")
            print(f"   Expected: [0.0, 0.07, 3.8]")
            if len(vector_output) > 1:
                print(f"   Last vector: {vector_output[-1]}")
                print(f"   Expected: [0.0, 0.07, 3.1]")
    except Exception as e:
        print(f"   Error: {e}")

# 3. Check second Move component (0532cbdf) Motion input
print("\n3. SECOND MOVE MOTION INPUT (0532cbdf):")
second_move_guid = None
for comp_id, comp_data in graph.items():
    if isinstance(comp_data, dict):
        obj = comp_data.get('obj', {})
        if obj.get('instance_guid') == '0532cbdf-875b-4db9-8c88-352e21051436':
            second_move_guid = comp_id
            break

if second_move_guid:
    comp_info = graph[second_move_guid]
    try:
        motion_value = resolve_input_value(second_move_guid, 'param_input_1', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"   Motion value type: {type(motion_value).__name__}")
        if isinstance(motion_value, list):
            if len(motion_value) > 0:
                if isinstance(motion_value[0], list):
                    print(f"   Motion: list of {len(motion_value)} vectors")
                    print(f"   First vector: {motion_value[0]}")
                    print(f"   Expected: [11.32743, -27.416834, 3.8]")
                    if len(motion_value) > 1:
                        print(f"   Last vector: {motion_value[-1]}")
                        print(f"   Expected: [11.32743, -27.416834, 3.1]")
                else:
                    print(f"   Motion: single vector {motion_value}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

# 4. Check second Move component Geometry input
print("\n4. SECOND MOVE GEOMETRY INPUT (0532cbdf):")
if second_move_guid:
    comp_info = graph[second_move_guid]
    try:
        geometry_value = resolve_input_value(second_move_guid, 'param_input_0', comp_info, evaluated, all_objects, output_params, graph=graph)
        print(f"   Geometry type: {type(geometry_value).__name__}")
        if isinstance(geometry_value, list) and len(geometry_value) > 0:
            first_geom = geometry_value[0]
            if isinstance(first_geom, dict) and 'corners' in first_geom:
                corners = first_geom.get('corners', [])
                if corners:
                    print(f"   First rectangle first corner: {corners[0]}")
                    print(f"   Expected Y: 0.0 (after Polar Array and List Item)")
    except Exception as e:
        print(f"   Error: {e}")

# 5. Check second Move component output
print("\n5. SECOND MOVE OUTPUT (0532cbdf):")
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
                    actual_y = corners[0][1] if len(corners[0]) > 1 else None
                    if actual_y:
                        print(f"   Actual Y: {actual_y}")
                        print(f"   Expected Y: {expected_centroid_y}")
                        print(f"   Difference: {actual_y - expected_centroid_y}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

# 6. Check Area component output
print("\n6. AREA COMPONENT OUTPUT (3bd2c1d3):")
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
            print(f"   Expected: [11.32743, {expected_centroid_y}, {expected_centroid_z_first}]")
            if len(centroid) > 0:
                actual_y = centroid[0][1] if len(centroid[0]) > 1 else None
                actual_z = centroid[0][2] if len(centroid[0]) > 2 else None
                if actual_y:
                    print(f"   Actual Y: {actual_y}")
                    print(f"   Expected Y: {expected_centroid_y}")
                    print(f"   Y Difference: {actual_y - expected_centroid_y}")
                if actual_z:
                    print(f"   Actual Z: {actual_z}")
                    print(f"   Expected Z: {expected_centroid_z_first}")
                    print(f"   Z Difference: {actual_z - expected_centroid_z_first}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Expected centroid Y: {expected_centroid_y}")
print(f"Expected centroid Z (first): {expected_centroid_z_first}")
print("\nCheck the differences above to identify where the mismatch occurs.")

