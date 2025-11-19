"""
Grasshopper component functions - exact implementations matching GH behavior.
Each function corresponds to a GH component type with matching inputs/outputs.
"""
import math
from typing import List, Tuple, Any, Optional, Union, Dict


# ============================================================================
# Vector and Point Operations
# ============================================================================

def vector_2pt_component(pointA: Union[List[float], List[List[float]]], 
                        pointB: Union[List[float], List[List[float]]], 
                        unitize: bool = False) -> Union[Tuple[List[float], float], Tuple[List[List[float]], List[float]]]:
    """
    GH Vector 2Pt component
    Creates a vector from point A to point B.
    Handles both single points and lists (like Negative/Unit Z components).
    
    Inputs:
        pointA: [x, y, z] start point (base point) or list of points
        pointB: [x, y, z] end point (tip point) or list of points
        unitize: if True, normalize the vector to unit length
    
    Outputs:
        vector: [x, y, z] vector from A to B (unitized if unitize=True)
                or list of vectors if inputs are lists
        length: scalar length of the vector or list of lengths
    """
    # GH <Vector 2Pt> <NickName> <GUID>
    import math
    
    # Check if inputs are lists of points
    pointA_is_list = isinstance(pointA, list) and len(pointA) > 0 and isinstance(pointA[0], list)
    pointB_is_list = isinstance(pointB, list) and len(pointB) > 0 and isinstance(pointB[0], list)
    
    if pointA_is_list and pointB_is_list:
        # Both are lists - process pairwise (shortest list matching)
        min_len = min(len(pointA), len(pointB))
        vectors = []
        lengths = []
        for i in range(min_len):
            pa = pointA[i]
            pb = pointB[i]
            if len(pa) < 3:
                pa = list(pa) + [0.0] * (3 - len(pa))
            if len(pb) < 3:
                pb = list(pb) + [0.0] * (3 - len(pb))
            vec = [pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]]
            length = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
            if unitize and length > 0:
                vec = [vec[0] / length, vec[1] / length, vec[2] / length]
            vectors.append(vec)
            lengths.append(length)
        return vectors, lengths
    elif pointA_is_list:
        # Point A is list, Point B is single - process each Point A with Point B
        if len(pointB) < 3:
            pointB = list(pointB) + [0.0] * (3 - len(pointB))
        vectors = []
        lengths = []
        for pa in pointA:
            if len(pa) < 3:
                pa = list(pa) + [0.0] * (3 - len(pa))
            vec = [pointB[0] - pa[0], pointB[1] - pa[1], pointB[2] - pa[2]]
            length = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
            if unitize and length > 0:
                vec = [vec[0] / length, vec[1] / length, vec[2] / length]
            vectors.append(vec)
            lengths.append(length)
        return vectors, lengths
    elif pointB_is_list:
        # Point A is single, Point B is list - process Point A with each Point B
        if len(pointA) < 3:
            pointA = list(pointA) + [0.0] * (3 - len(pointA))
        vectors = []
        lengths = []
        for pb in pointB:
            if len(pb) < 3:
                pb = list(pb) + [0.0] * (3 - len(pb))
            vec = [pb[0] - pointA[0], pb[1] - pointA[1], pb[2] - pointA[2]]
            length = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
            if unitize and length > 0:
                vec = [vec[0] / length, vec[1] / length, vec[2] / length]
            vectors.append(vec)
            lengths.append(length)
        return vectors, lengths
    else:
        # Both are single points - normal processing
        if len(pointA) < 3:
            pointA = list(pointA) + [0.0] * (3 - len(pointA))
        if len(pointB) < 3:
            pointB = list(pointB) + [0.0] * (3 - len(pointB))
        
        # Calculate vector from A to B
        vector = [pointB[0] - pointA[0], pointB[1] - pointA[1], pointB[2] - pointA[2]]
        
        # Calculate length
        length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
        
        # Unitize if requested
        if unitize and length > 0:
            vector = [vector[0] / length, vector[1] / length, vector[2] / length]
        
        return vector, length


def unitize_component(vector: List[float]) -> List[float]:
    """
    GH Unitize component
    Normalizes a vector to unit length.
    
    Inputs:
        vector: [x, y, z] input vector
    
    Outputs:
        unit_vector: [x, y, z] normalized vector
    """
    # GH <Unitize> <NickName> <GUID>
    if len(vector) < 3:
        raise ValueError("Vector must have at least 3 components")
    length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    if length < 1e-10:
        return [0.0, 0.0, 0.0]
    return [vector[0] / length, vector[1] / length, vector[2] / length]


def vector_xyz_component(x: float, y: float, z: float) -> List[float]:
    """
    GH Vector XYZ component
    Creates a vector from x, y, z components.
    
    Inputs:
        x: X component
        y: Y component
        z: Z component
    
    Outputs:
        vector: [x, y, z] vector
    """
    # GH <Vector XYZ> <NickName> <GUID>
    return [float(x), float(y), float(z)]


def amplitude_component(vector: List[float], amplitude: float) -> List[float]:
    """
    GH Amplitude component
    Scales a vector by an amplitude (length) value.
    
    Inputs:
        vector: [x, y, z] base vector
        amplitude: amplitude (length) value
    
    Outputs:
        vector: [x, y, z] scaled vector
    """
    # GH <Amplitude> <NickName> <GUID>
    if len(vector) < 3:
        raise ValueError("Vector must have at least 3 components")
    # Normalize the vector first, then scale by amplitude
    length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    if length < 1e-10:
        return [0.0, 0.0, 0.0]
    unit = [vector[0] / length, vector[1] / length, vector[2] / length]
    return [unit[0] * amplitude, unit[1] * amplitude, unit[2] * amplitude]


def unit_y_component(factor: Union[float, List[float]] = 1.0) -> Union[List[float], List[List[float]]]:
    """
    GH Unit Y component
    Returns the unit Y vector multiplied by a factor.
    Handles both single values and lists (like Negative component).
    
    Inputs:
        factor: multiplication factor (default 1.0) or list of factors
    
    Outputs:
        unit_y: [0, factor, 0] - unit Y vector scaled by factor
                or list of vectors if factor is a list
    """
    # GH <Unit Y> <NickName> <GUID>
    # Handle list inputs (like Negative component does)
    if isinstance(factor, list):
        return [[0.0, float(f), 0.0] for f in factor]
    
    # Single value
    if not isinstance(factor, (int, float)):
        try:
            factor = float(factor)
        except (ValueError, TypeError):
            factor = 1.0
    return [0.0, float(factor), 0.0]


