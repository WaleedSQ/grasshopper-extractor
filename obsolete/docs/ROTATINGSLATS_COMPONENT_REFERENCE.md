# Rotatingslats Component Reference

## Overview

The Rotatingslats computation chain evaluates rotation angles for slats based on sun position. The pipeline processes geometry inputs (slat surfaces, points, vectors) through a series of transformations and calculations to compute the angle between slat normals and the sun vector. The final output is converted from radians to degrees and displayed in a yellow panel. The evaluator uses topological sort to resolve dependencies and evaluates components in the correct order. Sun inputs (`sun_vector`, `sun_angle_deg`) are currently hard-coded as specified.

**Pipeline flow**: External inputs (sliders, panels, geometry) → Geometry construction (Polygon, Rotate, Mirror, Deconstruct Brep) → Vector operations (Vector 2Pt, Amplitude, Vector XYZ) → Angle calculation → Degrees conversion → Final output panel.

---

## Component Types

### Addition

**GH Metadata:**
- TypeName: `Addition`
- NickNames: `"Result"`, `"+"`
- GUIDs in graph: `d055df7d-4a48-4ccd-b770-433bbaa60269`, `e2671ced-ddeb-4187-8048-66f3d519cefb`

**Code Mapping:**
- Function: `addition_component(a, b)`
- Module: `gh_components.py`
- Signature: `(a: Union[float, List[float]], b: Union[float, List[float]]) -> Union[float, List[float]]`

**Semantics:**
- Adds two numbers or element-wise adds two vectors
- Input matching: scalar/scalar → scalar, list/list → list (must have same length)
- No graft/flatten/simplify flags handled
- Assumes vectors have same length if both are lists

---

### Amplitude

**GH Metadata:**
- TypeName: `Amplitude`
- NickNames: `"Amplitude"`
- GUIDs in graph: `f54babb4-b955-42d1-aeb1-3b2192468fed`, `d0668a07-...`

**Code Mapping:**
- Function: `amplitude_component(vector, amplitude)`
- Module: `gh_components.py`
- Signature: `(vector: List[float], amplitude: float) -> List[float]`

**Semantics:**
- Normalizes input vector to unit length, then scales by amplitude value
- Input: vector3 list, scalar amplitude
- Output: vector3 list
- Returns `[0.0, 0.0, 0.0]` if input vector length < 1e-10

---

### Angle

**GH Metadata:**
- TypeName: `Angle`
- NickNames: `"Angle"`, `"Rotation angles from normal"`
- GUIDs in graph: `0d695e6b-3696-4337-bc80-d14104f8a59e`

**Code Mapping:**
- Function: `angle_component(vectorA, vectorB, plane)`
- Module: `gh_components.py`
- Signature: `(vectorA: List[float], vectorB: List[float], plane: Optional[dict]) -> Tuple[float, float]`

**Semantics:**
- Computes angle between two vectors in radians
- Inputs: vector3 list A, vector3 list B, optional plane dict
- Outputs: `(angle: float, reflex: float)` where reflex = 2π - angle
- Vectors are normalized before calculation
- Returns `(0.0, 0.0)` if either vector length < 1e-10
- Evaluator handles dict inputs by extracting 'Vector' or 'Normal' keys, defaults to `[0.0, 0.0, 0.0]` if not list

---

### Area

**GH Metadata:**
- TypeName: `Area`
- NickNames: `"Area"`
- GUIDs in graph: `16022012-569d-4c58-a081-6d57649a1720`, `3732df33-c378-4227-b549-b5ab541e82c6`

**Code Mapping:**
- Function: `area_component(geometry)`
- Module: `gh_components.py`
- Signature: `(geometry: Any) -> float`

**Semantics:**
- Computes area of geometry (simplified implementation returns 0.0)
- Input: geometry object
- Output: area value (float) and centroid point `[x, y, z]`
- Evaluator returns `{'Area': result, 'Centroid': [0.0, 0.0, 0.0]}`

---

### Box 2Pt

**GH Metadata:**
- TypeName: `Box 2Pt`
- NickNames: `"Box 2Pt"`
- GUIDs in graph: `b908d823-e613-4684-9e94-65a0f60f19b7`

**Code Mapping:**
- Function: `box_2pt_component(corner1, corner2)`
- Module: `gh_components.py`
- Signature: `(corner1: List[float], corner2: List[float]) -> Any`

