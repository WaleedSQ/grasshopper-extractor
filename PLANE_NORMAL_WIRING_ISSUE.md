# Plane Normal Wiring Issue - Root Cause Found

## The Problem

Our angle values don't match the screenshot because we're using the wrong plane normals for Vector A.

## Two Plane Normal Components

### Plane Normal 1 (Position: 12043, 2991)
- **Z-Axis Input**: PolyLine at (11862, 2990)
- **Output z_axis**: `(0, -1, 0)`  
- **Currently feeds**: Angle Vector A ✗ WRONG!

### Plane Normal 2 (Position: 12184, 3075)
- **Z-Axis Input**: Construct Plane at (12039, 3119)
- **Output z_axis**: `(-1, 0, 0)` ✓ MATCHES SCREENSHOT!
- **Should feed**: Angle Vector A

## Construct Plane Output

The Construct Plane outputs planes with:
```
origin: [0, 0.07, 3.8] (varies for each slat)
x_axis: [-1, 0, 0]  ← This is extracted by Plane Normal 2
y_axis: [0, -1, 0]
z_axis: [0, 0, 1]
```

## Current Wiring (Wrong)

```
PolyLine → Plane Normal 1 → List Item → Angle Vector A
           (z_axis = 0,-1,0)
```

## Expected Wiring (From Screenshot)

```
Construct Plane → Plane Normal 2 → ??? → Angle Vector A
                  (z_axis = -1,0,0)
```

## Impact on Angle Calculation

### Current (Wrong):
- Vector A: `(0, -1, 0)` (repeated for all slats)
- Vector B: Varying line directions
- Result: Angles 2.58° → 74.15° (increasing)

### Expected (Correct):
- Vector A: `(-1, 0, 0)` (correct slat normal)
- Vector B: Varying line directions
- Result: Should be 43.71° → 22.97° (decreasing)

## Next Steps

Need to either:
1. Fix the wiring in our graph to use Plane Normal 2
2. Check if the GHX file wiring is correct and our parsing is wrong
3. Verify the screenshot matches the actual GHX state

## Question for User

The screenshots show planes with z_axis = `(-1, 0, 0)`, but our current evaluation uses planes with z_axis = `(0, -1, 0)`. 

Should the Angle component's Vector A be receiving planes from:
- A) The PolyLine-based Plane Normal (current: outputs `(0,-1,0)`)
- B) The Construct Plane-based Plane Normal (screenshot: outputs `(-1,0,0)`)

Or has the GHX file been modified since the screenshot was taken?