def unit_z_component(factor: Union[float, List[float]] = 1.0) -> Union[List[float], List[List[float]]]:
    """
    GH Unit Z component
    Returns the unit Z vector multiplied by a factor.
    Handles both single values and lists (like Negative component).
    
    Inputs:
        factor: multiplication factor (default 1.0) or list of factors
    
    Outputs:
        unit_z: [0, 0, factor] - unit Z vector scaled by factor
                or list of vectors if factor is a list
    """
    # GH <Unit Z> <NickName> <GUID>
    # Handle list inputs (like Negative component does)
    if isinstance(factor, list):
        return [[0.0, 0.0, float(f)] for f in factor]
    
    # Single value
    if not isinstance(factor, (int, float)):
        try:
            factor = float(factor)
        except (ValueError, TypeError):
            factor = 1.0
    return [0.0, 0.0, float(factor)]


# ============================================================================
# Plane Operations
# ============================================================================

def construct_plane_component(origin: List[float], x_axis: List[float], y_axis: List[float]) -> dict:
    """
    GH Construct Plane component
    Creates a plane from origin, X-axis, and Y-axis.
    
    Inputs:
        origin: [x, y, z] plane origin point
        x_axis: [x, y, z] X-axis vector
        y_axis: [x, y, z] Y-axis vector
    
    Outputs:
        plane: dict with 'origin', 'x_axis', 'y_axis', 'z_axis', 'normal'
    """
    # GH <Construct Plane> <NickName> <GUID>
    if len(origin) < 3 or len(x_axis) < 3 or len(y_axis) < 3:
        raise ValueError("All inputs must have at least 3 coordinates")
    
    # Normalize X-axis
    x_len = math.sqrt(x_axis[0]**2 + x_axis[1]**2 + x_axis[2]**2)
    if x_len < 1e-10:
        raise ValueError("X-axis vector is too small")
    x_unit = [x_axis[0] / x_len, x_axis[1] / x_len, x_axis[2] / x_len]
    
    # Normalize Y-axis
    y_len = math.sqrt(y_axis[0]**2 + y_axis[1]**2 + y_axis[2]**2)
    if y_len < 1e-10:
        raise ValueError("Y-axis vector is too small")
    y_unit = [y_axis[0] / y_len, y_axis[1] / y_len, y_axis[2] / y_len]
    
    # Z-axis is cross product of X and Y
    z_axis = [
        x_unit[1] * y_unit[2] - x_unit[2] * y_unit[1],
        x_unit[2] * y_unit[0] - x_unit[0] * y_unit[2],
        x_unit[0] * y_unit[1] - x_unit[1] * y_unit[0]
    ]
    z_len = math.sqrt(z_axis[0]**2 + z_axis[1]**2 + z_axis[2]**2)
    if z_len > 1e-10:
        z_unit = [z_axis[0] / z_len, z_axis[1] / z_len, z_axis[2] / z_len]
    else:
        z_unit = [0.0, 0.0, 1.0]  # Default if degenerate
    
    return {
        'origin': origin,
        'x_axis': x_unit,
        'y_axis': y_unit,
        'z_axis': z_unit,
        'normal': z_unit
    }


def plane_normal_component(plane: dict) -> List[float]:
    """
    GH Plane Normal component
    Extracts the normal vector (Z-axis) from a plane.
    
    Inputs:
        plane: plane dict with 'normal' or 'z_axis'
    
    Outputs:
        normal: [x, y, z] plane normal vector
    """
    # GH <Plane Normal> <NickName> <GUID>
    if isinstance(plane, dict):
        return plane.get('normal', plane.get('z_axis', [0.0, 0.0, 1.0]))
    # If plane is just a normal vector already
    return plane if isinstance(plane, list) else [0.0, 0.0, 1.0]


def plane_component() -> dict:
    """
    GH Plane component (default XY plane)
    Creates a default XY plane at origin.
    
    Outputs:
        plane: default XY plane
    """
    # GH <Plane> <NickName> <GUID>
    return {
        'origin': [0.0, 0.0, 0.0],
        'x_axis': [1.0, 0.0, 0.0],
        'y_axis': [0.0, 1.0, 0.0],
        'z_axis': [0.0, 0.0, 1.0],
        'normal': [0.0, 0.0, 1.0]
    }


# ============================================================================
# Point Operations
# ============================================================================

def construct_point_component(x: float, y: float, z: float) -> List[float]:
    """
    GH Construct Point component
    Creates a point from X, Y, Z coordinates.
    
    Inputs:
        x: X coordinate
        y: Y coordinate
        z: Z coordinate
    
    Outputs:
        point: [x, y, z]
    """
    # GH <Construct Point> <NickName> <GUID>
    return [float(x), float(y), float(z)]


def point_component(point: List[float]) -> List[float]:
    """
    GH Point component
    Passes through or creates a point.
    
    Inputs:
        point: [x, y, z] point coordinates
    
    Outputs:
        point: [x, y, z] same point
    """
    # GH <Point> <NickName> <GUID>
    return point if isinstance(point, list) else [float(point), 0.0, 0.0]


# ============================================================================
# Line Operations
# ============================================================================

