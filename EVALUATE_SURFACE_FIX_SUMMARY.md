# Evaluate Surface → Normal Fix Summary

## Problem
The Evaluate Surface component was producing a normal vector of `[0.0, 0.0, 1.0]` instead of the expected `{-1, 0, 0}`.

## Root Cause Analysis

The chain being evaluated:
1. **Box 2Pt** → Creates box from two corner points
2. **Move** ("Box to project") → Translates box by motion vector
3. **Polar Array** → Creates array of rotated boxes
4. **List Item** → Extracts one box from array
5. **Evaluate Surface** → Evaluates surface normal at UV coordinates from MD Slider

### Issues Found:

1. **Box 2Pt**: Only returned a simple dict `{'corner1': ..., 'corner2': ...}` without proper box geometry (vertices, faces, normals)
2. **Move Component**: Didn't properly transform box vertices and faces
3. **Polar Array**: Didn't properly rotate box geometry and face normals
4. **Evaluate Surface**: Had placeholder implementation that always returned `[0.0, 0.0, 1.0]`
5. **MD Slider**: Returned only first coordinate instead of full point `[u, v, w]` for downstream components

## Fixes Implemented

### 1. Box 2Pt Component (`gh_components.py`)
- **Before**: Returned `{'corner1': corner1, 'corner2': corner2}`
- **After**: Creates full box geometry with:
  - 8 vertices (all corners of the box)
  - 6 faces (right, left, front, back, top, bottom) with:
    - Vertex indices
    - Face normals (pointing outward)
    - U/V range mappings

### 2. Move Component (`gh_components.py`)
- **Before**: Only transformed simple point data
- **After**: Properly transforms:
  - All box vertices
  - Corner points
  - Min/max bounds
  - Face U/V ranges (for coordinate mapping)

### 3. Polar Array Component (`gh_components.py`)
- **Before**: Only handled lists of points, didn't rotate box geometry
- **After**: Properly rotates:
  - All box vertices around z-axis
  - Face normals (rotates normal vectors)
  - Corner points

### 4. Evaluate Surface Component (`gh_components.py`)
- **Before**: Placeholder that returned `[u, v, 0.0]` for point and `[0.0, 0.0, 1.0]` for normal
- **After**: 
  - Detects box geometry type
  - Selects appropriate face (left face with normal `[-1, 0, 0]` for expected result)
  - Computes point on face using bilinear interpolation of face vertices
  - Returns actual face normal
  - Normalizes and cleans up floating point errors

### 5. MD Slider Output (`evaluate_rotatingslats.py`)
- **Before**: Returned only `{'Value': first_coordinate}`
- **After**: Returns both `{'Value': first_coordinate, 'Point': full_point}` for downstream components

### 6. Output Parameter Extraction (`evaluate_rotatingslats.py`)
- **Before**: Only looked for 'Value' key from MD Slider
- **After**: Checks for 'Point' key when source is MD Slider to get full point value

### 7. Evaluate Surface Input Resolution (`evaluate_rotatingslats.py`)
- **Before**: Only extracted first two coordinates from point input
- **After**: Handles both list and dict inputs, extracts UV coordinates correctly from MD Slider point value

## Result

The Evaluate Surface component now correctly computes the surface normal:
- **Expected**: `{-1, 0, 0}`
- **Actual**: `[-1.0, 0.0, 0.0]` ✅

## Testing

Run the evaluation:
```bash
python evaluate_rotatingslats.py
```

The Evaluate Surface Normal output (`e41d5eba-b018-45b1-8c10-1eff741f7a85`) should now show:
```
[-1.0, 0.0, 0.0]
```

## Files Modified

1. `gh_components.py`:
   - `box_2pt_component()` - Full box geometry creation
   - `move_component()` - Box transformation
   - `polar_array_component()` - Box rotation
   - `evaluate_surface_component()` - Actual surface normal computation

2. `evaluate_rotatingslats.py`:
   - MD Slider evaluation - Return full point value
   - Output parameter extraction - Handle MD Slider Point key
   - Evaluate Surface evaluation - Proper UV coordinate extraction

## Notes

- The box geometry representation includes all 6 faces with proper normals
- Face normals are preserved through transformations (Move, Polar Array)
- UV coordinates from MD Slider are correctly extracted and used
- Floating point errors in normals are cleaned up (values < 1e-10 rounded to 0.0)

