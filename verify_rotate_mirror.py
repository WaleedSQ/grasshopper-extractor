"""
Verify Rotate and Mirror components in Rotatingslats chain.
"""
import json
import sys
import math
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, evaluate_graph, get_external_inputs

# Load data
graph_data = load_component_graph('complete_component_graph.json')
graph = graph_data.get('components', graph_data) if isinstance(graph_data, dict) and 'components' in graph_data else graph_data

with open('rotatingslats_data.json', 'r') as f:
    data = json.load(f)
    all_objects = {}
    all_objects.update(data.get('group_objects', {}))
    all_objects.update(data.get('external_objects', {}))

# Build output params
output_params = {}
for key, obj in all_objects.items():
    for param_key, param_info in obj.get('params', {}).items():
        if param_key.startswith('param_output'):
            param_guid = param_info.get('data', {}).get('InstanceGuid')
            if param_guid:
                output_params[param_guid] = {
                    'obj': obj,
                    'param_key': param_key,
                    'param_info': param_info
                }

# Component GUIDs
rotate_guid = '5a77f108-b5a1-429b-9d22-0a14d7945abd'
mirror_guid = '47650d42-5fa9-44b3-b970-9f28b94bb031'
polygon_guid = 'a2151ddb-9077-4065-90f3-e337cd983593'

print("=" * 80)
print("ROTATE AND MIRROR COMPONENTS VERIFICATION")
print("=" * 80)
print()

# Evaluate
print("Evaluating graph...")
evaluated = evaluate_graph(graph_data if isinstance(graph_data, dict) and 'components' in graph_data else graph, 
                          all_objects, output_params)

# ============================================================================
# ROTATE COMPONENT
# ============================================================================
print("\n" + "=" * 80)
print("ROTATE COMPONENT")
print("=" * 80)
print()

rotate_comp = graph.get(rotate_guid, {})
if not rotate_comp:
    print(f"Rotate component {rotate_guid[:8]}... NOT FOUND")
else:
    print("Component Info:")
    print(f"  GUID: {rotate_guid}")
    print(f"  Type: {rotate_comp.get('obj', {}).get('type', 'Unknown')}")
    print(f"  NickName: {rotate_comp.get('obj', {}).get('nickname', 'Unknown')}")
    print()
    
    # Get inputs
    inputs_info = rotate_comp.get('inputs', {})
    geom_input = inputs_info.get('param_input_0', {})
    angle_input = inputs_info.get('param_input_1', {})
    plane_input = inputs_info.get('param_input_2', {})
    
    print("Inputs:")
    # Geometry source
    geom_sources = geom_input.get('sources', [])
    if geom_sources:
        geom_source = geom_sources[0]
        print(f"  Geometry: from {geom_source.get('source_obj_name', 'Unknown')} ({geom_source.get('source_obj_guid', '')[:8] if geom_source.get('source_obj_guid') else 'N/A'}...)")
        print(f"    Source GUID: {geom_source.get('source_guid', 'N/A')[:8] if geom_source.get('source_guid') else 'N/A'}...")
    else:
        print(f"  Geometry: No source")
    
    # Angle
    angle_persistent = angle_input.get('persistent_values', [])
    if angle_persistent:
        angle = float(angle_persistent[0])
        print(f"  Angle: {angle} degrees ({math.radians(angle):.6f} radians)")
    else:
        print(f"  Angle: {angle_input.get('values', ['N/A'])[0]}")
    
    # Plane
    plane_persistent = plane_input.get('persistent_values', [])
    if plane_persistent:
        plane = json.loads(plane_persistent[0])
        print(f"  Plane: origin={plane['origin']}, normal={plane.get('normal', plane.get('z_axis', 'N/A'))}")
    else:
        print(f"  Plane: No persistent value")
    print()
    
    print("Expected Output:")
    print("  - Rotated polygon geometry")
    print("  - Vertices rotated by angle around plane normal")
    print()
    
    # Check Polygon output first
    if polygon_guid in evaluated:
        polygon_result = evaluated[polygon_guid]
        print("Polygon Output (input to Rotate):")
        print(f"  Type: {type(polygon_result).__name__}")
        if isinstance(polygon_result, dict):
            print(f"  Keys: {list(polygon_result.keys())}")
            # Polygon returns dict directly, not wrapped
            if 'vertices' in polygon_result:
                print(f"  Has vertices: True")
                print(f"  Number of vertices: {len(polygon_result['vertices'])}")
            elif 'Polygon' in polygon_result:
                polygon_geom = polygon_result['Polygon']
                print(f"  Polygon geometry type: {type(polygon_geom).__name__}")
                if isinstance(polygon_geom, dict):
                    print(f"  Has vertices: {'vertices' in polygon_geom}")
        print()
    
    # Check evaluation result
    print("Evaluation Result:")
    if rotate_guid in evaluated:
        result = evaluated[rotate_guid]
        if isinstance(result, dict):
            geom = result.get('Geometry')
            if geom:
                print(f"  Geometry type: {type(geom).__name__}")
                print(f"  Geometry value: {str(geom)[:100]}...")
                if isinstance(geom, dict):
                    print(f"  Geometry keys: {list(geom.keys())}")
                    if 'vertices' in geom:
                        vertices = geom['vertices']
                        print(f"  Number of vertices: {len(vertices)}")
                        if vertices:
                            print(f"  First vertex: {vertices[0]}")
                            print(f"  Last vertex: {vertices[-1]}")
                    if 'rotation_angle' in geom:
                        print(f"  Rotation angle: {geom['rotation_angle']} degrees")
                    
                    # Verify rotation
                    if 'vertices' in geom and polygon_guid in evaluated:
                        polygon_result = evaluated[polygon_guid]
                        if isinstance(polygon_result, dict):
                            polygon = polygon_result.get('Polygon') or polygon_result
                            if isinstance(polygon, dict) and 'vertices' in polygon:
                                orig_vertices = polygon['vertices']
                                rotated_vertices = geom['vertices']
                                if len(orig_vertices) == len(rotated_vertices) and len(orig_vertices) > 0:
                                    # Check first vertex rotation
                                    orig_v = orig_vertices[0]
                                    rot_v = rotated_vertices[0]
                                    if len(orig_v) >= 2 and len(rot_v) >= 2:
                                        orig_angle = math.atan2(orig_v[1], orig_v[0])
                                        rot_angle = math.atan2(rot_v[1], rot_v[0])
                                        angle_diff = math.degrees(rot_angle - orig_angle)
                                        print(f"\n  Rotation Verification:")
                                        print(f"    Original first vertex angle: {math.degrees(orig_angle):.2f} degrees")
                                        print(f"    Rotated first vertex angle: {math.degrees(rot_angle):.2f} degrees")
                                        print(f"    Angle difference: {angle_diff:.2f} degrees")
                                        if abs(angle_diff - angle) < 1.0:  # Allow small error
                                            print(f"    [OK] Rotation matches expected angle")
                                        else:
                                            print(f"    [WARNING] Rotation angle mismatch")
            else:
                print(f"  Geometry: None")
        else:
            print(f"  Result: {str(result)[:100]}...")
    else:
        print("  NOT EVALUATED")

