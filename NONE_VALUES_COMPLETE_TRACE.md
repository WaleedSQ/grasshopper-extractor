# Complete None Values Trace

## Summary
Tracing all None values from first inputs to last outputs in the Rotatingslats evaluation.

## Components with None Outputs (16 total)

### 1. Move Components (5 instances)

#### First Move "Slats original" (ddb9e6ae...)
- **Output**: Geometry: None
- **Expected Geometry Source**: Rectangle 2Pt output (dbc236d4...)
- **Root Cause**: Rectangle 2Pt component (a3eb185f...) is NOT in evaluation results
- **Motion Source**: Vector 2Pt output (07dcee6c...)
- **Motion Status**: Resolved to None

**Chain**: Rectangle 2Pt → First Move → Polar Array → List Item → Second Move → Area

#### Second Move "Slats original" (0532cbdf...)
- **Output**: Geometry: None
- **Expected Geometry Source**: List Item output (a72418c4...)
- **Root Cause**: List Item returns None (see below)
- **Motion Source**: Amplitude output (d0668a07...)
- **Motion Status**: Resolved to None

#### Move "Targets" (9f3f4672...)
- **Output**: Geometry: None
- **Motion**: [0.0, 1.0, 0.0] ✅ (OK)
- **Expected Geometry Source**: List Item output
- **Root Cause**: List Item returns None

#### Move "Targets" (b38a38f1...)
- **Output**: Geometry: None
- **Motion**: None
- **Root Cause**: Both inputs are None

#### Move "Box to project" (dfbbd4a2...)
- **Output**: Geometry: None
- **Expected Source**: Box 2Pt output (7de8f856...)
- **Root Cause**: Box 2Pt component not evaluated

### 2. Area Components (3 instances)
- **Output**: Area: None, Centroid: None
- **Root Cause**: Geometry input is None (from Move components above)
- **Components**: 
  - 16022012... (Area)
  - 3bd2c1d3... (Area)
  - 77f7eddb... (Area)

### 3. Amplitude (f54babb4...)
- **Output**: Vector: None
- **Root Cause**: Input Vector is None
- **Expected Source**: Vector 2Pt or Vector XYZ output

### 4. List Item (d89d47e0...)
- **Output**: Result: None
- **Root Cause**: List input is empty or source not evaluated
- **Expected Source**: Polar Array or other list output

### 5. Negative Components (3 instances)
- **Output**: Result: None
- **Root Cause**: Value input is None
- **Components**:
  - 835d042f... (-)
  - d63be87d... (-)
  - a69d2e4a... (-)

## Root Cause Analysis

### Primary Issue: Rectangle 2Pt Not Evaluated

**Component**: a3eb185f-a7cb-4727-aeaf-d5899f934b99
**Type**: Rectangle 2Pt
**Status**: ✅ In graph, ❌ NOT in evaluation results

**Why it's not evaluated:**
1. **Topological sort issue**: The `topological_sort` function was iterating over `graph.items()` which only sees the top-level `"components"` key, not the actual component entries.
2. **Fix applied**: Modified `topological_sort` to handle graph structure:
   ```python
   components_dict = graph.get('components', graph) if isinstance(graph, dict) and 'components' in graph else graph
   ```
3. **Dependencies**: Rectangle 2Pt depends on:
   - Plane: Has persistent_values ✅
   - Point A: Source from Construct Point A (902866aa...)
   - Point B: Source from Construct Point B (ef17623c...)
   - Length: Source from "Slat thickness"

**Impact**: Without Rectangle 2Pt, the entire Rotatingslats chain fails:
- First Move gets None → Polar Array gets None → List Item gets None → Second Move gets None → Area gets None

## Dependency Chain (Expected)

1. **Construct Point A** → Point A output
2. **Construct Point B** → Point B output
3. **Rectangle 2Pt** → Rectangle output (dbc236d4...)
4. **First Move** → Geometry output
5. **Polar Array** → Array output
6. **List Item** → Selected item
7. **Second Move** → Geometry output
8. **Area** → Centroid output

## Next Steps

1. ✅ Fixed topological_sort to handle graph structure
2. ⏳ Verify Rectangle 2Pt is now in topological sort
3. ⏳ Check if Rectangle 2Pt's dependencies (Construct Point A/B) are evaluated
4. ⏳ Verify Rectangle 2Pt appears in evaluation results
5. ⏳ Trace remaining None values (Amplitude, List Item, Negative components)