**Semantics:**
- Creates box geometry from two corner points
- Inputs: `Point A` (vector3), `Point B` (vector3) - also accepts `Corner 1`/`Corner 2`
- Output: box geometry dict `{'corner1': corner1, 'corner2': corner2}`
- Simplified implementation returns corner dict

---

### Construct Plane

**GH Metadata:**
- TypeName: `Construct Plane`
- NickNames: `"Construct Plane"`
- GUIDs in graph: `7ad636cc-e506-4f77-bb82-4a86ba2a3fea`

**Code Mapping:**
- Function: `construct_plane_component(origin, x_axis, y_axis)`
- Module: `gh_components.py`
- Signature: `(origin: List[float], x_axis: List[float], y_axis: List[float]) -> dict`

**Semantics:**
- Creates plane from origin point and X/Y axis vectors
- Inputs: origin (vector3), X axis (vector3), Y axis (vector3)
- Output: plane dict with `'origin'`, `'x_axis'`, `'y_axis'`, `'z_axis'`, `'normal'`
- X and Y axes are normalized; Z-axis computed as cross product
- Raises error if X or Y axis length < 1e-10

---

### Construct Point

**GH Metadata:**
- TypeName: `Construct Point`
- NickNames: `"p1"`, `"Target point"`
- GUIDs in graph: `57648120-f088-4498-99d0-f8f7f3b69b89`, `a6b98c27-e4dd-405e-93f5-755c12294748`, and 3 more

**Code Mapping:**
- Function: `construct_point_component(x, y, z)`
- Module: `gh_components.py`
- Signature: `(x: float, y: float, z: float) -> List[float]`

**Semantics:**
- Creates point from X, Y, Z coordinates
- Inputs: scalar X, scalar Y, scalar Z
- Output: point `[x, y, z]` list

---

### Deconstruct Brep

**GH Metadata:**
- TypeName: `Deconstruct Brep`
- NickNames: `"Deconstruct Brep"`
- GUIDs in graph: `c78ea9c5-07c7-443b-b188-078a6056dae8`

**Code Mapping:**
- Function: `deconstruct_brep_component(brep)`
- Module: `gh_components.py`
- Signature: `(brep: Any) -> Any`

**Semantics:**
- Deconstructs brep into faces, edges, vertices
- Input: brep geometry
- Output: dict with `'Faces'`, `'Edges'`, `'Vertices'` keys
- Returns at least one placeholder edge if brep is not None (for List Item access)

---

### Degrees

**GH Metadata:**
- TypeName: `Degrees`
- NickNames: `"Degrees"`
- GUIDs in graph: `fa0ba5a6-7dd9-43f4-a82a-cf02841d0f58`

**Code Mapping:**
- Function: `degrees_component(radians)`
- Module: `gh_components.py`
- Signature: `(radians: float) -> float`

**Semantics:**
- Converts radians to degrees
- Input: angle in radians (scalar)
- Output: angle in degrees (scalar)
- Uses `math.degrees()` conversion
- Final output parameter GUID: `4d5670e5-1abc-417e-b9ce-3cf7878b98c2`

---

### Division

**GH Metadata:**
- TypeName: `Division`
- NickNames: `"/"`, `"Result"`
- GUIDs in graph: `f9a68fee-bd6c-477a-9d8e-ae9e35697ab1`, and 1 more

**Code Mapping:**
- Function: `division_component(a, b)`
- Module: `gh_components.py`
- Signature: `(a: Union[float, List[float]], b: float) -> Union[float, List[float]]`

**Semantics:**
- Divides a by b
- Inputs: dividend (number or vector), divisor (number)
- Output: quotient (number or vector)
- Raises error if divisor < 1e-10 (division by zero)
- If dividend is list, performs element-wise division

---

### Divide Length

**GH Metadata:**
- TypeName: `Divide Length`
- NickNames: `"DL"`
- GUIDs in graph: `c7b8773d-e1e0-4c31-9b7c-b8b54f9e40e0`, and 1 more

**Code Mapping:**
- Function: `divide_length_component(curve, length)`
- Module: `gh_components.py`
- Signature: `(curve: Any, length: float) -> List[List[float]]`

**Semantics:**
- Divides curve by length value, creating points along curve
- Inputs: curve geometry, segment length (scalar)
- Output: list of points `[[x, y, z], ...]`
- Simplified implementation returns placeholder points
- Returns empty list if length <= 0

---

### Distance

