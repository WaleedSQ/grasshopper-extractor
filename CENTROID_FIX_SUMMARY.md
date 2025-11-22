# Centroid Fix Summary

## Issue
Area component (GUID: `77f7eddb`) was outputting centroid `[0, 0, 0]` instead of the expected `[0, 0.5, 2.0]`.

## Root Cause Analysis

### Problem 1: Rotate Component Parameter Name Mismatch
**Issue**: The Rotate component implementation was using input parameter name `'Axis'` but the GHX file defines it as `'Plane'`.

**Impact**: The Plane input was not being resolved, receiving empty string `''` instead of plane data.

**Fix**: Changed parameter name from `'Axis'` to `'Plane'` in `evaluate_rotate()` function.

```python
# Before:
axis_tree = inputs.get('Axis', DataTree())

# After:
plane_tree = inputs.get('Plane', DataTree())
```

### Problem 2: Rotate Component Missing Box Geometry Support
**Issue**: The Rotate component only handled:
- Points (list `[x, y, z]`)
- Lines (dict with `'start'`, `'end'`)
- Rectangles (dict with `'corners'`)

But did NOT handle Box geometry (dict with `'corner_a'`, `'corner_b'`).

**Impact**: Box geometry was passed through unchanged (not rotated).

**Fix**: Added Box rotation support in `evaluate_rotate()`:

```python
elif 'corner_a' in geom and 'corner_b' in geom:
    # Box
    rotated = {
        'corner_a': rotate_point(geom['corner_a']),
        'corner_b': rotate_point(geom['corner_b']),
        'plane': geom.get('plane')
    }
    rotated_geoms.append(rotated)
```

### Problem 3: Area Component Missing Box Geometry Support ⭐ **PRIMARY CAUSE**
**Issue**: The Area component only handled rectangles (dict with `'corners'`) but NOT Box geometry (dict with `'corner_a'`, `'corner_b'`).

**Impact**: When receiving a Box from the Rotate component, it returned default centroid `[0, 0, 0]`.

**Fix**: Added Box centroid calculation in `evaluate_area()`:

```python
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
```

## Verification

### Input Box
- `corner_a`: `[0, -2, 7]`
- `corner_b`: `[0, 3, -3]`

### Rotate Input
- **Geometry**: Box from Box 2Pt component
- **Angle**: `0.0` radians (from external slider "Orientation")
- **Plane**: XY plane at origin (persistent data)

### Rotate Output
- Box with same corners (no rotation since angle = 0°)

### Area Output ✅
- **Centroid**: `[0.0, 0.5, 2.0]` ✅ **CORRECT**
- **Expected**: `[0, 0.5, 2.0]`

### Calculation Verification
```
Centroid = [(corner_a + corner_b) / 2]
         = [(0+0)/2, (-2+3)/2, (7+(-3))/2]
         = [0, 0.5, 2]  ✅
```

## Key Insights

1. **Angle Source**: The "Orientation" slider is set to `0.0` (not the persistent data `1.5707963267948966`), meaning NO rotation is applied.

2. **Expected Behavior**: The centroid `[0, 0.5, 2.0]` is the centroid of the UNROTATED box, which is correct given angle = 0°.

3. **Geometry Propagation**: The pipeline is:
   - Box 2Pt → Rotate (with angle=0°) → Area → Centroid
   - Box geometry must be supported throughout the chain.

## Files Modified

### `gh_components_rotatingslats.py`
1. **`evaluate_rotate()` (Line ~1221)**:
   - Changed parameter name `'Axis'` → `'Plane'`
   - Added Box geometry rotation support

2. **`evaluate_area()` (Line ~1045)**:
   - Added Box geometry support
   - Calculates centroid as midpoint of box diagonal
   - Calculates surface area as sum of 6 faces

## Result
✅ All 56 components evaluated successfully  
✅ Centroid now correctly outputs `[0.0, 0.5, 2.0]`  
✅ Matches expected Grasshopper output  

---

*Fixed: November 22, 2025*  
*Status: Complete ✅*