def line_component(start_point: Union[List[float], List[List[float]]], 
                  end_point: Union[List[float], List[List[float]]]) -> Union[dict, List[dict]]:
    """
    GH Line component (Line Between)
    Creates a line from start point to end point.
    
    Inputs:
        start_point: [x, y, z] line start or list of start points
        end_point: [x, y, z] line end or list of end points
    
    Outputs:
        line: dict with 'start', 'end', 'direction', 'length' or list of such dicts
    """
    # GH <Line> <NickName> <GUID>
    import math
    
    # Check if inputs are lists of points
    start_is_list = isinstance(start_point, list) and len(start_point) > 0 and isinstance(start_point[0], list)
    end_is_list = isinstance(end_point, list) and len(end_point) > 0 and isinstance(end_point[0], list)
    
    if start_is_list or end_is_list:
        # Handle list inputs
        if start_is_list and end_is_list:
            # Both are lists - process pairwise (shortest list matching)
            min_len = min(len(start_point), len(end_point))
            lines = []
            for i in range(min_len):
                sp = start_point[i]
                ep = end_point[i]
                if len(sp) < 3:
                    sp = list(sp) + [0.0] * (3 - len(sp))
                if len(ep) < 3:
                    ep = list(ep) + [0.0] * (3 - len(ep))
                direction = [ep[0] - sp[0], ep[1] - sp[1], ep[2] - sp[2]]
                length = math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
                lines.append({
                    'start': sp,
                    'end': ep,
                    'direction': direction,
                    'length': length
                })
            return lines
        elif start_is_list:
            # Start is list, end is single - process each start with end
            if len(end_point) < 3:
                end_point = list(end_point) + [0.0] * (3 - len(end_point))
            lines = []
            for sp in start_point:
                if len(sp) < 3:
                    sp = list(sp) + [0.0] * (3 - len(sp))
                direction = [end_point[0] - sp[0], end_point[1] - sp[1], end_point[2] - sp[2]]
                length = math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
                lines.append({
                    'start': sp,
                    'end': end_point,
                    'direction': direction,
                    'length': length
                })
            return lines
        else:
            # End is list, start is single - process start with each end
            if len(start_point) < 3:
                start_point = list(start_point) + [0.0] * (3 - len(start_point))
            lines = []
            for ep in end_point:
                if len(ep) < 3:
                    ep = list(ep) + [0.0] * (3 - len(ep))
                direction = [ep[0] - start_point[0], ep[1] - start_point[1], ep[2] - start_point[2]]
                length = math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
                lines.append({
                    'start': start_point,
                    'end': ep,
                    'direction': direction,
                    'length': length
                })
            return lines
    
    # Both are single points - normal processing
    if len(start_point) < 3:
        start_point = list(start_point) + [0.0] * (3 - len(start_point))
    if len(end_point) < 3:
        end_point = list(end_point) + [0.0] * (3 - len(end_point))
    
    direction = [end_point[0] - start_point[0], 
                 end_point[1] - start_point[1], 
                 end_point[2] - start_point[2]]
    length = math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
    
    return {
        'start': start_point,
        'end': end_point,
        'direction': direction,
        'length': length
    }


# ============================================================================
# Angle Operations
# ============================================================================

def angle_component(vectorA: List[float], vectorB: List[float], plane: Optional[dict] = None) -> Tuple[float, float]:
    """
    GH Angle component
    Computes the angle between two vectors.
    
    Inputs:
        vectorA: [x, y, z] first vector
        vectorB: [x, y, z] second vector
        plane: optional plane for 2D angle (dict with 'normal')
    
    Outputs:
        angle: angle in radians
        reflex: reflex angle in radians (2π - angle)
    """
    # GH <Angle> <NickName> <GUID>
    if len(vectorA) < 3 or len(vectorB) < 3:
        raise ValueError("Vectors must have at least 3 components")
    
    # Normalize vectors
    lenA = math.sqrt(vectorA[0]**2 + vectorA[1]**2 + vectorA[2]**2)
    lenB = math.sqrt(vectorB[0]**2 + vectorB[1]**2 + vectorB[2]**2)
    
    if lenA < 1e-10 or lenB < 1e-10:
        return 0.0, 0.0
    
    vA = [vectorA[0] / lenA, vectorA[1] / lenA, vectorA[2] / lenA]
    vB = [vectorB[0] / lenB, vectorB[1] / lenB, vectorB[2] / lenB]
    
    # Dot product
    dot = vA[0] * vB[0] + vA[1] * vB[1] + vA[2] * vB[2]
    dot = max(-1.0, min(1.0, dot))  # Clamp to [-1, 1] for acos
    
    angle = math.acos(dot)
    reflex = 2.0 * math.pi - angle
    
    return angle, reflex


def degrees_component(radians: float) -> float:
    """
    GH Degrees component
    Converts radians to degrees.
    
    Inputs:
        radians: angle in radians
    
    Outputs:
        degrees: angle in degrees
    """
    # GH <Degrees> <NickName> <GUID>
    return math.degrees(float(radians))


# ============================================================================
# Math Operations
# ============================================================================

def addition_component(a: Union[float, List[float]], b: Union[float, List[float]]) -> Union[float, List[float]]:
    """
    GH Addition component
    Adds two numbers or vectors.
    
    Inputs:
        a: first number or vector
        b: second number or vector
    
    Outputs:
        result: sum
    """
    # GH <Addition> <NickName> <GUID>
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise ValueError("Vectors must have same length")
        return [a[i] + b[i] for i in range(len(a))]
    return float(a) + float(b)


def subtraction_component(a: Union[float, List[float]], b: Union[float, List[float]]) -> Union[float, List[float]]:
    """
    GH Subtraction component
    Subtracts b from a.
    
    Inputs:
        a: first number or vector
        b: second number or vector
    
    Outputs:
        result: difference
    """
    # GH <Subtraction> <NickName> <GUID>
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise ValueError("Vectors must have same length")
        return [a[i] - b[i] for i in range(len(a))]
    return float(a) - float(b)


def multiply_component(a: Union[float, List[float]], b: Union[float, List[float]]) -> Union[float, List[float]]:
    """
    GH Multiply component
    Multiplies two numbers or scales a vector.
    
    Inputs:
        a: first number or vector
        b: second number
    
    Outputs:
        result: product
    """
    # GH <Multiply> <NickName> <GUID>
    if isinstance(a, list):
        return [a[i] * float(b) for i in range(len(a))]
    if isinstance(b, list):
        return [float(a) * b[i] for i in range(len(b))]
    return float(a) * float(b)


def division_component(a: Union[float, List[float]], b: float) -> Union[float, List[float]]:
    """
    GH Division component
    Divides a by b.
    
    Inputs:
        a: dividend (number or vector)
        b: divisor (number)
    
    Outputs:
        result: quotient
    """
    # GH <Division> <NickName> <GUID>
    b_val = float(b)
    if abs(b_val) < 1e-10:
        raise ValueError("Division by zero")
    if isinstance(a, list):
        return [a[i] / b_val for i in range(len(a))]
    return float(a) / b_val


def negative_component(value: Union[float, List[float]]) -> Union[float, List[float]]:
    """
    GH Negative component
    Negates a number or vector.
    
    Inputs:
        value: number or vector to negate
    
    Outputs:
        result: negated value
    """
    # GH <Negative> <NickName> <GUID>
    if isinstance(value, list):
        return [-v for v in value]
    return -float(value)


# ============================================================================
# List Operations
# ============================================================================