**GH Metadata:**
- TypeName: `Distance`
- NickNames: `"Distance"`
- GUIDs in graph: (not in main computation path)

**Code Mapping:**
- Function: `distance_component(pointA, pointB)`
- Module: `gh_components.py`
- Signature: `(pointA: List[float], pointB: List[float]) -> float`

**Semantics:**
- Computes Euclidean distance between two points
- Inputs: point A (vector3), point B (vector3)
- Output: distance scalar

---

### Evaluate Surface

**GH Metadata:**
- TypeName: `Evaluate Surface`
- NickNames: `"Evaluate Surface"`
- GUIDs in graph: `d8de94de-c80f-4737-8059-5d259b78807c`

**Code Mapping:**
- Function: `evaluate_surface_component(surface, u, v)`
- Module: `gh_components.py`
- Signature: `(surface: Any, u: float, v: float) -> List[float]`

**Semantics:**
- Evaluates surface at U, V parameters
- Inputs: surface geometry, U parameter (scalar), V parameter (scalar)
- Output: point on surface `[x, y, z]`
- Evaluator extracts u, v from Point input (first two elements if list)
- Simplified implementation returns `[u, v, 0.0]`

---

### Line

**GH Metadata:**
- TypeName: `Line`
- NickNames: `"Between"`, `"In Ray"`
- GUIDs in graph: `c7dba531-36f1-4a2d-8e0e-ed94b3873bba`, and 2 more

**Code Mapping:**
- Function: `line_component(start_point, end_point)`
- Module: `gh_components.py`
- Signature: `(start_point: List[float], end_point: List[float]) -> dict`

**Semantics:**
- Creates line from start to end point
- Inputs: `Start Point` (vector3), `End Point` (vector3) - also accepts `Start`/`End` or `Point A`/`Point B`
- Output: line dict with `'start'`, `'end'`, `'direction'`, `'length'`

---

### List Item

**GH Metadata:**
- TypeName: `List Item`
- NickNames: `"LI"`
- GUIDs in graph: `d89d47e0-f858-44d9-8427-fdf2e3230954`, and 7 more

**Code Mapping:**
- Function: `list_item_component(list_data, index)`
- Module: `gh_components.py`
- Signature: `(list_data: List[Any], index: int) -> Any`

**Semantics:**
- Gets item from list by index
- Inputs: list, index (scalar, default 0)
- Output: item at index
- Raises IndexError if index out of range
- Wrap behavior: not implemented (always raises on out-of-range)

---

### MD Slider

**GH Metadata:**
- TypeName: `MD Slider`
- NickNames: `"MD Slider"`
- GUIDs in graph: `c4c92669-f802-4b5f-b3fb-61b8a642dc0a`

**Code Mapping:**
- Function: `md_slider_component(value)`
- Module: `gh_components.py`
- Signature: `(value: float) -> float`

**Semantics:**
- Passes through slider value
- Input: slider value (scalar or point3d list)
- Output: same value
- Evaluator checks `external_inputs` for value, defaults to 0.0 if not found

---

### Mirror

**GH Metadata:**
- TypeName: `Mirror`
- NickNames: `"Mirror"`
- GUIDs in graph: `47650d42-5fa9-44b3-b970-9f28b94bb031`

**Code Mapping:**
- Function: `mirror_component(geometry, plane)`
- Module: `gh_components.py`
- Signature: `(geometry: Any, plane: Any) -> Any`

**Semantics:**
- Mirrors geometry across plane
- Inputs: geometry, mirror plane
- Output: mirrored geometry
- Simplified implementation returns geometry as-is

---

### Move

**GH Metadata:**
- TypeName: `Move`
- NickNames: `"Slats original"`
- GUIDs in graph: `dfbbd4a2-021a-4c74-ac63-8939e6ac5429`, `ddb9e6ae-7d3e-41ae-8c75-fc726c984724`, and 4 more

**Code Mapping:**
- Function: `move_component(geometry, motion)`
- Module: `gh_components.py`
- Signature: `(geometry: Any, motion: List[float]) -> Any`

**Semantics:**
- Moves geometry by motion vector
- Inputs: `Geometry` (optional, can be None), `Motion` (vector3 list)
- Output: moved geometry
- Evaluator allows None geometry (returns placeholder)
- Simplified implementation returns geometry as-is

---

### Negative

