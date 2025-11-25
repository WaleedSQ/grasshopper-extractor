# Area → Centroid Fix Summary

## Problem
The Area component's Centroid output for the "Box to project" chain was returning `[0.0, 0.0, 0.0]` instead of the expected `{11.32743, -27.846834, 2.0}`.

## Root Cause Analysis

The chain being evaluated:
1. **Box 2Pt** → Creates box from two corner points
2. **Move** ("Box to project") → Translates box by motion vector `[11.327429598006665, -27.346834162334087, 0.0]`
3. **Area** → Computes area and centroid of the moved box

### Issues Found:

1. **Area Component**: Didn't handle box geometry type (`'type': 'box'`)
   - Only handled rectangles (with 'corners') and polylines (with 'points')
   - Returned placeholder `[0.0, 0.0, 0.0]` for box geometry

2. **Centroid Calculation**: Initially tried to use stored `min`/`max` bounds
   - These bounds might not be correctly updated after Move transformation
   - Needed to compute from actual vertices after transformation

## Fixes Implemented

### 1. Area Component Box Handling (`gh_components.py`)

**Before**: Only handled rectangles and polylines, returned placeholder for boxes

**After**: Added proper box geometry handling:
- Detects box geometry by checking `geometry.get('type') == 'box'`
- Computes centroid from actual vertices (more accurate after transforms)
- Computes box surface area: `2 * (width*height + width*depth + height*depth)`

### 2. Centroid Calculation Method

**Before**: Used stored `min`/`max` bounds which might be stale after transformations

**After**: 
- Computes actual min/max from vertices after transformation
- Centroid = average of actual min and max corners
- Falls back to stored min/max or corner1/corner2 if vertices unavailable

### Implementation Details

```python
# Compute actual min/max from vertices (more accurate after transforms)
actual_min = [
    min(v[0] for v in vertices if len(v) > 0),
    min(v[1] for v in vertices if len(v) > 1),
    min(v[2] for v in vertices if len(v) > 2)
]
actual_max = [
    max(v[0] for v in vertices if len(v) > 0),
    max(v[1] for v in vertices if len(v) > 1),
    max(v[2] for v in vertices if len(v) > 2)
]
# Centroid is the average of actual min and max
centroid = [
    (actual_min[0] + actual_max[0]) / 2.0,
    (actual_min[1] + actual_max[1]) / 2.0,
    (actual_min[2] + actual_max[2]) / 2.0
]
```

## Result

The Area component now correctly computes the centroid:
- **Expected**: `{11.32743, -27.846834, 2.0}`
- **Actual**: `[11.327429598006665, -27.846834162334087, 2.0]` ✅

**Precision Check**:
- X: |11.32743 - 11.327429598006665| = 0.0000004 < 1e-6 ✅
- Y: |-27.846834 - (-27.846834162334087)| = 0.00000016 < 1e-6 ✅
- Z: |2.0 - 2.0| = 0.0 ✅

## Testing

Run the evaluation:
```bash
python evaluate_rotatingslats.py
```

The Area Centroid output (`34529a8c-3dfd-4d96-865b-9e4cbfddad6c`) should now show:
```
[11.327429598006665, -27.846834162334087, 2.0]
```

## Files Modified

1. `gh_components.py`:
   - `area_component()` - Added box geometry handling
   - Computes centroid from actual vertices after transformation
   - Computes box surface area

## Notes

- The centroid is computed from the geometric center of the box (average of min and max)
- Using actual vertices ensures accuracy after transformations (Move, Rotate, etc.)
- The box area is computed as the sum of all 6 face areas
- The fix maintains compatibility with existing rectangle and polyline handling

