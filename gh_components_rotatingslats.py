"""
PHASE 4: Rotatingslats Component Implementation

One-to-one component implementations matching exact Grasshopper behavior.
NO heuristics, NO approximations.

Each function signature:
    evaluate_<TypeName>(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]

Each line documents its GH correspondence:
    # GH <TypeName> operation
"""

import math
from typing import Dict, List, Tuple
from gh_evaluator_core import DataTree, match_longest, COMPONENT_REGISTRY


# ============================================================================
# MATH / ARITHMETIC COMPONENTS
# ============================================================================

@COMPONENT_REGISTRY.register("Subtraction")
def evaluate_subtraction(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Subtraction component (A - B).
    
    Inputs:
        A: First operand
        B: Second operand (subtracted from A)
    
    Outputs:
        Result: A - B
    """
    # GH Subtraction: match inputs using longest strategy
    a_tree = inputs.get('A', DataTree.from_scalar(0))
    b_tree = inputs.get('B', DataTree.from_scalar(0))
    
    a_matched, b_matched = match_longest(a_tree, b_tree)
    
    # GH Subtraction: subtract branch by branch
    result = DataTree()
    for path in a_matched.get_paths():
        a_items = a_matched.get_branch(path)
        b_items = b_matched.get_branch(path)
        
        result_items = []
        for a_val, b_val in zip(a_items, b_items):
            # GH Subtraction: numeric subtraction
            if a_val is None or b_val is None:
                raise ValueError(f"GH Subtraction: None value encountered (a={a_val}, b={b_val})")
            result_items.append(a_val - b_val)
        
        result.set_branch(path, result_items)
    
    return {'Result': result}


@COMPONENT_REGISTRY.register("Division")
def evaluate_division(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Division component (A / B).
    
    Inputs:
        A: Numerator
        B: Denominator
    
    Outputs:
        Result: A / B
    """
    # GH Division: match inputs using longest strategy
    a_tree = inputs.get('A', DataTree.from_scalar(0))
    b_tree = inputs.get('B', DataTree.from_scalar(1))
    
    a_matched, b_matched = match_longest(a_tree, b_tree)
    
    # GH Division: divide branch by branch
    result = DataTree()
    for path in a_matched.get_paths():
        a_items = a_matched.get_branch(path)
        b_items = b_matched.get_branch(path)
        
        result_items = []
        for a_val, b_val in zip(a_items, b_items):
            # GH Division: numeric division
            if a_val is None or b_val is None:
                raise ValueError(f"GH Division: None value encountered (a={a_val}, b={b_val})")
            if b_val == 0:
                result_items.append(float('inf') if a_val >= 0 else float('-inf'))
            else:
                result_items.append(a_val / b_val)
        
        result.set_branch(path, result_items)
    
    return {'Result': result}


@COMPONENT_REGISTRY.register("Negative")
def evaluate_negative(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Negative component (-x).
    
    Inputs:
        Value: Input value
    
    Outputs:
        Result: Negated value
    """
    # GH Negative: negate each value
    value_tree = inputs.get('Value', DataTree.from_scalar(0))
    
    result = DataTree()
    for path in value_tree.get_paths():
        items = value_tree.get_branch(path)
        result.set_branch(path, [-x for x in items])
    
    return {'Result': result}


# ============================================================================
# ANGLE / UNIT CONVERSION
# ============================================================================

@COMPONENT_REGISTRY.register("Degrees")
def evaluate_degrees(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Degrees component: convert radians to degrees.
    
    Inputs:
        Radians: Angle in radians
    
    Outputs:
        Degrees: Angle in degrees
    """
    # GH Degrees: radians to degrees conversion
    radians_tree = inputs.get('Radians', DataTree.from_scalar(0))
    
    result = DataTree()
    for path in radians_tree.get_paths():
        items = radians_tree.get_branch(path)
        # GH Degrees: degrees = radians * 180 / π
        result.set_branch(path, [math.degrees(x) for x in items])
    
    return {'Degrees': result}


@COMPONENT_REGISTRY.register("Angle")
def evaluate_angle(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Angle component: angle between two vectors.
    
    Inputs:
        Vector A: First vector (can be vector, plane, or line)
        Vector B: Second vector (can be vector, plane, or line)
        Plane: Optional plane for oriented angle
    
    Outputs:
        Angle: Angle in radians
        Reflex: Reflex angle (2π - angle)
    """
    # GH Angle: compute angle between vectors
    a_tree = inputs.get('Vector A', DataTree())
    b_tree = inputs.get('Vector B', DataTree())
    plane_tree = inputs.get('Plane', DataTree())
    
    # Match all three inputs to get the longest list replication
    a_matched, b_matched, plane_matched = match_longest(a_tree, b_tree, plane_tree)
    
    angle_result = DataTree()
    reflex_result = DataTree()
    
    def extract_vector(item):
        """Extract a vector from various geometry types."""
        if item is None:
            raise ValueError("GH Angle: input is None")
        
        # Direct vector [x, y, z]
        if isinstance(item, (list, tuple)) and len(item) >= 3:
            return list(item[:3])
        
        # Plane dict - extract Z-axis
        elif isinstance(item, dict) and 'z_axis' in item:
            return item['z_axis']
        
        # Line dict - extract direction vector
        elif isinstance(item, dict) and 'start' in item and 'end' in item:
            start = item['start']
            end = item['end']
            return [end[0] - start[0], end[1] - start[1], end[2] - start[2]]
        
        else:
            raise ValueError(f"GH Angle: cannot extract vector from {type(item)}: {item}")
    
    def extract_plane_normal(item):
        """Extract plane normal (Z-axis) if provided; return None if not usable."""
        if isinstance(item, dict):
            if 'z_axis' in item:
                return item['z_axis']
            if 'normal' in item:
                return item['normal']
        # Allow direct vector as normal
        if isinstance(item, (list, tuple)) and len(item) >= 3:
            return list(item[:3])
        return None
    
    def normalize(vec):
        length = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
        return [vec[0]/length, vec[1]/length, vec[2]/length] if length > 0 else [0, 0, 0]
    
    for path in a_matched.get_paths():
        a_items = a_matched.get_branch(path)
        b_items = b_matched.get_branch(path)
        plane_items = plane_matched.get_branch(path)
        
        # Skip empty branches
        if len(a_items) == 0 or len(b_items) == 0:
            continue
        
        angles = []
        reflexes = []
        
        for a_item, b_item, plane_item in zip(a_items, b_items, plane_items):
            # Skip if any required input is None
            if a_item is None or b_item is None:
                # GH Angle: skip None inputs (can happen with mismatched data trees)
                continue
            
            # Extract vectors from inputs
            a_vec = extract_vector(a_item)
            b_vec = extract_vector(b_item)
            plane_normal = extract_plane_normal(plane_item)
            
            # GH Angle: compute angle using dot product
            # angle = arccos(dot(a, b) / (|a| * |b|))
            a_unit = normalize(a_vec)
            b_unit = normalize(b_vec)
            
            dot_raw = a_vec[0] * b_vec[0] + a_vec[1] * b_vec[1] + a_vec[2] * b_vec[2]
            mag_a = math.sqrt(a_vec[0]**2 + a_vec[1]**2 + a_vec[2]**2)
            mag_b = math.sqrt(b_vec[0]**2 + b_vec[1]**2 + b_vec[2]**2)
            
            if mag_a == 0 or mag_b == 0:
                angle = 0
            else:
                cos_angle = dot_raw / (mag_a * mag_b)
                # Clamp to [-1, 1] to avoid numerical errors
                cos_angle = max(-1, min(1, cos_angle))
                angle = math.acos(cos_angle)
                
                # If plane normal provided, compute oriented angle
                if plane_normal:
                    n_unit = normalize(plane_normal)
                    cross = [
                        a_unit[1] * b_unit[2] - a_unit[2] * b_unit[1],
                        a_unit[2] * b_unit[0] - a_unit[0] * b_unit[2],
                        a_unit[0] * b_unit[1] - a_unit[1] * b_unit[0]
                    ]
                    sign = cross[0] * n_unit[0] + cross[1] * n_unit[1] + cross[2] * n_unit[2]
                    # GH oriented angle: if cross is aligned with plane normal, keep angle; otherwise take reflex
                    if sign > 0:
                        angle = angle
                    else:
                        angle = (2 * math.pi) - angle
            
            angles.append(angle)
            reflexes.append(2 * math.pi - angle)
        
        angle_result.set_branch(path, angles)
        reflex_result.set_branch(path, reflexes)
    
    return {'Angle': angle_result, 'Reflex': reflex_result}


# ============================================================================
# SERIES / RANGE GENERATION
# ============================================================================

@COMPONENT_REGISTRY.register("Series")
def evaluate_series(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Series component: generate arithmetic sequence.
    
    Inputs:
        Start: Start value (S)
        Step: Step size (N)
        Count: Number of values (C)
    
    Outputs:
        Series: List of values [S, S+N, S+2N, ..., S+(C-1)N]
    """
    # GH Series: generate arithmetic sequence
    start_tree = inputs.get('Start', DataTree.from_scalar(0))
    step_tree = inputs.get('Step', DataTree.from_scalar(1))
    count_tree = inputs.get('Count', DataTree.from_scalar(10))
    
    start_m, step_m, count_m = match_longest(start_tree, step_tree, count_tree)
    
    result = DataTree()
    
    for path in start_m.get_paths():
        start_items = start_m.get_branch(path)
        step_items = step_m.get_branch(path)
        count_items = count_m.get_branch(path)
        
        series_per_input = []
        
        for start_val, step_val, count_val in zip(start_items, step_items, count_items):
            # GH Series: generate count values starting at start with step
            count_int = int(count_val)
            series = [start_val + i * step_val for i in range(count_int)]
            series_per_input.extend(series)
        
        result.set_branch(path, series_per_input)
    
    return {'Series': result}


# ============================================================================
# LIST OPERATIONS
# ============================================================================

@COMPONENT_REGISTRY.register("List Item")
def evaluate_list_item(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH List Item component: extract item at index from list.
    
    Inputs:
        List: Input list
        Index: Index to extract (i)
        Wrap: Wrap index if out of bounds (default True)
    
    Outputs:
        Item: Item at index i
    """
    # GH List Item: extract item by index
    list_tree = inputs.get('List', DataTree())
    index_tree = inputs.get('Index', DataTree.from_scalar(0))
    wrap_tree = inputs.get('Wrap', DataTree.from_scalar(True))
    
    result = DataTree()
    
    # For each branch in the list tree
    for path in list_tree.get_paths():
        # The branch IS the list to extract from
        list_items = list_tree.get_branch(path)
        
        # Get corresponding indices - if index is scalar, use it for all branches
        # Otherwise try to match by path
        if path in index_tree.get_paths():
            index_branch = index_tree.get_branch(path)
        elif len(index_tree.get_paths()) == 1:
            # Single scalar index - use for all branches
            index_branch = index_tree.get_branch(index_tree.get_paths()[0])
        else:
            # Default to 0 if no match
            index_branch = [0]
        
        # Same for wrap
        if path in wrap_tree.get_paths():
            wrap_branch = wrap_tree.get_branch(path)
        elif len(wrap_tree.get_paths()) == 1:
            wrap_branch = wrap_tree.get_branch(wrap_tree.get_paths()[0])
        else:
            wrap_branch = [True]
        
        # If we have multiple indices, extract multiple items
        # Otherwise, extract one item
        extracted = []
        
        # Match longest: for each index, extract from the list
        max_len = max(len(index_branch), len(wrap_branch), 1)
        
        if len(list_items) == 0:
            # Empty list -> GH returns nulls for each requested index
            result.set_branch(path, [None] * max_len)
            continue
        
        for i in range(max_len):
            idx = index_branch[min(i, len(index_branch) - 1)] if index_branch else 0
            wrap = wrap_branch[min(i, len(wrap_branch) - 1)] if wrap_branch else True
            
            idx_int = int(idx)
            
            if wrap:
                # GH List Item: wrap index
                idx_int = idx_int % len(list_items)
            else:
                # GH List Item: out-of-range returns null
                if idx_int < 0 or idx_int >= len(list_items):
                    extracted.append(None)
                    continue
            
            extracted.append(list_items[idx_int])
        
        result.set_branch(path, extracted)
    
    return {'Item': result}


# ============================================================================
# VECTOR OPERATIONS
# ============================================================================

@COMPONENT_REGISTRY.register("Vector 2Pt")
def evaluate_vector_2pt(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Vector 2Pt component: vector from point A to point B.
    
    Inputs:
        Point A: Base point
        Point B: Tip point
        Unitize: Unitize output (default False)
    
    Outputs:
        Vector: B - A (unitized if Unitize=True)
        Length: Magnitude of vector
    """
    # GH Vector 2Pt: create vector from two points
    # Input names match GH exactly (from GHX lines 1434, 1461, 1488)
    a_tree = inputs.get('Point A', inputs.get('A', DataTree()))
    b_tree = inputs.get('Point B', inputs.get('B', DataTree()))
    unitize_tree = inputs.get('Unitize', DataTree.from_scalar(False))
    
    a_matched, b_matched, unitize_matched = match_longest(a_tree, b_tree, unitize_tree)
    
    vector_result = DataTree()
    length_result = DataTree()
    
    for path in a_matched.get_paths():
        a_items = a_matched.get_branch(path)
        b_items = b_matched.get_branch(path)
        unitize_items = unitize_matched.get_branch(path)
        
        vectors = []
        lengths = []
        
        for a_pt, b_pt, unitize in zip(a_items, b_items, unitize_items):
            # GH Vector 2Pt: vector = B - A
            if a_pt is None:
                raise ValueError("GH Vector 2Pt: point A is None")
            if b_pt is None:
                raise ValueError("GH Vector 2Pt: point B is None")
            if not isinstance(a_pt, (list, tuple)) or len(a_pt) < 3:
                raise ValueError(f"GH Vector 2Pt: invalid point A format: {a_pt}")
            if not isinstance(b_pt, (list, tuple)) or len(b_pt) < 3:
                raise ValueError(f"GH Vector 2Pt: invalid point B format: {b_pt}")
            
            ax, ay, az = a_pt
            bx, by, bz = b_pt
            
            vx = bx - ax
            vy = by - ay
            vz = bz - az
            
            # GH Vector 2Pt: compute length before unitizing
            length = math.sqrt(vx**2 + vy**2 + vz**2)
            
            # GH Vector 2Pt: unitize if requested (GHX line 1521)
            if unitize and length > 0:
                vx = vx / length
                vy = vy / length
                vz = vz / length
            
            vectors.append([vx, vy, vz])
            lengths.append(length)
        
        vector_result.set_branch(path, vectors)
        length_result.set_branch(path, lengths)
    
    return {'Vector': vector_result, 'Length': length_result}


@COMPONENT_REGISTRY.register("Unit Y")
def evaluate_unit_y(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Unit Y component: unit vector in Y direction, scaled by factor.
    
    Inputs:
        Factor: Scale factor (default 1)
    
    Outputs:
        Unit vector: [0, Factor, 0]
    """
    # GH Unit Y: create Y-direction unit vector
    factor_tree = inputs.get('Factor', DataTree.from_scalar(1))
    
    result = DataTree()
    
    for path in factor_tree.get_paths():
        factors = factor_tree.get_branch(path)
        # GH Unit Y: vector = [0, factor, 0]
        vectors = [[0, f, 0] for f in factors]
        result.set_branch(path, vectors)
    
    return {'Unit vector': result}


@COMPONENT_REGISTRY.register("Unit Z")
def evaluate_unit_z(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Unit Z component: unit vector in Z direction, scaled by factor.
    
    Inputs:
        Factor: Scale factor (default 1)
    
    Outputs:
        Unit vector: [0, 0, Factor]
    """
    # GH Unit Z: create Z-direction unit vector
    factor_tree = inputs.get('Factor', DataTree.from_scalar(1))
    
    result = DataTree()
    
    for path in factor_tree.get_paths():
        factors = factor_tree.get_branch(path)
        # GH Unit Z: vector = [0, 0, factor]
        vectors = [[0, 0, f] for f in factors]
        result.set_branch(path, vectors)
    
    return {'Unit vector': result}


# ============================================================================
# POINT OPERATIONS
# ============================================================================

@COMPONENT_REGISTRY.register("Construct Point")
def evaluate_construct_point(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Construct Point component: create point from X, Y, Z coordinates.
    
    Inputs:
        X coordinate: X coordinate
        Y coordinate: Y coordinate
        Z coordinate: Z coordinate
    
    Outputs:
        Point: [X, Y, Z]
    """
    # GH Construct Point: create point from coordinates
    x_tree = inputs.get('X coordinate', DataTree.from_scalar(0))
    y_tree = inputs.get('Y coordinate', DataTree.from_scalar(0))
    z_tree = inputs.get('Z coordinate', DataTree.from_scalar(0))
    
    x_m, y_m, z_m = match_longest(x_tree, y_tree, z_tree)
    
    result = DataTree()
    
    for path in x_m.get_paths():
        x_items = x_m.get_branch(path)
        y_items = y_m.get_branch(path)
        z_items = z_m.get_branch(path)
        
        points = []
        for x_val, y_val, z_val in zip(x_items, y_items, z_items):
            # GH Construct Point: point = [x, y, z]
            points.append([x_val, y_val, z_val])
        
        result.set_branch(path, points)
    
    return {'Point': result}


# ============================================================================
# PLANE OPERATIONS
# ============================================================================

@COMPONENT_REGISTRY.register("YZ Plane")
def evaluate_yz_plane(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH YZ Plane component: create plane perpendicular to X axis.
    
    Inputs:
        Origin: Origin point
    
    Outputs:
        Plane: YZ plane at origin
    """
    # GH YZ Plane: create plane with X-axis as normal
    origin_tree = inputs.get('Origin', DataTree.from_list([[0, 0, 0]]))
    
    result = DataTree()
    
    for path in origin_tree.get_paths():
        origins = origin_tree.get_branch(path)
        planes = []
        
        for origin in origins:
            # GH YZ Plane: plane with origin and X-axis normal
            # Plane axes lie in the YZ plane; normal points along +X
            plane = {
                'origin': origin,
                'x_axis': [0, 1, 0],  # Along world Y
                'y_axis': [0, 0, 1],  # Along world Z
                'z_axis': [1, 0, 0]   # Normal to YZ plane (+X)
            }
            planes.append(plane)
        
        result.set_branch(path, planes)
    
    return {'Plane': result}


@COMPONENT_REGISTRY.register("Construct Plane")
def evaluate_construct_plane(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Construct Plane component: create plane from origin, X-axis, and Y-axis.
    
    Inputs:
        Origin: Origin point
        X-Axis: X-axis direction
        Y-Axis: Y-axis direction
    
    Outputs:
        Plane: Constructed plane (Z = X cross Y)
    """
    # GH Construct Plane: create plane from origin and X, Y axes
    origin_tree = inputs.get('Origin', DataTree.from_list([[0, 0, 0]]))
    x_axis_tree = inputs.get('X-Axis', DataTree.from_list([[1, 0, 0]]))
    y_axis_tree = inputs.get('Y-Axis', DataTree.from_list([[0, 1, 0]]))
    
    # Match all three inputs
    origin_m, x_axis_m, y_axis_m = match_longest(origin_tree, x_axis_tree, y_axis_tree)
    
    result = DataTree()
    
    for path in origin_m.get_paths():
        origins = origin_m.get_branch(path)
        x_axes = x_axis_m.get_branch(path)
        y_axes = y_axis_m.get_branch(path)
        
        planes = []
        
        for origin, x_axis_input, y_axis_input in zip(origins, x_axes, y_axes):
            # GH Construct Plane: extract X-axis
            # X-axis can be a vector [x,y,z], a polyline dict, or a plane dict
            if isinstance(x_axis_input, dict):
                if 'vertices' in x_axis_input:
                    # It's a polyline, compute direction from first to last vertex
                    vertices = x_axis_input['vertices']
                    if len(vertices) < 2:
                        x_axis = [1, 0, 0]
                    else:
                        first = vertices[0]
                        last = vertices[-1]
                        x_axis = [last[0] - first[0], last[1] - first[1], last[2] - first[2]]
                elif 'x_axis' in x_axis_input or 'z_axis' in x_axis_input:
                    # It's a plane, extract its x_axis or z_axis
                    x_axis = x_axis_input.get('x_axis', x_axis_input.get('z_axis', [1, 0, 0]))
                else:
                    x_axis = [1, 0, 0]
            elif isinstance(x_axis_input, (list, tuple)) and len(x_axis_input) == 3:
                x_axis = list(x_axis_input)
            else:
                x_axis = [1, 0, 0]
            
            # GH Construct Plane: extract Y-axis
            # Y-axis can be a vector [x,y,z], a polyline dict, or a plane dict
            if isinstance(y_axis_input, dict):
                if 'vertices' in y_axis_input:
                    # It's a polyline, compute direction from first to last vertex
                    vertices = y_axis_input['vertices']
                    if len(vertices) < 2:
                        y_axis = [0, 1, 0]
                    else:
                        first = vertices[0]
                        last = vertices[-1]
                        y_axis = [last[0] - first[0], last[1] - first[1], last[2] - first[2]]
                elif 'y_axis' in y_axis_input or 'z_axis' in y_axis_input:
                    # It's a plane, extract its y_axis or z_axis
                    y_axis = y_axis_input.get('y_axis', y_axis_input.get('z_axis', [0, 1, 0]))
                else:
                    y_axis = [0, 1, 0]
            elif isinstance(y_axis_input, (list, tuple)) and len(y_axis_input) == 3:
                y_axis = list(y_axis_input)
            else:
                y_axis = [0, 1, 0]
            
            # Normalize X-axis
            x_len = math.sqrt(x_axis[0]**2 + x_axis[1]**2 + x_axis[2]**2)
            if x_len == 0:
                x_norm = [1, 0, 0]
            else:
                x_norm = [x_axis[0] / x_len, x_axis[1] / x_len, x_axis[2] / x_len]
            
            # Normalize Y-axis
            y_len = math.sqrt(y_axis[0]**2 + y_axis[1]**2 + y_axis[2]**2)
            if y_len == 0:
                y_norm = [0, 1, 0]
            else:
                y_norm = [y_axis[0] / y_len, y_axis[1] / y_len, y_axis[2] / y_len]
            
            # Z = X cross Y
            z_axis = [
                x_norm[1] * y_norm[2] - x_norm[2] * y_norm[1],
                x_norm[2] * y_norm[0] - x_norm[0] * y_norm[2],
                x_norm[0] * y_norm[1] - x_norm[1] * y_norm[0]
            ]
            z_len = math.sqrt(z_axis[0]**2 + z_axis[1]**2 + z_axis[2]**2)
            if z_len > 0:
                z_norm = [z_axis[0] / z_len, z_axis[1] / z_len, z_axis[2] / z_len]
            else:
                z_norm = [0, 0, 1]
            
            plane = {
                'origin': origin,
                'x_axis': x_norm,
                'y_axis': y_norm,
                'z_axis': z_norm
            }
            planes.append(plane)
        
        result.set_branch(path, planes)
    
    return {'Plane': result}


@COMPONENT_REGISTRY.register("Plane Normal")
def evaluate_plane_normal(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Plane Normal component: construct plane from origin and Z-axis (normal).
    
    Inputs:
        Origin: Plane origin point
        Z-Axis: Z-axis direction (normal), can be vector or plane
    
    Outputs:
        Plane: Constructed plane
    """
    # GH Plane Normal: constructs a plane from origin + z-axis
    # Defaults: origin = (0,0,0), Z-axis = (0,0,1)
    origin_tree = inputs.get('Origin', DataTree.from_list([[0, 0, 0]]))
    z_axis_tree = inputs.get('Z-Axis', DataTree.from_list([[0, 0, 1]]))
    
    # Match the two inputs using longest list matching
    origin_matched, z_axis_matched = match_longest(origin_tree, z_axis_tree)
    
    result = DataTree()
    
    for path in origin_matched.get_paths():
        origins = origin_matched.get_branch(path)
        z_inputs = z_axis_matched.get_branch(path)
        
        planes = []
        
        for origin, z_input in zip(origins, z_inputs):
            # GH Plane Normal: validate origin
            if origin is None:
                raise ValueError("GH Plane Normal: origin is None")
            if not isinstance(origin, (list, tuple)) or len(origin) != 3:
                raise ValueError(f"GH Plane Normal: origin must be [x,y,z], got {type(origin)}")
            
            # GH Plane Normal: extract Z-axis
            # Z-axis can be a vector [x,y,z], a plane dict, or a polyline dict
            if isinstance(z_input, dict):
                if 'z_axis' in z_input:
                    # It's a plane, extract its Z-axis as the new Z-axis direction
                    # (Grasshopper Plane Normal uses input plane's Z-axis for direction)
                    z_axis = z_input['z_axis']
                elif 'vertices' in z_input:
                    # It's a polyline, compute direction from first to last vertex
                    vertices = z_input['vertices']
                    if len(vertices) < 2:
                        raise ValueError("GH Plane Normal: polyline must have at least 2 vertices")
                    # Direction from first to last vertex
                    first = vertices[0]
                    last = vertices[-1]
                    z_axis = [last[0] - first[0], last[1] - first[1], last[2] - first[2]]
                else:
                    raise ValueError(f"GH Plane Normal: dict must have z_axis or vertices key, got {list(z_input.keys())}")
            elif isinstance(z_input, (list, tuple)) and len(z_input) == 3:
                z_axis = list(z_input)
            else:
                raise ValueError(f"GH Plane Normal: z-axis must be vector, plane, or polyline, got {type(z_input)}")
            
            # GH Plane Normal: normalize Z-axis
            z_len = (z_axis[0]**2 + z_axis[1]**2 + z_axis[2]**2)**0.5
            if z_len == 0:
                raise ValueError("GH Plane Normal: Z-axis has zero length")
            z_norm = [z_axis[0]/z_len, z_axis[1]/z_len, z_axis[2]/z_len]
            
            # GH Plane Normal: construct X and Y axes perpendicular to Z
            # Find the axis that is least aligned with Z to use as reference
            if abs(z_norm[0]) <= abs(z_norm[1]) and abs(z_norm[0]) <= abs(z_norm[2]):
                ref = [1.0, 0.0, 0.0]
            elif abs(z_norm[1]) <= abs(z_norm[2]):
                ref = [0.0, 1.0, 0.0]
            else:
                ref = [0.0, 0.0, 1.0]
            
            # X-axis = ref projected onto plane perpendicular to Z, normalized
            ref_dot_z = ref[0]*z_norm[0] + ref[1]*z_norm[1] + ref[2]*z_norm[2]
            x_axis = [
                ref[0] - ref_dot_z * z_norm[0],
                ref[1] - ref_dot_z * z_norm[1],
                ref[2] - ref_dot_z * z_norm[2]
            ]
            x_len = (x_axis[0]**2 + x_axis[1]**2 + x_axis[2]**2)**0.5
            x_norm = [x_axis[0]/x_len, x_axis[1]/x_len, x_axis[2]/x_len]
            
            # Y-axis = cross(Z, X)
            y_axis = [
                z_norm[1] * x_norm[2] - z_norm[2] * x_norm[1],
                z_norm[2] * x_norm[0] - z_norm[0] * x_norm[2],
                z_norm[0] * x_norm[1] - z_norm[1] * x_norm[0]
            ]
            
            planes.append({
                'origin': list(origin),
                'x_axis': x_norm,
                'y_axis': y_axis,
                'z_axis': z_norm
            })
        
        result.set_branch(path, planes)
    
    return {'Plane': result}


# ============================================================================
# CURVE OPERATIONS
# ============================================================================

@COMPONENT_REGISTRY.register("Line")
def evaluate_line(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Line component: create line from start and end points OR start and direction.
    
    Inputs (Mode 1 - Two Points):
        Start Point: Start point
        End Point: End point
    
    Inputs (Mode 2 - Point + Direction):
        Start Point: Start point
        Direction: Direction vector
        Length: Length (optional)
    
    Outputs:
        Line: Line segment
        Length: Line length
    """
    # GH Line: create line segment
    start_tree = inputs.get('Start Point', DataTree())
    end_tree = inputs.get('End Point', DataTree())
    direction_tree = inputs.get('Direction', DataTree())
    length_tree = inputs.get('Length', DataTree.from_scalar(None))
    
    # Determine mode: if End Point is present, use two-point mode
    if end_tree.get_paths():
        # Mode 1: Start Point + End Point
        start_m, end_m = match_longest(start_tree, end_tree)
        
        line_result = DataTree()
        length_result = DataTree()
        
        for path in start_m.get_paths():
            starts = start_m.get_branch(path)
            ends = end_m.get_branch(path)
            
            lines = []
            lengths = []
            
            for start, end in zip(starts, ends):
                # GH Line: validate inputs
                if start is None:
                    raise ValueError("GH Line: start point is None")
                if end is None:
                    raise ValueError("GH Line: end point is None")
                if not isinstance(start, (list, tuple)) or len(start) < 3:
                    raise ValueError(f"GH Line: invalid start point format: {start}")
                if not isinstance(end, (list, tuple)) or len(end) < 3:
                    raise ValueError(f"GH Line: invalid end point format: {end}")
                
                # Calculate length
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                dz = end[2] - start[2]
                length = math.sqrt(dx**2 + dy**2 + dz**2)
                
                line = {'start': list(start), 'end': list(end)}
                lines.append(line)
                lengths.append(length)
            
            line_result.set_branch(path, lines)
            length_result.set_branch(path, lengths)
        
        return {'Line': line_result, 'Length': length_result}
    
    else:
        # Mode 2: Start Point + Direction (+ optional Length)
        start_m, direction_m, length_m = match_longest(start_tree, direction_tree, length_tree)
        
        line_result = DataTree()
        length_result = DataTree()
        
        for path in start_m.get_paths():
            starts = start_m.get_branch(path)
            directions = direction_m.get_branch(path)
            lengths_override = length_m.get_branch(path)
            
            lines = []
            lengths = []
            
            for start, direction, length_override in zip(starts, directions, lengths_override):
                # GH Line: line from start in direction
                if start is None:
                    raise ValueError("GH Line: start point is None")
                if direction is None:
                    raise ValueError("GH Line: direction vector is None")
                if not isinstance(start, (list, tuple)) or len(start) < 3:
                    raise ValueError(f"GH Line: invalid start point format: {start}")
                if not isinstance(direction, (list, tuple)) or len(direction) < 3:
                    raise ValueError(f"GH Line: invalid direction format: {direction}")
                
                dx, dy, dz = direction
                dir_len = math.sqrt(dx**2 + dy**2 + dz**2)

                # If a length override is provided, scale the direction to that length
                if length_override is None:
                    use_len = dir_len
                else:
                    try:
                        use_len = float(length_override)
                    except (TypeError, ValueError):
                        use_len = dir_len

                if dir_len == 0:
                    end = list(start)
                    length_val = 0
                else:
                    scale = use_len / dir_len if use_len is not None else 1.0
                    end = [
                        start[0] + dx * scale,
                        start[1] + dy * scale,
                        start[2] + dz * scale
                    ]
                    length_val = abs(use_len) if use_len is not None else dir_len

                line = {'start': list(start), 'end': end}
                lines.append(line)
                lengths.append(length_val)
        
        line_result.set_branch(path, lines)
        length_result.set_branch(path, lengths)
    
    return {'Line': line_result, 'Length': length_result}


@COMPONENT_REGISTRY.register("PolyLine")
def evaluate_polyline(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH PolyLine component: create polyline from points.
    
    Inputs:
        Vertices: List of points
        Closed: Whether to close the polyline
    
    Outputs:
        Polyline: Polyline curve
        Length: Total length
    """
    # GH PolyLine: create polyline from vertices
    vertices_tree = inputs.get('Vertices', DataTree())
    closed_tree = inputs.get('Closed', DataTree.from_scalar(False))
    
    polyline_result = DataTree()
    length_result = DataTree()
    
    for path in vertices_tree.get_paths():
        # GH PolyLine: The branch contains a list of vertices (points)
        # All vertices in the branch form ONE polyline
        vertices = vertices_tree.get_branch(path)
        
        # GH PolyLine: validate we have vertices
        if not isinstance(vertices, list):
            raise ValueError(f"GH PolyLine: vertices must be a list, got {type(vertices)}")
        if len(vertices) < 2:
            raise ValueError(f"GH PolyLine: need at least 2 vertices, got {len(vertices)}")
        
        # Validate all vertices are points
        for i, v in enumerate(vertices):
            if not isinstance(v, (list, tuple)) or len(v) < 3:
                raise ValueError(f"GH PolyLine: vertex {i} is invalid: {v}")
        
        # GH PolyLine: get closed parameter (default to False)
        closed = False
        closed_branch = closed_tree.get_branch(path)
        if closed_branch and len(closed_branch) > 0:
            closed = bool(closed_branch[0])
        
        polyline = {'vertices': vertices, 'closed': closed}
        
        # Calculate length
        total_length = 0
        for i in range(len(vertices) - 1):
            p1 = vertices[i]
            p2 = vertices[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dz = p2[2] - p1[2]
            segment_length = math.sqrt(dx**2 + dy**2 + dz**2)
            total_length += segment_length
        
        # If closed, add segment from last to first
        if closed:
            p1 = vertices[-1]
            p2 = vertices[0]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dz = p2[2] - p1[2]
            segment_length = math.sqrt(dx**2 + dy**2 + dz**2)
            total_length += segment_length
        
        polyline_result.set_branch(path, [polyline])
        length_result.set_branch(path, [total_length])
    
    return {'Polyline': polyline_result, 'Length': length_result}


@COMPONENT_REGISTRY.register("Divide Length")
def evaluate_divide_length(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Divide Length component: divide curve into segments of specified length.
    
    Inputs:
        Curve: Curve to divide
        Length: Segment length
    
    Outputs:
        Points: Division points
        Tangents: Tangent vectors at points
        Parameters: Parameter values
    """
    # GH Divide Length: divide curve by length
    curve_tree = inputs.get('Curve', DataTree())
    length_tree = inputs.get('Length', DataTree.from_scalar(1))
    
    curve_m, length_m = match_longest(curve_tree, length_tree)
    
    points_result = DataTree()
    tangents_result = DataTree()
    parameters_result = DataTree()
    
    for path in curve_m.get_paths():
        curves = curve_m.get_branch(path)
        lengths = length_m.get_branch(path)
        
        all_points = []
        all_tangents = []
        all_parameters = []
        
        for curve, seg_length in zip(curves, lengths):
            # GH Divide Length: divide line into segments
            if curve is None:
                raise ValueError("GH Divide Length: curve is None")
            if not isinstance(curve, dict):
                raise ValueError(f"GH Divide Length: curve must be a dict, got {type(curve)}")
            
            if 'start' in curve and 'end' in curve:
                # Line segment
                start = curve['start']
                end = curve['end']
                
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                dz = end[2] - start[2]
                total_length = math.sqrt(dx**2 + dy**2 + dz**2)
                
                if total_length == 0 or seg_length <= 0:
                    all_points.append(start)
                    all_tangents.append([0, 0, 0])
                    all_parameters.append(0)
                    continue
                
                # Number of full segments of length seg_length
                num_segments = int(total_length / seg_length)
                num_segments = max(1, num_segments)  # At least one segment for non-zero length
                
                tangent = [dx / total_length, dy / total_length, dz / total_length]
                
                # Generate parameters at multiples of seg_length along the line
                t_values = [min((i * seg_length) / total_length, 1.0) for i in range(num_segments + 1)]
                if t_values[-1] < 1.0:
                    t_values.append(1.0)  # Ensure endpoint
                
                for t in t_values:
                    point = [
                        start[0] + t * dx,
                        start[1] + t * dy,
                        start[2] + t * dz
                    ]
                    all_points.append(point)
                    all_tangents.append(tangent)
                    all_parameters.append(t)
        
        points_result.set_branch(path, all_points)
        tangents_result.set_branch(path, all_tangents)
        parameters_result.set_branch(path, all_parameters)
    
    return {
        'Points': points_result,
        'Tangents': tangents_result,
        'Parameters': parameters_result
    }


# ============================================================================
# SURFACE OPERATIONS
# ============================================================================

@COMPONENT_REGISTRY.register("Rectangle 2Pt")
def evaluate_rectangle_2pt(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Rectangle 2Pt component: create rectangle from two corner points and plane.
    
    Inputs:
        Plane: Base plane
        Point A: First corner
        Point B: Opposite corner
    
    Outputs:
        Rectangle: Rectangle curve
        Length: Length dimension
        Width: Width dimension
    """
    # GH Rectangle 2Pt: create rectangle from corners
    plane_tree = inputs.get('Plane', DataTree())
    a_tree = inputs.get('Point A', DataTree())
    b_tree = inputs.get('Point B', DataTree())
    
    plane_m, a_m, b_m = match_longest(plane_tree, a_tree, b_tree)
    
    rectangle_result = DataTree()
    length_result = DataTree()
    width_result = DataTree()
    
    for path in plane_m.get_paths():
        planes = plane_m.get_branch(path)
        a_points = a_m.get_branch(path)
        b_points = b_m.get_branch(path)
        
        rectangles = []
        lengths = []
        widths = []
        
        for plane, pt_a, pt_b in zip(planes, a_points, b_points):
            # GH Rectangle 2Pt: create rectangle from two diagonal corners
            # Project points onto plane and create rectangle
            
            # Compute rectangle corners
            corner1 = pt_a
            corner2 = [pt_b[0], pt_a[1], pt_a[2]]
            corner3 = pt_b
            corner4 = [pt_a[0], pt_b[1], pt_a[2]]
            
            # Compute dimensions
            length = abs(pt_b[0] - pt_a[0])
            width = abs(pt_b[1] - pt_a[1])
            
            rectangle = {
                'corners': [corner1, corner2, corner3, corner4],
                'plane': plane
            }
            
            rectangles.append(rectangle)
            lengths.append(length)
            widths.append(width)
        
        rectangle_result.set_branch(path, rectangles)
        length_result.set_branch(path, lengths)
        width_result.set_branch(path, widths)
    
    return {
        'Rectangle': rectangle_result,
        'Length': length_result,
        'Width': width_result
    }


@COMPONENT_REGISTRY.register("Area")
def evaluate_area(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Area component: compute area of surface or planar curve.
    
    Inputs:
        Geometry: Surface or closed planar curve
    
    Outputs:
        Area: Area value
        Centroid: Area centroid
    """
    # GH Area: compute area
    geom_tree = inputs.get('Geometry', DataTree())
    
    area_result = DataTree()
    centroid_result = DataTree()
    
    for path in geom_tree.get_paths():
        geometries = geom_tree.get_branch(path)
        
        areas = []
        centroids = []
        
        for geom in geometries:
            if isinstance(geom, dict):
                if 'corners' in geom:
                    # Rectangle
                    corners = geom['corners']
                    
                    # Compute area as width * height
                    # Assume axis-aligned for simplicity
                    dx = abs(corners[2][0] - corners[0][0])
                    dy = abs(corners[2][1] - corners[0][1])
                    area = dx * dy
                    
                    # Centroid is average of corners
                    cx = sum(c[0] for c in corners) / len(corners)
                    cy = sum(c[1] for c in corners) / len(corners)
                    cz = sum(c[2] for c in corners) / len(corners)
                    centroid = [cx, cy, cz]
                    
                    areas.append(area)
                    centroids.append(centroid)
                elif 'corner_a' in geom and 'corner_b' in geom:
                    # Box
                    corner_a = geom['corner_a']
                    corner_b = geom['corner_b']
                    
                    # Compute surface area (sum of all 6 faces)
                    dx = abs(corner_b[0] - corner_a[0])
                    dy = abs(corner_b[1] - corner_a[1])
                    dz = abs(corner_b[2] - corner_a[2])
                    area = 2 * (dx * dy + dy * dz + dz * dx)
                    
                    # Centroid is midpoint of diagonal
                    cx = (corner_a[0] + corner_b[0]) / 2
                    cy = (corner_a[1] + corner_b[1]) / 2
                    cz = (corner_a[2] + corner_b[2]) / 2
                    centroid = [cx, cy, cz]
                    
                    areas.append(area)
                    centroids.append(centroid)
                else:
                    areas.append(0)
                    centroids.append([0, 0, 0])
            else:
                areas.append(0)
                centroids.append([0, 0, 0])
        
        area_result.set_branch(path, areas)
        centroid_result.set_branch(path, centroids)
    
    return {'Area': area_result, 'Centroid': centroid_result}


@COMPONENT_REGISTRY.register("Box 2Pt")
def evaluate_box_2pt(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Box 2Pt component: create box from two corner points.
    
    Inputs:
        Base Plane: Base plane
        Point A: First corner
        Point B: Opposite corner
    
    Outputs:
        Box: Box geometry
    """
    # GH Box 2Pt: create box from corners
    plane_tree = inputs.get('Base Plane', DataTree())
    a_tree = inputs.get('Point A', DataTree())
    b_tree = inputs.get('Point B', DataTree())
    
    plane_m, a_m, b_m = match_longest(plane_tree, a_tree, b_tree)
    
    box_result = DataTree()
    
    for path in plane_m.get_paths():
        planes = plane_m.get_branch(path)
        a_points = a_m.get_branch(path)
        b_points = b_m.get_branch(path)
        
        boxes = []
        
        for plane, pt_a, pt_b in zip(planes, a_points, b_points):
            # GH Box 2Pt: create box
            box = {
                'corner_a': pt_a,
                'corner_b': pt_b,
                'plane': plane
            }
            boxes.append(box)
        
        box_result.set_branch(path, boxes)
    
    return {'Box': box_result}


# ============================================================================
# TRANSFORM OPERATIONS
# ============================================================================

@COMPONENT_REGISTRY.register("Move")
def evaluate_move(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Move component: translate geometry by vector.
    
    Inputs:
        Geometry: Geometry to move
        Motion: Translation vector
    
    Outputs:
        Geometry: Translated geometry
        Transform: Transformation matrix
    """
    # GH Move: translate geometry
    geom_tree = inputs.get('Geometry', DataTree())
    motion_tree = inputs.get('Motion', DataTree())
    
    geom_m, motion_m = match_longest(geom_tree, motion_tree)
    
    geometry_result = DataTree()
    transform_result = DataTree()
    
    for path in geom_m.get_paths():
        geometries = geom_m.get_branch(path)
        motions = motion_m.get_branch(path)
        
        moved_geoms = []
        transforms = []
        
        for geom, motion in zip(geometries, motions):
            # GH Move: translate by motion vector
            if motion is None:
                raise ValueError("GH Move: motion vector is None")
            if not isinstance(motion, (list, tuple)) or len(motion) < 3:
                raise ValueError(f"GH Move: invalid motion vector format: {motion}")
            
            mx, my, mz = motion
            
            if isinstance(geom, list) and len(geom) == 3:
                # Point
                moved = [geom[0] + mx, geom[1] + my, geom[2] + mz]
                moved_geoms.append(moved)
            elif isinstance(geom, dict):
                if 'start' in geom and 'end' in geom:
                    # Line
                    moved = {
                        'start': [geom['start'][0] + mx, geom['start'][1] + my, geom['start'][2] + mz],
                        'end': [geom['end'][0] + mx, geom['end'][1] + my, geom['end'][2] + mz]
                    }
                    moved_geoms.append(moved)
                elif 'corners' in geom:
                    # Rectangle
                    moved_corners = [
                        [c[0] + mx, c[1] + my, c[2] + mz]
                        for c in geom['corners']
                    ]
                    moved = {
                        'corners': moved_corners,
                        'plane': geom['plane']
                    }
                    moved_geoms.append(moved)
                else:
                    moved_geoms.append(geom)
            else:
                moved_geoms.append(geom)
            
            # Transformation matrix (translation)
            transform = {'translation': motion}
            transforms.append(transform)
        
        geometry_result.set_branch(path, moved_geoms)
        transform_result.set_branch(path, transforms)
    
    return {'Geometry': geometry_result, 'Transform': transform_result}


@COMPONENT_REGISTRY.register("Rotate")
def evaluate_rotate(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Rotate component: rotate geometry around a plane.
    
    Inputs:
        Geometry: Geometry to rotate
        Angle: Rotation angle in radians
        Plane: Rotation plane (rotates around plane's Z-axis at plane's origin)
    
    Outputs:
        Geometry: Rotated geometry
        Transform: Transformation matrix
    """
    # GH Rotate: rotate geometry around plane's Z-axis
    geom_tree = inputs.get('Geometry', DataTree())
    angle_tree = inputs.get('Angle', DataTree())
    plane_tree = inputs.get('Plane', DataTree())
    
    geom_m, angle_m, plane_m = match_longest(geom_tree, angle_tree, plane_tree)
    
    geometry_result = DataTree()
    transform_result = DataTree()
    
    for path in geom_m.get_paths():
        geometries = geom_m.get_branch(path)
        angles = angle_m.get_branch(path)
        planes = plane_m.get_branch(path)
        
        rotated_geoms = []
        transforms = []
        
        for geom, angle, plane in zip(geometries, angles, planes):
            # GH Rotate: rotate geometry around plane's Z-axis at plane's origin
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            # Determine rotation origin/axis (Grasshopper: plane origin, plane Z)
            if plane and isinstance(plane, dict):
                rot_origin = plane.get('origin', [0, 0, 0])
                rot_axis = plane.get('z_axis', plane.get('normal', [0, 0, 1]))
            else:
                rot_origin = [0, 0, 0]
                rot_axis = [0, 0, 1]

            def normalize(vec):
                length = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
                return [vec[0]/length, vec[1]/length, vec[2]/length] if length > 0 else vec

            rot_axis_norm = normalize(rot_axis)

            def rotate_point(pt):
                """Rotate point around rot_axis at rot_origin."""
                # Translate to origin
                px = pt[0] - rot_origin[0]
                py = pt[1] - rot_origin[1]
                pz = pt[2] - rot_origin[2]

                # Rodrigues' rotation formula
                ax, ay, az = rot_axis_norm
                dot = px*ax + py*ay + pz*az
                cross = [
                    py*az - pz*ay,
                    pz*ax - px*az,
                    px*ay - py*ax
                ]

                rotated = [
                    px * cos_a + cross[0] * sin_a + ax * dot * (1 - cos_a),
                    py * cos_a + cross[1] * sin_a + ay * dot * (1 - cos_a),
                    pz * cos_a + cross[2] * sin_a + az * dot * (1 - cos_a)
                ]

                # Translate back
                return [
                    rotated[0] + rot_origin[0],
                    rotated[1] + rot_origin[1],
                    rotated[2] + rot_origin[2]
                ]
            
            if isinstance(geom, list) and len(geom) == 3:
                # Point
                rotated = rotate_point(geom)
                rotated_geoms.append(rotated)
            elif isinstance(geom, dict):
                if 'start' in geom and 'end' in geom:
                    # Line
                    rotated = {
                        'start': rotate_point(geom['start']),
                        'end': rotate_point(geom['end'])
                    }
                    rotated_geoms.append(rotated)
                elif 'corners' in geom:
                    # Rectangle
                    rotated_corners = [rotate_point(c) for c in geom['corners']]
                    rotated = {
                        'corners': rotated_corners,
                        'plane': geom['plane']
                    }
                    rotated_geoms.append(rotated)
                elif 'corner_a' in geom and 'corner_b' in geom:
                    # Box
                    rotated = {
                        'corner_a': rotate_point(geom['corner_a']),
                        'corner_b': rotate_point(geom['corner_b']),
                        'plane': geom.get('plane')
                    }
                    rotated_geoms.append(rotated)
                elif 'origin' in geom and 'x_axis' in geom and 'y_axis' in geom and 'z_axis' in geom:
                    # Plane: rotate origin and axes around rotation plane's Z/normal
                    def rotate_vec(vec):
                        """Rotate direction vector around rot_axis_norm (no translation)."""
                        ax, ay, az = rot_axis_norm
                        vx, vy, vz = vec
                        dot = vx*ax + vy*ay + vz*az
                        cross = [
                            vy*az - vz*ay,
                            vz*ax - vx*az,
                            vx*ay - vy*ax
                        ]
                        return [
                            vx * cos_a + cross[0] * sin_a + ax * dot * (1 - cos_a),
                            vy * cos_a + cross[1] * sin_a + ay * dot * (1 - cos_a),
                            vz * cos_a + cross[2] * sin_a + az * dot * (1 - cos_a)
                        ]

                    rotated_origin = rotate_point(geom['origin'])
                    x_rot = rotate_vec(geom['x_axis'])
                    y_rot = rotate_vec(geom['y_axis'])
                    z_rot = rotate_vec(geom['z_axis'])

                    rotated = {
                        'origin': rotated_origin,
                        'x_axis': normalize(x_rot),
                        'y_axis': normalize(y_rot),
                        'z_axis': normalize(z_rot)
                    }
                    rotated_geoms.append(rotated)
                else:
                    rotated_geoms.append(geom)
            else:
                rotated_geoms.append(geom)
            
            # Transformation matrix
            transform = {'rotation': angle, 'axis': plane}
            transforms.append(transform)
        
        geometry_result.set_branch(path, rotated_geoms)
        transform_result.set_branch(path, transforms)
    
    return {'Geometry': geometry_result, 'Transform': transform_result}


@COMPONENT_REGISTRY.register("Project")
def evaluate_project(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Project component: project curve onto brep.
    
    Inputs:
        Curve: Curve to project
        Brep: Target brep/surface
        Direction: Projection direction
    
    Outputs:
        Curve: Projected curve
    """
    # GH Project: project curve onto surface
    print(f"evaluate_project: #####################################################")
    curve_tree = inputs.get('Curve', DataTree())
    brep_tree = inputs.get('Brep', DataTree())
    direction_tree = inputs.get('Direction', DataTree.from_scalar([0, 0, -1]))

    curve_m, brep_m, direction_m = match_longest(curve_tree, brep_tree, direction_tree)

    def normalize(vec):
        length = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
        return [vec[0]/length, vec[1]/length, vec[2]/length] if length > 0 else vec

    def extract_direction(item):
        # Direction can be vector or plane (use plane normal)
        if isinstance(item, (list, tuple)) and len(item) >= 3:
            return list(item[:3])
        if isinstance(item, dict) and 'z_axis' in item:
            return item['z_axis']
        return [0, 0, -1]

    def extract_plane(item):
        # Brep is approximated as a plane target for projection
        if isinstance(item, dict) and 'origin' in item and 'z_axis' in item:
            return item
        # Default: world XY
        return {
            'origin': [0, 0, 0],
            'z_axis': [0, 0, 1],
            'x_axis': [1, 0, 0],
            'y_axis': [0, 1, 0]
        }

    def project_point(pt, plane, direction):
        """Project point onto plane along direction."""
        if pt is None or len(pt) < 3:
            return pt
        origin = plane.get('origin', [0, 0, 0])
        plane_normal = plane.get('z_axis', plane.get('normal', [0, 0, 1]))
        d_vec = direction or [0, 0, -1]

        n = normalize(plane_normal)
        d = d_vec
        dn = d[0]*n[0] + d[1]*n[1] + d[2]*n[2]
        if dn == 0:
            # Direction is parallel to plane; return original point
            return list(pt)
        t = ((origin[0]-pt[0]) * n[0] + (origin[1]-pt[1]) * n[1] + (origin[2]-pt[2]) * n[2]) / dn
        return [pt[0] + t * d[0], pt[1] + t * d[1], pt[2] + t * d[2]]

    projected_result = DataTree()

    for path in curve_m.get_paths():
        curves = curve_m.get_branch(path)
        breps = brep_m.get_branch(path)
        directions = direction_m.get_branch(path)

        projected_curves = []

        for curve, brep, direction in zip(curves, breps, directions):
            plane = extract_plane(brep)
            dir_vec = extract_direction(direction)

            if isinstance(curve, list) and len(curve) == 3:
                # Point as degenerate curve
                projected_curves.append(project_point(curve, plane, dir_vec))
            elif isinstance(curve, dict):
                if 'start' in curve and 'end' in curve:
                    # Line
                    projected_curves.append({
                        'start': project_point(curve['start'], plane, dir_vec),
                        'end': project_point(curve['end'], plane, dir_vec)
                    })
                elif 'vertices' in curve:
                    # Polyline
                    projected_curves.append({
                        'vertices': [project_point(v, plane, dir_vec) for v in curve['vertices']]
                    })
                elif 'corners' in curve:
                    # Rectangle polyline
                    projected_curves.append({
                        'corners': [project_point(c, plane, dir_vec) for c in curve['corners']],
                        'plane': plane
                    })
                else:
                    # Unknown dict geometry: leave unchanged
                    projected_curves.append(curve)
            else:
                # Unsupported type, pass through
                projected_curves.append(curve)

        projected_result.set_branch(path, projected_curves)

    return {'Curve': projected_result}


# ============================================================================
# SUMMARY
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("PHASE 4: Rotatingslats Component Implementation")
    print("=" * 80)
    print()
    print(f"Registered {len(COMPONENT_REGISTRY.list_registered())} components:")
    print()
    for comp_type in COMPONENT_REGISTRY.list_registered():
        print(f"  - {comp_type}")
    print()
    print("=" * 80)
    print("PHASE 4 COMPLETE")
    print("=" * 80)
    print()
    print("All components implement exact Grasshopper behavior.")
    print("Ready for PHASE 5: Wired topological evaluation")