**GH Metadata:**
- TypeName: `Negative`
- NickNames: `"-"`
- GUIDs in graph: `a69d2e4a-b63b-40d0-838f-dff4d90a83ce`, and 5 more

**Code Mapping:**
- Function: `negative_component(value)`
- Module: `gh_components.py`
- Signature: `(value: Union[float, List[float]]) -> Union[float, List[float]]`

**Semantics:**
- Negates number or vector
- Input: number or vector
- Output: negated value
- If input is list, returns element-wise negation
- Evaluator checks `value is None` (not `or value`) to handle 0.0 correctly

---

### Number

**GH Metadata:**
- TypeName: `Number`
- NickNames: `"Targets Height"`, `"Distance between slats"`, and 10 more
- GUIDs in graph: `06d478b1-5fdf-4861-8f0e-1772b5bbf067`, `d1793081-6841-4117-bc0f-e6e4492b65f6`, and 10 more

**Code Mapping:**
- Function: `number_component(value)`
- Module: `gh_components.py`
- Signature: `(value: float) -> float`

**Semantics:**
- Passes through number value
- Input: number (scalar)
- Output: same number
- Can have Source connection to Panel or output parameter
- Evaluator resolves sources through Panel connections or direct output parameter links

---

### Number Slider

**GH Metadata:**
- TypeName: `Number Slider`
- NickNames: `"Number Slider"`
- GUIDs in graph: (external inputs)

**Code Mapping:**
- Function: `number_slider_component(value)`
- Module: `gh_components.py`
- Signature: `(value: float) -> float`

**Semantics:**
- Passes through slider value
- Input: slider value (scalar)
- Output: same value
- Evaluator checks `external_inputs` for value

---

### Plane

**GH Metadata:**
- TypeName: `Plane`
- NickNames: `"Plane"`
- GUIDs in graph: `32cc502c-07b0-4d58-aef1-8acf8b2f4015`, and 1 more

**Code Mapping:**
- Function: `plane_component()`
- Module: `gh_components.py`
- Signature: `() -> dict`

**Semantics:**
- Creates default XY plane at origin
- No inputs
- Output: plane dict with default XY plane `{'origin': [0,0,0], 'x_axis': [1,0,0], 'y_axis': [0,1,0], 'z_axis': [0,0,1], 'normal': [0,0,1]}`

---

### Plane Normal

**GH Metadata:**
- TypeName: `Plane Normal`
- NickNames: `"PN"`, `"Plane Normal"`
- GUIDs in graph: `09db66ec-b6d3-4823-8cec-d459daf0aedc`, and 2 more

**Code Mapping:**
- Function: `plane_normal_component(plane)`
- Module: `gh_components.py`
- Signature: `(plane: dict) -> List[float]`

**Semantics:**
- Extracts normal vector (Z-axis) from plane
- Inputs: `Origin` (vector3), `Z-Axis` (vector3) - also accepts `Plane` dict
- Output: normal vector `[x, y, z]`
- Evaluator constructs plane dict from Origin and Z-Axis if provided separately

---

### Point

**GH Metadata:**
- TypeName: `Point`
- NickNames: `"Point"`
- GUIDs in graph: `12d02e9b-6145-4953-8f48-b184902a818f`, and 2 more

**Code Mapping:**
- Function: `point_component(point)`
- Module: `gh_components.py`
- Signature: `(point: List[float]) -> List[float]`

**Semantics:**
- Passes through or creates point
- Input: point `[x, y, z]` or coordinate
- Output: point `[x, y, z]`
- Evaluator returns `[0.0, 0.0, 0.0]` placeholder if no inputs (external input)

---

### Point On Curve

**GH Metadata:**
- TypeName: `Point On Curve`
- NickNames: `"Point On Curve"`
- GUIDs in graph: `6ce8bcba-18ea-46fc-a145-b1c1b45c304f`

**Code Mapping:**
- Function: `point_on_curve_component(curve, parameter)`
- Module: `gh_components.py`
- Signature: `(curve: Any, parameter: float) -> List[float]`

**Semantics:**
- Evaluates point on curve at parameter
- Inputs: `Curve` (from Container-level Source), `parameter` (scalar, default 0.5)
- Output: point on curve `[x, y, z]`
- Curve input is defined at Container level (not in param_input), source GUID: `8e8b33cf-5b52-4e6f-aca9-d798fd82b943`
- Simplified implementation returns `[0.0, 0.0, 0.0]`

---

### Polar Array