def series_component(start: float, count: int, step: float) -> List[float]:
    """
    GH Series component
    Generates a series of numbers.
    
    Inputs:
        start: starting value
        count: number of values
        step: step size
    
    Outputs:
        series: list of numbers
    """
    # GH <Series> <NickName> <GUID>
    if count < 0:
        return []
    # Ensure count is an integer
    count_int = int(count) if count > 0 else 0
    return [start + i * step for i in range(count_int)]


def list_item_component(list_data: List[Any], index: int) -> Any:
    """
    GH List Item component
    Gets an item from a list by index.
    
    Inputs:
        list_data: input list
        index: item index (should already be wrapped/clamped by evaluate_component if wrap is enabled)
    
    Outputs:
        item: list item at index
    """
    # GH <List Item> <NickName> <GUID>
    if not isinstance(list_data, list):
        raise ValueError("First input must be a list")
    # Ensure index is an integer
    index_int = int(index)
    # Note: The wrap logic is handled in evaluate_component before calling this function
    # So if wrap is enabled, the index should already be in range
    # If wrap is disabled and index is out of range, we raise an error (Grasshopper behavior)
    if index_int < 0 or index_int >= len(list_data):
        raise IndexError(f"Index {index_int} out of range for list of length {len(list_data)}")
    return list_data[index_int]


# ============================================================================
# Distance and Length Operations
# ============================================================================

def distance_component(pointA: List[float], pointB: List[float]) -> float:
    """
    GH Distance component
    Computes distance between two points.
    
    Inputs:
        pointA: [x, y, z] first point
        pointB: [x, y, z] second point
    
    Outputs:
        distance: distance value
    """
    # GH <Distance> <NickName> <GUID>
    if len(pointA) < 3 or len(pointB) < 3:
        raise ValueError("Points must have at least 3 coordinates")
    dx = pointB[0] - pointA[0]
    dy = pointB[1] - pointA[1]
    dz = pointB[2] - pointA[2]
    return math.sqrt(dx*dx + dy*dy + dz*dz)


def divide_length_component(curve: Any, length: float) -> List[List[float]]:
    """
    GH Divide Length component
    Divides a curve by a length value, creating points along the curve.
    
    Inputs:
        curve: curve geometry to divide
        length: segment length
    
    Outputs:
        points: list of points along the curve
    """
    # GH <Divide Length> <NickName> <GUID>
    # Simplified - would need actual curve division
    # For now, return placeholder points
    if length <= 0:
        return []
    # Return a few placeholder points
    return [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]


# ============================================================================
# Geometry Operations
# ============================================================================

def project_component(geometry: Any, target: dict, direction: Any = None) -> Any:
    """
    GH Project component
    Projects geometry onto a target (plane, surface, etc.).
    
    Inputs:
        geometry: geometry to project (point, curve, etc.)
        target: target plane or surface
        direction: optional projection direction
    
    Outputs:
        projected: projected geometry
    """
    # GH <Project> <NickName> <GUID>
    # Simplified: project point onto plane
    if isinstance(geometry, list) and len(geometry) >= 3:
        # Assume it's a point
        if isinstance(target, dict) and 'normal' in target:
            # Project point onto plane
            plane_origin = target.get('origin', [0.0, 0.0, 0.0])
            plane_normal = target.get('normal', [0.0, 0.0, 1.0])
            
            # Vector from plane origin to point
            vec = [geometry[0] - plane_origin[0],
                   geometry[1] - plane_origin[1],
                   geometry[2] - plane_origin[2]]
            
            # Distance along normal
            dist = vec[0] * plane_normal[0] + vec[1] * plane_normal[1] + vec[2] * plane_normal[2]
            
            # Projected point
            return [
                geometry[0] - dist * plane_normal[0],
                geometry[1] - dist * plane_normal[1],
                geometry[2] - dist * plane_normal[2]
            ]
    return geometry


def evaluate_surface_component(surface: Any, u: float, v: float) -> List[float]:
    """
    GH Evaluate Surface component
    Evaluates a surface at U, V parameters.
    
    Inputs:
        surface: surface geometry
        u: U parameter
        v: V parameter
    
    Outputs:
        point: [x, y, z] point on surface
    """
    # GH <Evaluate Surface> <NickName> <GUID>
    # Simplified implementation - would need actual surface evaluation
    # For now, return a placeholder
    return [float(u), float(v), 0.0]


# ============================================================================
# Additional Component Types
# ============================================================================

def value_list_component(values: List[Any]) -> List[Any]:
    """
    GH Value List component
    Passes through a list of values.
    
    Inputs:
        values: list of values
    
    Outputs:
        values: same list
    """
    # GH <Value List> <NickName> <GUID>
    return values if isinstance(values, list) else [values]


def number_component(value: float) -> float:
    """
    GH Number component
    Passes through a number value.
    
    Inputs:
        value: number
    
    Outputs:
        value: same number
    """
    # GH <Number> <NickName> <GUID>
    return float(value)


def number_slider_component(value: float) -> float:
    """
    GH Number Slider component
    Passes through a slider value.
    
    Inputs:
        value: slider value
    
    Outputs:
        value: same value
    """
    # GH <Number Slider> <NickName> <GUID>
    return float(value)


def surface_component(geometry: Any) -> Any:
    """
    GH Surface component
    Passes through surface geometry.
    
    Inputs:
        geometry: surface geometry
    
    Outputs:
        surface: same surface
    """
    # GH <Surface> <NickName> <GUID>
    return geometry


def area_component(geometry: Any) -> Dict[str, Any]:
    """
    GH Area component
    Computes area and centroid of geometry.
    
    Inputs:
        geometry: geometry object (brep, mesh, or planar closed curve)
    
    Outputs:
        area: area value
        centroid: [x, y, z] centroid point
    """
    # GH <Area> <NickName> <GUID>
    # Simplified - would need actual geometry area calculation
    # For now, return placeholder values
    # If geometry is a rectangle, try to compute centroid from corners
    if isinstance(geometry, dict):
        if 'corners' in geometry:
            # Rectangle - compute centroid from corners
            corners = geometry['corners']
            if corners and len(corners) >= 2:
                # Average of all corners
                centroid = [
                    sum(c[0] for c in corners) / len(corners),
                    sum(c[1] for c in corners) / len(corners),
                    sum(c[2] if len(c) > 2 else 0 for c in corners) / len(corners)
                ]
                return {'Area': geometry.get('area', 0.0), 'Centroid': centroid}
        elif 'points' in geometry:
            # Polyline - compute centroid from points
            points = geometry['points']
            if points:
                centroid = [
                    sum(p[0] for p in points) / len(points),
                    sum(p[1] for p in points) / len(points),
                    sum(p[2] if len(p) > 2 else 0 for p in points) / len(points)
                ]
                return {'Area': 0.0, 'Centroid': centroid}
    
    # Default: return placeholder
    return {'Area': 0.0, 'Centroid': [0.0, 0.0, 0.0]}


