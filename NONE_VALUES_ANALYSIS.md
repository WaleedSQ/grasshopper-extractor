# None Values Analysis

## Summary
Found 16 components with None outputs. Root cause: Source components are not being evaluated.

## Key Findings

### 1. First Move "Slats original" (ddb9e6ae...)
- **Output**: Geometry: None
- **Expected Source**: Rectangle 2Pt output (dbc236d4...)
- **Root Cause**: Rectangle 2Pt component (a3eb185f...) is NOT in evaluation results
- **Chain**: Rectangle 2Pt → First Move → Polar Array → List Item → Second Move → Area

### 2. Second Move "Slats original" (0532cbdf...)
- **Output**: Geometry: None
- **Expected Source**: List Item output (a72418c4...)
- **Root Cause**: List Item returns None (see below)

### 3. Move "Targets" (9f3f4672...)
- **Output**: Geometry: None
- **Motion**: [0.0, 1.0, 0.0] (OK)
- **Expected Source**: List Item output
- **Root Cause**: List Item returns None

### 4. Move "Targets" (b38a38f1...)
- **Output**: Geometry: None
- **Motion**: None
- **Root Cause**: Both Geometry and Motion inputs are None

### 5. Move "Box to project" (dfbbd4a2...)
- **Output**: Geometry: None
- **Expected Source**: Box 2Pt output
- **Root Cause**: Box 2Pt component not evaluated

### 6. Area components (3 instances)
- **Output**: Area: None, Centroid: None
- **Root Cause**: Geometry input is None (from Move components above)

### 7. Amplitude (f54babb4...)
- **Output**: Vector: None
- **Root Cause**: Input Vector is None

### 8. List Item (d89d47e0...)
- **Output**: Result: None
- **Root Cause**: List input is empty or source not evaluated

### 9. Negative components (3 instances)
- **Output**: Result: None
- **Root Cause**: Value input is None

## Root Causes

1. **Rectangle 2Pt not evaluated**: The component a3eb185f... is missing from evaluation results
2. **Box 2Pt not evaluated**: Box components are missing
3. **Source components not in topological sort**: Some components may not be included in the dependency graph
4. **Input resolution failing**: Sources exist but aren't being resolved correctly

## Next Steps

1. Check why Rectangle 2Pt (a3eb185f...) is not in the evaluation order
2. Verify topological sort includes all required components
3. Check if Rectangle 2Pt has dependencies that aren't being evaluated
4. Verify input resolution is finding source components correctly