**GH Metadata:**
- TypeName: `Polar Array`
- NickNames: `"Polar Array"`
- GUIDs in graph: (3 instances)

**Code Mapping:**
- Function: `polar_array_component(geometry, center, count, angle)`
- Module: `gh_components.py`
- Signature: `(geometry: Any, center: List[float], count: int, angle: float) -> List[Any]`

**Semantics:**
- Creates polar array of geometry
- Inputs: geometry, center point (vector3), count (scalar), angle (scalar, radians)
- Output: list of geometries
- Simplified implementation returns `[geometry] * count`

---

### Polygon

**GH Metadata:**
- TypeName: `Polygon`
- NickNames: `"Polygon"`
- GUIDs in graph: `a2151ddb-9077-4065-90f3-e337cd983593`

**Code Mapping:**
- Function: `polygon_component(plane, radius, segments, fillet_radius)`
- Module: `gh_components.py`
- Signature: `(plane: Any, radius: float, segments: int, fillet_radius: float) -> Any`

**Semantics:**
- Creates polygon with optional round edges
- Inputs: plane, radius (scalar), segments (scalar), fillet_radius (scalar, default 0.0)
- Output: polygon curve
- Simplified implementation returns placeholder

---

### PolyLine

**GH Metadata:**
- TypeName: `PolyLine`
- NickNames: `"PolyLine"`
- GUIDs in graph: (2 instances)

**Code Mapping:**
- Function: `polyline_component(points, closed)`
- Module: `gh_components.py`
- Signature: `(points: List[List[float]], closed: bool) -> Any`

**Semantics:**
- Creates polyline from points
- Inputs: points (list of vector3), closed (bool, default False)
- Output: polyline geometry
- Simplified implementation returns `{'points': points, 'closed': closed}`

---

### Project

**GH Metadata:**
- TypeName: `Project`
- NickNames: `"Project"`
- GUIDs in graph: `9cd053c9-3dd2-432b-aa46-a29a4b05c339`

**Code Mapping:**
- Function: `project_component(geometry, target, direction)`
- Module: `gh_components.py`
- Signature: `(geometry: Any, target: dict, direction: Any) -> Any`

**Semantics:**
- Projects geometry onto target (plane, surface, etc.)
- Inputs: `Curve` (geometry), `Brep` (target), `Direction` (optional)
- Output: projected geometry
- Simplified implementation projects point onto plane if geometry is point list

---

### Rectangle 2Pt

**GH Metadata:**
- TypeName: `Rectangle 2Pt`
- NickNames: `"Rectangle 2Pt"`
- GUIDs in graph: `a3eb185f-a7cb-4727-aeaf-d5899f934b99`

**Code Mapping:**
- Function: `rectangle_2pt_component(corner1, corner2)`
- Module: `gh_components.py`
- Signature: `(corner1: List[float], corner2: List[float]) -> Any`

**Semantics:**
- Creates rectangle from two corner points
- Inputs: `Point A` (vector3), `Point B` (vector3), `Plane` (optional), `Radius` (optional)
- Output: rectangle geometry
- Simplified implementation returns corner dict

---

### Rotate

**GH Metadata:**
- TypeName: `Rotate`
- NickNames: `"Rotate"`
- GUIDs in graph: `5a77f108-b5a1-429b-9d22-0a14d7945abd`

**Code Mapping:**
- Function: `rotate_component(geometry, angle, plane)`
- Module: `gh_components.py`
- Signature: `(geometry: Any, angle: float, plane: Any) -> Any`

**Semantics:**
- Rotates geometry around plane
- Inputs: `Geometry`, `Angle` (degrees), `Plane`
- Output: rotated geometry
- Simplified implementation returns geometry as-is

---

### Series

**GH Metadata:**
- TypeName: `Series`
- NickNames: `"Series"`
- GUIDs in graph: (3 instances)

**Code Mapping:**
- Function: `series_component(start, count, step)`
- Module: `gh_components.py`
- Signature: `(start: float, count: int, step: float) -> List[float]`

**Semantics:**
- Generates series of numbers
- Inputs: start (scalar), count (scalar), step (scalar)
- Output: list of numbers `[start, start+step, start+2*step, ...]`
- Returns empty list if count < 0

---

### Subtraction

**GH Metadata:**
- TypeName: `Subtraction`
- NickNames: `"-"`, `"Result"`
- GUIDs in graph: `d055df7d-4a48-4ccd-b770-433bbaa60269`, `e2671ced-ddeb-4187-8048-66f3d519cefb`

