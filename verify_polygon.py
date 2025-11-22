"""
Verify Polygon component in Rotatingslats chain.
"""
import json
import sys
sys.path.insert(0, '.')

from evaluate_rotatingslats import load_component_graph, evaluate_graph, get_external_inputs
import math

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

# Polygon component GUID
polygon_guid = 'a2151ddb-9077-4065-90f3-e337cd983593'

print("=" * 80)
print("POLYGON COMPONENT VERIFICATION")
print("=" * 80)
print()

# Get component info
polygon_comp = graph.get(polygon_guid, {})
if not polygon_comp:
    print(f"Polygon component {polygon_guid[:8]}... NOT FOUND")
    sys.exit(1)

print("Component Info:")
print(f"  GUID: {polygon_guid}")
print(f"  Type: {polygon_comp.get('obj', {}).get('type', 'Unknown')}")
print(f"  NickName: {polygon_comp.get('obj', {}).get('nickname', 'Unknown')}")
print()

# Get inputs
inputs_info = polygon_comp.get('inputs', {})
plane_input = inputs_info.get('param_input_0', {})
radius_input = inputs_info.get('param_input_1', {})
segments_input = inputs_info.get('param_input_2', {})
fillet_input = inputs_info.get('param_input_3', {})

print("Inputs:")
print("  1. Plane:")
plane_persistent = plane_input.get('persistent_values', [])
if plane_persistent:
    plane = json.loads(plane_persistent[0])
    print(f"     Origin: {plane['origin']}")
    print(f"     Normal: {plane['normal']}")
else:
    print("     No persistent value")
print()

print("  2. Radius:")
radius_persistent = radius_input.get('persistent_values', [])
if radius_persistent:
    radius = float(radius_persistent[0])
    print(f"     Value: {radius}")
else:
    print("     No persistent value")
print()

print("  3. Segments:")
segments_sources = segments_input.get('sources', [])
if segments_sources:
    seg_source = segments_sources[0]
    print(f"     Source: {seg_source.get('source_obj_name', 'Unknown')} ({seg_source.get('source_guid', '')[:8] if seg_source.get('source_guid') else 'N/A'}...)")
    # Get value from external_inputs
    with open('external_inputs.json', 'r') as f:
        ext_inputs = json.load(f)
    seg_value = ext_inputs.get(seg_source.get('source_guid', ''), {}).get('value', 'N/A')
    print(f"     Value: {seg_value}")
else:
    seg_persistent = segments_input.get('persistent_values', [])
    if seg_persistent:
        print(f"     Value: {seg_persistent[0]} (persistent)")
    else:
        print("     No value")
print()

print("  4. Fillet Radius:")
fillet_persistent = fillet_input.get('persistent_values', [])
if fillet_persistent:
    fillet = float(fillet_persistent[0])
    print(f"     Value: {fillet}")
else:
    print("     No persistent value")
print()

print("Expected Output:")
print("  - Polygon geometry with vertices on a circle")
print("  - Radius: 3.0")
print("  - Segments: 8 (octagon)")
print("  - Vertices: 8 points + closing point = 9 vertices")
print()

# Evaluate
print("Evaluating graph...")
evaluated = evaluate_graph(graph_data if isinstance(graph_data, dict) and 'components' in graph_data else graph, 
                          all_objects, output_params)

print("\nEvaluation Result:")
if polygon_guid in evaluated:
    result = evaluated[polygon_guid]
    print(f"  Result type: {type(result).__name__}")
    print(f"  Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
    
    if isinstance(result, dict):
        # Check if result itself is the polygon dict
        if 'vertices' in result or 'polygon' in result:
            polygon = result
        else:
            polygon = result.get('Polygon') or result.get('polygon')
        
        if polygon:
            print(f"  Polygon type: {type(polygon).__name__}")
            if isinstance(polygon, dict):
                print(f"  Polygon keys: {list(polygon.keys())}")
                if 'vertices' in polygon:
                    vertices = polygon['vertices']
                    print(f"  Number of vertices: {len(vertices)}")
                    print(f"  First vertex: {vertices[0]}")
                    print(f"  Last vertex: {vertices[-1]}")
                    # Check if closed (first == last)
                    if len(vertices) > 0:
                        first = vertices[0]
                        last = vertices[-1]
                        is_closed = all(abs(first[i] - last[i]) < 1e-10 for i in range(min(len(first), len(last))))
                        print(f"  Is closed: {is_closed}")
                if 'radius' in polygon:
                    print(f"  Radius: {polygon['radius']}")
                if 'segments' in polygon:
                    print(f"  Segments: {polygon['segments']}")
                if 'plane' in polygon:
                    print(f"  Plane: {polygon['plane']}")
                
                # Verify vertices are on circle
                if 'vertices' in polygon and 'radius' in polygon and 'plane' in polygon:
                    vertices = polygon['vertices']
                    radius = polygon['radius']
                    plane = polygon['plane']
                    origin = plane.get('origin', [0.0, 0.0, 0.0])
                    
                    print(f"\n  Verification:")
                    print(f"    Checking vertices are on circle (radius={radius}, origin={origin}):")
                    all_on_circle = True
                    for i, vertex in enumerate(vertices[:-1]):  # Exclude closing vertex
                        if len(vertex) >= 2:
                            dx = vertex[0] - origin[0] if len(origin) > 0 else vertex[0]
                            dy = vertex[1] - origin[1] if len(origin) > 1 else vertex[1]
                            dist = math.sqrt(dx*dx + dy*dy)
                            error = abs(dist - radius)
                            if error > 0.01:  # Allow small floating point error
                                print(f"      Vertex {i}: distance={dist:.6f}, error={error:.6f} ❌")
                                all_on_circle = False
                    if all_on_circle:
                        print(f"      All vertices on circle [OK]")
        else:
            print(f"  Polygon key not found, result: {result}")
    else:
        print(f"  Result: {str(result)[:200]}...")
else:
    print("  NOT EVALUATED")