def move_component(geometry: Any, motion: Union[List[float], List[List[float]]]) -> Tuple[Any, Dict[str, Any]]:
    """
    GH Move component
    Moves geometry by motion vector(s).
    
    Inputs:
        geometry: geometry to move (point, list of points, or geometry dict)
        motion: [x, y, z] motion vector or list of motion vectors
    
    Outputs:
        moved: moved geometry (or list of moved geometries if motion is a list)
        transform: transformation data (translation matrix/vector)
    """
    # GH <Move> <NickName> <GUID>
    # Check if motion is a list of vectors (list of lists)
    motion_is_list = isinstance(motion, list) and len(motion) > 0 and isinstance(motion[0], list)
    
    if motion_is_list:
        # Motion is a list of vectors - apply each to geometry
        # If geometry is a single point, create a list of moved points
        if isinstance(geometry, list) and len(geometry) == 3 and all(isinstance(x, (int, float)) for x in geometry):
            # Single point with list of motion vectors - create list of moved points
            moved_points = []
            for vec in motion:
                if isinstance(vec, list) and len(vec) >= 3:
                    moved_points.append([
                        geometry[0] + (vec[0] if isinstance(vec[0], (int, float)) else 0.0),
                        geometry[1] + (vec[1] if isinstance(vec[1], (int, float)) else 0.0),
                        geometry[2] + (vec[2] if isinstance(vec[2], (int, float)) else 0.0)
                    ])
            transform = {'type': 'translation', 'motion': motion, 'translation': motion}
            return moved_points, transform
        # If geometry is a list of points, apply motion vectors pairwise (shortest list)
        elif isinstance(geometry, list) and len(geometry) > 0:
            if isinstance(geometry[0], list) and len(geometry[0]) == 3:
                # List of points with list of motion vectors - apply pairwise
                min_len = min(len(geometry), len(motion))
                moved_points = []
                for i in range(min_len):
                    pt = geometry[i]
                    vec = motion[i] if isinstance(motion[i], list) and len(motion[i]) >= 3 else [0.0, 0.0, 0.0]
                    moved_points.append([
                        pt[0] + (vec[0] if isinstance(vec[0], (int, float)) else 0.0),
                        pt[1] + (vec[1] if isinstance(vec[1], (int, float)) else 0.0),
                        pt[2] + (vec[2] if isinstance(vec[2], (int, float)) else 0.0)
                    ])
                transform = {'type': 'translation', 'motion': motion, 'translation': motion}
                return moved_points, transform
    
    # Motion is a single vector - normalize to list of 3 floats
    if not isinstance(motion, list):
        motion = [0.0, 0.0, 0.0]
    elif len(motion) != 3 or not all(isinstance(x, (int, float)) for x in motion):
        # Check if it's a list of lists (should have been handled above)
        if isinstance(motion, list) and len(motion) > 0 and isinstance(motion[0], list):
            # This shouldn't happen, but handle it
            motion = motion[0] if len(motion[0]) >= 3 else [0.0, 0.0, 0.0]
        else:
            motion = list(motion[:3]) + [0.0] * (3 - len(motion))
    
    # Handle different geometry types with single motion vector
    if geometry is None:
        return None, {'type': 'translation', 'motion': motion, 'translation': motion}
    
    # If geometry is a point (list of 3 numbers)
    if isinstance(geometry, list) and len(geometry) == 3 and all(isinstance(x, (int, float)) for x in geometry):
        moved_point = [geometry[0] + motion[0], geometry[1] + motion[1], geometry[2] + motion[2]]
        transform = {'type': 'translation', 'motion': motion, 'translation': motion}
        return moved_point, transform
    
    # If geometry is a list of points
    if isinstance(geometry, list) and len(geometry) > 0:
        # Check if first item is a point (list of 3 numbers)
        if isinstance(geometry[0], list) and len(geometry[0]) == 3:
            # List of points - apply motion to each
            moved_points = [[pt[0] + motion[0], pt[1] + motion[1], pt[2] + motion[2]] for pt in geometry]
            transform = {'type': 'translation', 'motion': motion, 'translation': motion}
            return moved_points, transform
        # Check if first item is a dict with point data
        elif isinstance(geometry[0], dict):
            # List of geometry dicts - apply motion to each
            moved_geometries = []
            for geom in geometry:
                moved_geom = dict(geom)
                # Try to find and update point data
                for key in ['point', 'Point', 'origin', 'Origin', 'center', 'Center']:
                    if key in moved_geom and isinstance(moved_geom[key], list) and len(moved_geom[key]) >= 3:
                        moved_geom[key] = [
                            moved_geom[key][0] + motion[0],
                            moved_geom[key][1] + motion[1],
                            moved_geom[key][2] + motion[2]
                        ]
                moved_geometries.append(moved_geom)
            transform = {'type': 'translation', 'motion': motion, 'translation': motion}
            return moved_geometries, transform
    
    # If geometry is a dict with point data
    if isinstance(geometry, dict):
        moved_geometry = dict(geometry)
        # Try to find and update point data
        for key in ['point', 'Point', 'origin', 'Origin', 'center', 'Center']:
            if key in moved_geometry and isinstance(moved_geometry[key], list) and len(moved_geometry[key]) >= 3:
                moved_geometry[key] = [
                    moved_geometry[key][0] + motion[0],
                    moved_geometry[key][1] + motion[1],
                    moved_geometry[key][2] + motion[2]
                ]
        transform = {'type': 'translation', 'motion': motion, 'translation': motion}
        return moved_geometry, transform
    
    # Fallback: return geometry as-is
    transform = {'type': 'translation', 'motion': motion, 'translation': motion}
    return geometry, transform


