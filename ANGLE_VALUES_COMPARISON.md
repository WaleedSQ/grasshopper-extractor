# Angle Values Comparison

## Current Output vs Screenshot

### Our Degrees Output:
```
0: 2.58°
1: 23.34°
2: 39.27°
3: 50.29°
4: 57.84°
5: 63.16°
6: 67.06°
7: 70.01°
8: 72.31°
9: 74.15°
```

**Pattern**: Values INCREASE from 2.58° to 74.15°

### Screenshot Degrees Output:
```
0: 43.71°
1: 43.03°
2: 42.22°
3: 41.22°
4: 39.96°
5: 38.34°
6: 36.18°
7: 33.22°
8: 29.03°
9: 22.97°
```

**Pattern**: Values DECREASE from 43.71° to 22.97°

---

## What We're Currently Calculating

### Vector A (from Plane Normal):
- All 10 planes have the SAME z_axis: `[0, -1, 0]`
- Only origins vary (Z from 3.8 to 3.1)
- When extracted as vector: `[0, -1, 0]` (repeated 10 times)

### Vector B (from Line "Between"):
- 10 different lines with varying directions
- Example: 
  - Start: `[0.0, 0.271, 3.809]`
  - End: `[0.0, 0.070, 3.800]`
  - Direction: `[0, -0.201, -0.009]`

### Current Angle Calculation:
- Angle between Vector A `[0, -1, 0]` and Vector B direction
- As Vector B varies from nearly parallel to Vector A to more angled, our angle increases
- This gives us: 2.58° → 74.15° (increasing)

---

## Possible Issues

### 1. Wrong Vectors Being Used
Maybe Vector A should be from:
- ✗ Rotated slat planes (but we checked - they would need to exist and vary)
- ✗ A different geometric reference
- ? Something else we haven't identified

### 2. Angle Measurement Reference
Screenshot might be measuring:
- Angle from horizontal (not between two vectors)
- Angle from vertical
- Complementary angle
- Angle in a specific plane projection

### 3. Different Input State
The screenshot might have different slider values than our current evaluation

### 4. Vector Extraction Issue
We might be extracting the wrong component from planes:
- Currently using `z_axis` for planes
- Maybe should use `x_axis` or `y_axis`?
- Or normal direction of rotated geometry?

---

## Questions for Clarification

1. **Are the slider values in the screenshot the same as our current evaluation?**
   - Number of slats: 10
   - All other sliders at their current values?

2. **What should Vector A actually represent?**
   - Slat surface normal (from rotated geometry)?
   - A fixed reference direction?
   - The plane z-axis we're currently using?

3. **What should Vector B represent?**
   - Line direction from DL points (currently using)?
   - Something else?

4. **Should the angle be:**
   - Direct angle between vectors (what we're doing)?
   - Angle from horizontal/vertical?
   - Projected angle in a specific plane?

---

## Current Component Chain

```
Plane Normal (z_axis=[0,-1,0] for all) 
  → List Item [index=0] 
  → Angle Vector A (grafted to match Vector B)

Line Between (10 varying directions)
  → Angle Vector B

Angle: calculates dot product angle
  → Degrees: converts to degrees
```

---

**Status**: Awaiting clarification on what the expected values represent