# ============================================================================
# MIRROR COMPONENT
# ============================================================================
print("\n" + "=" * 80)
print("MIRROR COMPONENT")
print("=" * 80)
print()

mirror_comp = graph.get(mirror_guid, {})
if not mirror_comp:
    print(f"Mirror component {mirror_guid[:8]}... NOT FOUND")
else:
    print("Component Info:")
    print(f"  GUID: {mirror_guid}")
    print(f"  Type: {mirror_comp.get('obj', {}).get('type', 'Unknown')}")
    print(f"  NickName: {mirror_comp.get('obj', {}).get('nickname', 'Unknown')}")
    print()
    
    # Get inputs
    inputs_info = mirror_comp.get('inputs', {})
    geom_input = inputs_info.get('param_input_0', {})
    plane_input = inputs_info.get('param_input_1', {})
    
    print("Inputs:")
    # Geometry source
    geom_sources = geom_input.get('sources', [])
    if geom_sources:
        geom_source = geom_sources[0]
        print(f"  Geometry: from {geom_source.get('source_obj_name', 'Unknown')} ({geom_source.get('source_obj_guid', '')[:8] if geom_source.get('source_obj_guid') else 'N/A'}...)")
        print(f"    Source GUID: {geom_source.get('source_guid', 'N/A')[:8] if geom_source.get('source_guid') else 'N/A'}...")
    else:
        print(f"  Geometry: No source")
    
    # Plane
    plane_persistent = plane_input.get('persistent_values', [])
    if plane_persistent:
        plane = json.loads(plane_persistent[0])
        print(f"  Plane: origin={plane['origin']}, normal={plane.get('normal', plane.get('z_axis', 'N/A'))}")
    else:
        print(f"  Plane: No persistent value")
    print()
    
    print("Expected Output:")
    print("  - Mirrored polygon geometry")
    print("  - Vertices mirrored across plane")
    print()
    
    # Check evaluation result
    print("Evaluation Result:")
    if mirror_guid in evaluated:
        result = evaluated[mirror_guid]
        if isinstance(result, dict):
            geom = result.get('Geometry')
            if geom:
                print(f"  Geometry type: {type(geom).__name__}")
                if isinstance(geom, dict):
                    print(f"  Geometry keys: {list(geom.keys())}")
                    if 'vertices' in geom:
                        vertices = geom['vertices']
                        print(f"  Number of vertices: {len(vertices)}")
                        if vertices:
                            print(f"  First vertex: {vertices[0]}")
                            print(f"  Last vertex: {vertices[-1]}")
                    
                    # Verify mirror
                    if 'vertices' in geom and rotate_guid in evaluated:
                        rotate_result = evaluated[rotate_guid]
                        if isinstance(rotate_result, dict):
                            rotated_geom = rotate_result.get('Geometry')
                            if isinstance(rotated_geom, dict) and 'vertices' in rotated_geom:
                                rotated_vertices = rotated_geom['vertices']
                                mirrored_vertices = geom['vertices']
                                if len(rotated_vertices) == len(mirrored_vertices) and len(rotated_vertices) > 0:
                                    # Check if vertices are mirrored
                                    # Mirror plane normal is [1, 0, 0] (X-axis)
                                    # So X coordinates should be negated
                                    print(f"\n  Mirror Verification:")
                                    first_rot = rotated_vertices[0]
                                    first_mir = mirrored_vertices[0]
                                    if len(first_rot) >= 3 and len(first_mir) >= 3:
                                        x_rot = first_rot[0]
                                        x_mir = first_mir[0]
                                        print(f"    Rotated first vertex X: {x_rot:.6f}")
                                        print(f"    Mirrored first vertex X: {x_mir:.6f}")
                                        if abs(x_rot + x_mir) < 0.01:  # X should be negated
                                            print(f"    [OK] X coordinate mirrored (negated)")
                                        else:
                                            print(f"    [WARNING] X coordinate not properly mirrored")
            else:
                print(f"  Geometry: None")
        else:
            print(f"  Result: {str(result)[:100]}...")
    else:
        print("  NOT EVALUATED")