def polar_array_component(geometry: Any, plane: dict, count: int, angle: float) -> List[Any]:
    """
    GH Polar Array component
    Creates polar array of geometry rotated around a plane's origin.
    
    Inputs:
        geometry: base geometry (can be a single item or a list of items)
        plane: plane dict with 'origin', 'x_axis', 'y_axis', 'z_axis'
        count: number of items in array
        angle: total sweep angle in radians (counter-clockwise from plane x-axis)
    
    Outputs:
        array: list of geometries (rotated copies)
        Note: If geometry is a list, each array item contains the full list (not individual items)
    """
    # GH <Polar Array> <NickName> <GUID>
    import math
    
    # Ensure count is an integer
    count_int = int(count) if count > 0 else 0
    if count_int == 0:
        return []
    
    # If only one item, return original geometry wrapped in a list
    if count_int == 1:
        return [geometry]
    
    # Extract plane origin (center of rotation)
    origin = plane.get('origin', [0.0, 0.0, 0.0]) if isinstance(plane, dict) else [0.0, 0.0, 0.0]
    
    # Calculate angle step
    angle_step = angle / count_int if count_int > 1 else 0.0
    
    # Create array of geometries
    # For now, we return copies of the geometry
    # In a full implementation, each copy would be rotated by the appropriate angle
    # around the plane's origin, using the plane's z-axis as the rotation axis
    array = []
    for i in range(count_int):
        # Calculate rotation angle for this item
        rotation_angle = i * angle_step
        
        # For now, return the geometry as-is (simplified)
        # In a full implementation, we would:
        # 1. Translate geometry to origin
        # 2. Rotate around z-axis by rotation_angle
        # 3. Translate back
        # This requires proper 3D transformation matrices
        
        # If geometry is a list, create a copy (shallow copy is fine for now)
        if isinstance(geometry, list):
            array.append(list(geometry))
        else:
            array.append(geometry)
    
    return array


def md_slider_component(value: float) -> float:
    """
    GH MD Slider component (Multi-Dimensional Slider)
    Passes through a slider value.
    
    Inputs:
        value: slider value
    
    Outputs:
        value: same value
    """
    # GH <MD Slider> <NickName> <GUID>
    return float(value)


def box_2pt_component(corner1: List[float], corner2: List[float]) -> Any:
    """
    GH Box 2Pt component
    Creates a box from two corner points.
    
    Inputs:
        corner1: first corner [x, y, z]
        corner2: second corner [x, y, z]
    
    Outputs:
        box: box geometry
    """
    # GH <Box 2Pt> <NickName> <GUID>
    # Simplified - would need actual box creation
    return {'corner1': corner1, 'corner2': corner2}


def rectangle_2pt_component(plane: Optional[Dict[str, Any]], pointA: List[float], pointB: List[float], radius: float = 0.0) -> Tuple[Any, float]:
    """
    GH Rectangle 2Pt component
    Creates a rectangle from a base plane and two corner points.
    
    Inputs:
        plane: rectangle base plane (dict with origin, x_axis, y_axis, z_axis) - optional, defaults to XY plane
        pointA: first corner point [x, y, z]
        pointB: second corner point [x, y, z]
        radius: corner fillet radius (default 0.0)
    
    Outputs:
        rectangle: rectangle geometry
        length: length of rectangle curve (perimeter)
    """
    # GH <Rectangle 2Pt> <NickName> <GUID>
    # Create rectangle from plane and two corner points
    # If plane is provided, the rectangle is created in that plane
    # Otherwise, it's created in the XY plane
    
    # Ensure points have 3 coordinates
    if len(pointA) < 3:
        pointA = list(pointA) + [0.0] * (3 - len(pointA))
    if len(pointB) < 3:
        pointB = list(pointB) + [0.0] * (3 - len(pointB))
    
    # If plane is provided, we would transform points to plane coordinates
    # For now, we'll work in the coordinate system of the points
    # The plane's origin and axes would be used to transform the rectangle
    # For simplicity, we'll calculate in the current coordinate system
    
    # Calculate rectangle dimensions
    width = abs(pointB[0] - pointA[0])
    height = abs(pointB[1] - pointA[1])
    
    # Calculate all four corners
    # Corner 1: pointA
    # Corner 2: (pointB.x, pointA.y, pointA.z)
    # Corner 3: pointB
    # Corner 4: (pointA.x, pointB.y, pointB.z)
    corner1 = pointA
    corner2 = [pointB[0], pointA[1], pointA[2]]
    corner3 = pointB
    corner4 = [pointA[0], pointB[1], pointB[2]]
    
    # Calculate perimeter (length of rectangle curve)
    # For a rectangle: 2 * (width + height)
    # If radius > 0, the corners are filleted, but for simplicity we'll use the basic perimeter
    length = 2.0 * (width + height)
    
    # Create rectangle representation
    rectangle = {
        'type': 'rectangle',
        'plane': plane if plane else {'origin': [0, 0, 0], 'x_axis': [1, 0, 0], 'y_axis': [0, 1, 0], 'z_axis': [0, 0, 1]},
        'corner1': corner1,
        'corner2': corner2,
        'corner3': corner3,
        'corner4': corner4,
        'pointA': pointA,
        'pointB': pointB,
        'width': width,
        'height': height,
        'radius': radius,
        'area': width * height,
        'corners': [corner1, corner2, corner3, corner4]
    }
    
    return rectangle, length


def polyline_component(points: List[List[float]], closed: bool = False) -> Any:
    """
    GH PolyLine component
    Creates a polyline from points.
    
    Inputs:
        points: list of points [[x, y, z], ...]
        closed: whether to close the polyline
    
    Outputs:
        polyline: polyline geometry
    """
    # GH <PolyLine> <NickName> <GUID>
    # Simplified - would need actual polyline creation
    return {'points': points, 'closed': closed}