**Code Mapping:**
- Function: `subtraction_component(a, b)`
- Module: `gh_components.py`
- Signature: `(a: Union[float, List[float]], b: Union[float, List[float]]) -> Union[float, List[float]]`

**Semantics:**
- Subtracts b from a
- Inputs: A (number or vector), B (number or vector)
- Output: difference (number or vector)
- If both are lists, performs element-wise subtraction (must have same length)

---

### Surface

**GH Metadata:**
- TypeName: `Surface`
- NickNames: `"Slat source"`
- GUIDs in graph: `8fec620f-ff7f-4b94-bb64-4c7fce2fcb34`

**Code Mapping:**
- Function: `surface_component(geometry)`
- Module: `gh_components.py`
- Signature: `(geometry: Any) -> Any`

**Semantics:**
- Passes through surface geometry
- Input: surface geometry (from Container-level Source: `dbc236d4-a2fe-48a8-a86e-eebfb04b1053`)
- Output: surface geometry
- Evaluator checks Container-level Source connection to Rectangle 2Pt output

---

### Unit Y

**GH Metadata:**
- TypeName: `Unit Y`
- NickNames: `"Unit Y"`
- GUIDs in graph: (2 instances)

**Code Mapping:**
- Function: `unit_y_component()`
- Module: `gh_components.py`
- Signature: `() -> List[float]`

**Semantics:**
- Returns unit Y vector
- No inputs
- Output: `[0.0, 1.0, 0.0]`

---

### Unit Z

**GH Metadata:**
- TypeName: `Unit Z`
- NickNames: `"Unit Z"`
- GUIDs in graph: (1 instance)

**Code Mapping:**
- Function: `unit_z_component()`
- Module: `gh_components.py`
- Signature: `() -> List[float]`

**Semantics:**
- Returns unit Z vector
- No inputs
- Output: `[0.0, 0.0, 1.0]`

---

### Unitize

**GH Metadata:**
- TypeName: `Unitize`
- NickNames: `"Unitize"`
- GUIDs in graph: (not in main computation path)

**Code Mapping:**
- Function: `unitize_component(vector)`
- Module: `gh_components.py`
- Signature: `(vector: List[float]) -> List[float]`

**Semantics:**
- Normalizes vector to unit length
- Input: vector3 list
- Output: normalized vector3 list
- Returns `[0.0, 0.0, 0.0]` if vector length < 1e-10

---

### Value List

**GH Metadata:**
- TypeName: `Value List`
- NickNames: `"Value List"`
- GUIDs in graph: `e5d1f3af-f59d-40a8-aa35-162cf16c9594`

**Code Mapping:**
- Function: `value_list_component(values)`
- Module: `gh_components.py`
- Signature: `(values: List[Any]) -> List[Any]`

**Semantics:**
- Passes through list of values
- Input: list of values
- Output: same list
- Evaluator checks `persistent_values` or `values` in parameters, returns empty list if no inputs

---

### Vector 2Pt

**GH Metadata:**
- TypeName: `Vector 2Pt`
- NickNames: `"Vector 2Pt"`
- GUIDs in graph: `1f794702-1a6b-441e-b41d-c4749b372177`

**Code Mapping:**
- Function: `vector_2pt_component(pointA, pointB)`
- Module: `gh_components.py`
- Signature: `(pointA: List[float], pointB: List[float]) -> List[float]`

**Semantics:**
- Creates vector from point A to point B
- Inputs: `Point A` (vector3), `Point B` (vector3)
- Output: vector `[x, y, z]` = B - A

---

### Vector XYZ

**GH Metadata:**
- TypeName: `Vector XYZ`
- NickNames: `"Vector XYZ"`
- GUIDs in graph: `0e4c5858-...`, `f5598672-...`

**Code Mapping:**
- Function: `vector_xyz_component(x, y, z)`
- Module: `gh_components.py`
- Signature: `(x: float, y: float, z: float) -> List[float]`

**Semantics:**
- Creates vector from X, Y, Z components
- Inputs: `X component` (scalar), `Y component` (scalar), `Z component` (scalar)
- Output: vector `[x, y, z]`
- Evaluator converts string values from `persistent_values` to float

---

## Pipeline Instances

The following is an ordered list of key nodes along the main computation path from inputs to final output. Components are listed in approximate evaluation order (topological sort order).