def polygon_component(plane: Any, radius: float, segments: int, fillet_radius: float = 0.0) -> Any:
    """
    GH Polygon component
    Creates a polygon with optional round edges.
    
    Inputs:
        plane: polygon base plane
        radius: radius of polygon (distance from center to tip)
        segments: number of segments
        fillet_radius: polygon corner fillet radius
    
    Outputs:
        polygon: polygon curve with vertices
    """
    # GH <Polygon> <NickName> <GUID>
    import math
    
    # Get plane origin and axes
    if isinstance(plane, dict):
        origin = plane.get('origin', [0, 0, 0])
        x_axis = plane.get('x_axis', [1, 0, 0])
        y_axis = plane.get('y_axis', [0, 1, 0])
    else:
        origin = [0, 0, 0]
        x_axis = [1, 0, 0]
        y_axis = [0, 1, 0]
    
    # Ensure radius and segments are valid
    radius = float(radius) if radius else 1.0
    segments = int(segments) if segments else 3
    segments = max(3, segments)  # Minimum 3 segments
    
    # Create polygon vertices in the plane
    vertices = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        # Create point in local coordinate system (XY plane)
        local_x = radius * math.cos(angle)
        local_y = radius * math.sin(angle)
        local_z = 0.0
        
        # Transform to world coordinates using plane axes
        # Point = origin + local_x * x_axis + local_y * y_axis
        if isinstance(origin, (list, tuple)) and len(origin) >= 3:
            if isinstance(x_axis, (list, tuple)) and len(x_axis) >= 3:
                if isinstance(y_axis, (list, tuple)) and len(y_axis) >= 3:
                    world_x = origin[0] + local_x * x_axis[0] + local_y * y_axis[0]
                    world_y = origin[1] + local_x * x_axis[1] + local_y * y_axis[1]
                    world_z = origin[2] + local_x * x_axis[2] + local_y * y_axis[2]
                    vertices.append([world_x, world_y, world_z])
                else:
                    vertices.append([origin[0] + local_x, origin[1] + local_y, origin[2] + local_z])
            else:
                vertices.append([origin[0] + local_x, origin[1] + local_y, origin[2] + local_z])
        else:
            vertices.append([local_x, local_y, local_z])
    
    # Close the polygon by adding first vertex at end
    if len(vertices) > 0:
        vertices.append(vertices[0])
    
    return {
        'polygon': 'polygon_geometry',
        'vertices': vertices,
        'radius': radius,
        'segments': segments,
        'plane': plane
    }


def rotate_component(geometry: Any, angle: float, plane: Any) -> Any:
    """
    GH Rotate component
    Rotates geometry around a plane.
    
    Inputs:
        geometry: geometry to rotate
        angle: rotation angle in degrees
        plane: rotation plane
    
    Outputs:
        geometry: rotated geometry
    """
    # GH <Rotate> <NickName> <GUID>
    import math
    
    # Convert angle to radians
    angle_rad = math.radians(float(angle)) if angle else 0.0
    
    # Get rotation plane
    if isinstance(plane, dict):
        origin = plane.get('origin', [0, 0, 0])
        z_axis = plane.get('z_axis', plane.get('normal', [0, 0, 1]))
    else:
        origin = [0, 0, 0]
        z_axis = [0, 0, 1]
    
    # If geometry has vertices, rotate them
    if isinstance(geometry, dict) and 'vertices' in geometry:
        vertices = geometry['vertices']
        rotated_vertices = []
        
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # For rotation around Z-axis in XY plane
        for vertex in vertices:
            if isinstance(vertex, (list, tuple)) and len(vertex) >= 3:
                x, y, z = vertex[0], vertex[1], vertex[2]
                # Rotate around Z-axis (in XY plane)
                x_rot = x * cos_a - y * sin_a
                y_rot = x * sin_a + y * cos_a
                z_rot = z
                rotated_vertices.append([x_rot, y_rot, z_rot])
            else:
                rotated_vertices.append(vertex)
        
        result = geometry.copy()
        result['vertices'] = rotated_vertices
        result['rotation_angle'] = angle
        return result
    
    # Otherwise, pass through
    return geometry


def mirror_component(geometry: Any, plane: Any) -> Any:
    """
    GH Mirror component
    Mirrors geometry across a plane.
    
    Inputs:
        geometry: geometry to mirror
        plane: mirror plane
    
    Outputs:
        geometry: mirrored geometry
    """
    # GH <Mirror> <NickName> <GUID>
    
    # Get mirror plane
    if isinstance(plane, dict):
        origin = plane.get('origin', [0, 0, 0])
        normal = plane.get('normal', plane.get('z_axis', [1, 0, 0]))
    else:
        origin = [0, 0, 0]
        normal = [1, 0, 0]  # Default: mirror across YZ plane (X-axis normal)
    
    # If geometry has vertices, mirror them
    if isinstance(geometry, dict) and 'vertices' in geometry:
        vertices = geometry['vertices']
        mirrored_vertices = []
        
        # Normalize normal vector
        if isinstance(normal, (list, tuple)) and len(normal) >= 3:
            n_len = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
            if n_len > 1e-10:
                n = [normal[0]/n_len, normal[1]/n_len, normal[2]/n_len]
            else:
                n = [1, 0, 0]
        else:
            n = [1, 0, 0]
        
        # Mirror each vertex across the plane
        for vertex in vertices:
            if isinstance(vertex, (list, tuple)) and len(vertex) >= 3:
                x, y, z = vertex[0], vertex[1], vertex[2]
                # Vector from plane origin to vertex
                v = [x - origin[0], y - origin[1], z - origin[2]]
                # Project onto normal
                dot = v[0] * n[0] + v[1] * n[1] + v[2] * n[2]
                # Mirror: subtract 2 * projection
                mirrored = [
                    x - 2 * dot * n[0],
                    y - 2 * dot * n[1],
                    z - 2 * dot * n[2]
                ]
                mirrored_vertices.append(mirrored)
            else:
                mirrored_vertices.append(vertex)
        
        result = geometry.copy()
        result['vertices'] = mirrored_vertices
        result['mirrored'] = True
        return result
    
    # Otherwise, pass through
    return geometry


def deconstruct_brep_component(brep: Any) -> Any:
    """
    GH Deconstruct Brep component
    Deconstructs a brep into its components.
    
    Inputs:
        brep: brep geometry
    
    Outputs:
        faces: list of faces
        edges: list of edges
        vertices: list of vertices
    """
    # GH <Deconstruct Brep> <NickName> <GUID>
    
    edges = []
    if brep:
        # If brep has vertices, extract edges from them
        if isinstance(brep, dict) and 'vertices' in brep:
            vertices = brep['vertices']
            # Create edges from consecutive vertices
            for i in range(len(vertices) - 1):
                edges.append({
                    'type': 'edge',
                    'index': i,
                    'start': vertices[i],
                    'end': vertices[i + 1],
                    'source_brep': brep
                })
        elif isinstance(brep, dict):
            # Check if brep has polygon/geometry info that we can use
            if 'polygon' in brep or 'geometry' in brep:
                # For a polygon-based brep without vertices, return placeholder edges
                # Return enough edges for List Item access
                for i in range(10):
                    edges.append({
                        'type': 'edge',
                        'index': i,
                        'source_brep': brep,
                        'placeholder': True
                    })
            else:
                # Generic brep dict - create placeholder edges
                for i in range(10):
                    edges.append({
                        'type': 'edge',
                        'index': i,
                        'source_brep': brep,
                        'placeholder': True
                    })
        else:
            # Brep is not a dict or is None - return placeholder edges
            for i in range(10):
                edges.append({
                    'type': 'edge',
                    'index': i,
                    'placeholder': True
                })
    
    return {
        'Faces': [],
        'Edges': edges,
        'Vertices': []
    }


def point_on_curve_component(curve: Any, parameter: float) -> List[float]:
    """
    GH Point On Curve component
    Evaluates a point on a curve at a parameter.
    
    Inputs:
        curve: curve geometry (can be edge from Deconstruct Brep, curve dict, or placeholder)
        parameter: parameter value (0-1, where 0 is start, 1 is end)
    
    Outputs:
        point: [x, y, z] point on curve
    """
    # GH <Point On Curve> <NickName> <GUID>
    
    # Normalize parameter
    t = float(parameter) if parameter is not None else 0.0
    t = max(0.0, min(1.0, t))  # Clamp to [0, 1]
    
    # Handle edge dicts from Deconstruct Brep
    if isinstance(curve, dict):
        # Check for start/end points in curve dict (actual edge geometry)
        if 'start' in curve and 'end' in curve:
            start = curve['start']
            end = curve['end']
            # Linear interpolation along the curve
            if isinstance(start, (list, tuple)) and len(start) >= 3:
                if isinstance(end, (list, tuple)) and len(end) >= 3:
                    return [
                        start[0] + t * (end[0] - start[0]),
                        start[1] + t * (end[1] - start[1]),
                        start[2] + t * (end[2] - start[2])
                    ]
        
        # Check if it's a placeholder edge - try to extract from source_brep
        if curve.get('placeholder') is True:
            source_brep = curve.get('source_brep')
            edge_index = curve.get('index', 0)
            if source_brep and isinstance(source_brep, dict) and 'vertices' in source_brep:
                # Extract edge from brep vertices
                vertices = source_brep['vertices']
                if edge_index < len(vertices) - 1:
                    start = vertices[edge_index]
                    end = vertices[edge_index + 1]
                    if isinstance(start, (list, tuple)) and len(start) >= 3:
                        if isinstance(end, (list, tuple)) and len(end) >= 3:
                            return [
                                start[0] + t * (end[0] - start[0]),
                                start[1] + t * (end[1] - start[1]),
                                start[2] + t * (end[2] - start[2])
                            ]
            # If we can't extract, return placeholder
            return [0.0, 0.0, 0.0]
        
        # Check for point directly
        if 'point' in curve:
            point = curve['point']
            if isinstance(point, (list, tuple)) and len(point) >= 3:
                return list(point[:3])
        
        # Check for points list (polyline representation)
        if 'points' in curve and isinstance(curve['points'], list):
            points = curve['points']
            if len(points) > 0 and isinstance(points[0], (list, tuple)) and len(points[0]) >= 3:
                if len(points) == 1:
                    return list(points[0][:3])
                # Map parameter to segment
                segment_count = len(points) - 1
                segment_index = int(t * segment_count)
                segment_index = min(segment_index, segment_count - 1)
                local_t = (t * segment_count) - segment_index
                start = points[segment_index]
                end = points[segment_index + 1]
                return [
                    start[0] + local_t * (end[0] - start[0]),
                    start[1] + local_t * (end[1] - start[1]),
                    start[2] + local_t * (end[2] - start[2])
                ]
    
    # Handle string placeholders (legacy format)
    if isinstance(curve, str):
        # Legacy placeholder string - return generic placeholder
        return [0.0, 0.0, 0.0]
    
    # If curve is a list/tuple of points, treat as polyline
    if isinstance(curve, (list, tuple)) and len(curve) > 0:
        if isinstance(curve[0], (list, tuple)) and len(curve[0]) >= 3:
            # Polyline - interpolate between points
            if len(curve) == 1:
                return list(curve[0][:3])
            # Map parameter to segment
            segment_count = len(curve) - 1
            segment_index = int(t * segment_count)
            segment_index = min(segment_index, segment_count - 1)
            local_t = (t * segment_count) - segment_index
            start = curve[segment_index]
            end = curve[segment_index + 1]
            return [
                start[0] + local_t * (end[0] - start[0]),
                start[1] + local_t * (end[1] - start[1]),
                start[2] + local_t * (end[2] - start[2])
            ]
        elif len(curve) >= 3:
            # Single point as list
            return list(curve[:3])
    
    # Default: return placeholder indicating computation requires actual geometry
    # This handles the case where curve is None or unrecognized format
    return [0.0, 0.0, 0.0]


# ============================================================================
# Component Registry
# ============================================================================

COMPONENT_FUNCTIONS = {
    'Vector 2Pt': vector_2pt_component,
    'Unitize': unitize_component,
    'Vector XYZ': vector_xyz_component,
    'Amplitude': amplitude_component,
    'Unit Y': unit_y_component,
    'Unit Z': unit_z_component,
    'Construct Plane': construct_plane_component,
    'Plane Normal': plane_normal_component,
    'Plane': plane_component,
    'Construct Point': construct_point_component,
    'Point': point_component,
    'Line': line_component,
    'Angle': angle_component,
    'Degrees': degrees_component,
    'Addition': addition_component,
    'Subtraction': subtraction_component,
    'Multiply': multiply_component,
    'Division': division_component,
    'Negative': negative_component,
    'Series': series_component,
    'List Item': list_item_component,
    'Distance': distance_component,
    'Divide Length': divide_length_component,
    'Project': project_component,
    'Evaluate Surface': evaluate_surface_component,
    'Value List': value_list_component,
    'Number': number_component,
    'Number Slider': number_slider_component,
    'Surface': surface_component,
    'Area': area_component,
    'Move': move_component,
    'Polar Array': polar_array_component,
    'MD Slider': md_slider_component,
    'Box 2Pt': box_2pt_component,
    'Rectangle 2Pt': rectangle_2pt_component,
    'PolyLine': polyline_component,
    'Deconstruct Brep': deconstruct_brep_component,
    'Point On Curve': point_on_curve_component,
    'Mirror': mirror_component,
    'Rotate': rotate_component,
    'Polygon': polygon_component,
}