1. **External Inputs** → Hard-coded sun values and sliders
   - Sun vector: `[33219.837229, -61164.521016, 71800.722722]`
   - Number of slats: `10.0`
   - Slats height threshold: `3.1`

2. **Subtraction** (`e2671ced-ddeb-4187-8048-66f3d519cefb`) → `subtraction_component`
   - Inputs: A, B (from external inputs)
   - Output: `Result` → feeds Division
   - Role: Computes intermediate value for slat spacing calculation

3. **Subtraction** (`d055df7d-4a48-4ccd-b770-433bbaa60269`) → `subtraction_component`
   - Inputs: A, B
   - Output: `Result` → feeds Division
   - Role: Computes intermediate value for slat spacing calculation

4. **Division** (`f9a68fee-bd6c-477a-9d8e-ae9e35697ab1`) → `division_component`
   - Inputs: A (from Subtraction `e2671ced...`), B (from Subtraction `d055df7d...`)
   - Output: `Result` (`20f5465a...`) → feeds Panel → Number
   - Role: Computes distance between slats

5. **Number** (`06d478b1-5fdf-4861-8f0e-1772b5bbf067`) → `number_component`
   - NickName: "Distance between slats"
   - Inputs: `Value` (from Panel `d019d2ee...` which sources Division output `20f5465a...`)
   - Output: `Value`
   - Role: Passes through distance value for downstream calculations

6. **Box 2Pt** (`b908d823-e613-4684-9e94-65a0f60f19b7`) → `box_2pt_component`
   - Inputs: `Point A`, `Point B`
   - Output: box geometry
   - Role: Defines bounding box for slat geometry

7. **Polygon** (`a2151ddb-9077-4065-90f3-e337cd983593`) → `polygon_component`
   - Inputs: plane, radius, segments, fillet_radius
   - Output: `Polygon` (`b94e42e9...`) → feeds Rotate
   - Role: Creates base polygon geometry for slat

8. **Rotate** (`5a77f108-b5a1-429b-9d22-0a14d7945abd`) → `rotate_component`
   - Inputs: `Geometry` (from Polygon `b94e42e9...`), `Angle`, `Plane`
   - Output: `Geometry` (`3560b89d...`) → feeds Mirror
   - Role: Rotates polygon geometry

9. **Mirror** (`47650d42-5fa9-44b3-b970-9f28b94bb031`) → `mirror_component`
   - Inputs: `Geometry` (from Rotate `3560b89d...`), `Plane`
   - Output: `Geometry` (`db399c50...`) → feeds Deconstruct Brep
   - Role: Mirrors rotated geometry

10. **Deconstruct Brep** (`c78ea9c5-07c7-443b-b188-078a6056dae8`) → `deconstruct_brep_component`
    - Inputs: `Brep` (from Mirror `db399c50...`)
    - Output: `Edges` (`2ee35645...`) → feeds List Item
    - Role: Extracts edges from mirrored geometry

11. **List Item** (`d89d47e0-f858-44d9-8427-fdf2e3230954`) → `list_item_component`
    - Inputs: `List` (from Deconstruct Brep `Edges` `2ee35645...`), `Index` (0)
    - Output: `Item` (`8e8b33cf...`) → feeds Point On Curve
    - Role: Gets first edge from edges list

12. **Point On Curve** (`6ce8bcba-18ea-46fc-a145-b1c1b45c304f`) → `point_on_curve_component`
    - Inputs: `Curve` (from List Item `8e8b33cf...`, Container-level Source), `parameter` (0.5)
    - Output: `Point` → feeds downstream vector calculations
    - Role: Evaluates point on curve for normal calculation

13. **Area** (`16022012-569d-4c58-a081-6d57649a1720`) → `area_component`
    - Inputs: `Geometry`
    - Output: `Centroid` (`50d6fc68...`) → feeds Vector 2Pt
    - Role: Computes area centroid for vector calculation

14. **Vector 2Pt** (`1f794702-1a6b-441e-b41d-c4749b372177`) → `vector_2pt_component`
    - Inputs: `Point A` (from Area `Centroid` `50d6fc68...`), `Point B`
    - Output: `Vector` (`84214afe...`) → feeds Amplitude
    - Role: Creates vector from centroid to target point

15. **Amplitude** (`f54babb4-b955-42d1-aeb1-3b2192468fed`) → `amplitude_component`
    - Inputs: `Vector` (from Vector 2Pt `84214afe...`), `Amplitude`
    - Output: `Vector` → feeds downstream calculations
    - Role: Scales vector to specified amplitude

16. **Vector XYZ** (`0e4c5858-...`, `f5598672-...`) → `vector_xyz_component`
    - Inputs: `X component`, `Y component`, `Z component`
    - Output: `Vector` → feeds Move component `Motion` input
    - Role: Creates motion vector for geometry transformation

17. **Move** (`dfbbd4a2-021a-4c74-ac63-8939e6ac5429`, `ddb9e6ae-7d3e-41ae-8c75-fc726c984724`) → `move_component`
    - Inputs: `Geometry` (from Surface `8fec620f...`), `Motion` (from Vector XYZ/Amplitude)
    - Output: `Geometry`
    - Role: Moves geometry by motion vector

18. **Plane Normal** (`09db66ec-b6d3-4823-8cec-d459daf0aedc`) → `plane_normal_component`
    - Inputs: `Origin` (`34529a8c...`), `Z-Axis` (`e41d5eba...`)
    - Output: `Normal` → feeds Angle
    - Role: Extracts normal vector from plane for angle calculation

19. **Line** (`c7dba531-36f1-4a2d-8e0e-ed94b3873bba`) → `line_component`
    - Inputs: `Start Point` (`01fd4f89...`), `End Point` (`12d02e9b...`)
    - Output: `Line` (`9822511c...`) → feeds Divide Length
    - Role: Creates line for division

20. **Divide Length** (`c7b8773d-e1e0-4c31-9b7c-b8b54f9e40e0`) → `divide_length_component`
    - Inputs: `Curve` (from Line `9822511c...`), `Length` (0.2)
    - Output: `Points` → feeds Project
    - Role: Divides line into segments

21. **Project** (`9cd053c9-3dd2-432b-aa46-a29a4b05c339`) → `project_component`
    - Inputs: `Curve` (from Divide Length), `Brep` (`3d373d1a...`), `Direction`
    - Output: `Curve` → feeds downstream calculations
    - Role: Projects curve onto brep surface

22. **Evaluate Surface** (`d8de94de-c80f-4737-8059-5d259b78807c`) → `evaluate_surface_component`
    - Inputs: `Surface` (from Surface `3d373d1a...`), `Point` (from MD Slider `c4c92669...`)
    - Output: `Point` → feeds downstream calculations
    - Role: Evaluates point on surface at UV coordinates

23. **Angle** (`0d695e6b-3696-4337-bc80-d14104f8a59e`) → `angle_component`
    - Inputs: `Vector A`, `Vector B` (from Plane Normal and sun vector)
    - Output: `Angle` (`23900bd5...`) → feeds Degrees
    - Role: Computes angle between slat normal and sun vector in radians

24. **Degrees** (`fa0ba5a6-7dd9-43f4-a82a-cf02841d0f58`) → `degrees_component`
    - Inputs: `Radians` (from Angle `23900bd5...`)
    - Output: `Degrees` (`4d5670e5-1abc-417e-b9ce-3cf7878b98c2`) → **FINAL OUTPUT**
    - Role: Converts angle from radians to degrees for final display

---

## Notes

- **Input Resolution**: The evaluator resolves inputs in this order: (1) constant values from `persistent_values` or `values`, (2) source connections from other components, (3) external inputs from `external_inputs.json`, (4) default/placeholder values.

- **Multiple Sources**: Some inputs have multiple sources (e.g., Move `Motion` input). The evaluator combines them: if all sources are 3-element lists (vectors), they are summed; otherwise, a list of resolved values is returned.

- **Container-level Sources**: Some components (Surface, Point On Curve) have sources defined at the Container level rather than in `param_input` chunks. The evaluator handles these specially.

- **Simplified Implementations**: Many geometry components (Polygon, Rotate, Mirror, Move, etc.) use simplified implementations that return placeholders or pass-through values. Full geometry calculations would require Rhino geometry libraries.

- **Data Matching**: The evaluator does not implement GH's LONGEST/SHORTEST/XREF matching semantics. It uses the first available source or combines multiple sources as described above.

- **Graft/Flatten/Simplify**: These flags are not currently handled in the evaluator. All inputs are treated as flat lists or scalars.

- **Wrap Behavior**: List Item components do not implement wrap behavior. Out-of-range indices raise IndexError.

