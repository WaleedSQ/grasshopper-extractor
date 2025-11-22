# Bugs Fixed Summary

## Current Status
- **49/56 components evaluating successfully** (87.5%)
- **7 components with errors** (12.5%)

## Critical Bugs Fixed

### 1. ✅ Wire Resolution Bug in `isolate_rotatingslats.py`
**Problem:** When creating internal wires, the `from_component` field was set to the output parameter GUID instead of the component GUID.

**Impact:** The topological sort couldn't build the correct dependency graph because it was looking up parameter GUIDs as if they were component GUIDs.

**Fix:** Modified `isolate_rotatingslats.py` to create corrected wire objects with resolved component GUIDs:
```python
corrected_wire = {
    'from_component': from_comp_guid,  # Now component GUID, not param GUID
    'from_param': wire['from_param'],
    'to_component': wire['to_component'],
    'to_param': wire['to_param'],
    'to_param_name': wire['to_param_name']
}
```

### 2. ✅ Topological Sort Bug in `gh_evaluator_wired.py`
**Problem:** The topological sort was still treating `wire['from_component']` as a parameter GUID and trying to resolve it, which failed after the wire fix above.

**Impact:** Components were evaluated in the wrong order. For example, "Move: New Sun" was evaluated at step 27 but its dependency "Area" wasn't evaluated until step 46, causing it to receive empty/incorrect data.

**Fix:** Updated topological sort to use `wire['from_component']` directly as component GUID:
```python
# Before:
from_param_guid = wire['from_component']  # Actually parameter GUID
from_comp_guid = param_to_component.get(from_param_guid)

# After:
from_comp_guid = wire['from_component']  # Now component GUID
```

### 3. ✅ Plane Normal Implementation Bug
**Problem:** Plane Normal was implemented as a deconstructor (extracting components from a plane) when it should be a constructor (building a plane from origin + Z-axis).

**Fix:** Completely rewrote `evaluate_plane_normal()` to construct planes from origin and Z-axis vectors, including proper normalization and orthogonal axis computation.

### 4. ✅ PolyLine Data Structure Bug  
**Problem:** PolyLine was iterating over individual vertices as if each was a separate polyline, instead of treating all vertices in a branch as ONE polyline.

**Fix:** Modified to process all vertices in a branch as a single polyline:
```python
# Before: for vertices in vertex_lists (treating each vertex as a list)
# After: vertices = vertices_tree.get_branch(path)  (all vertices = one polyline)
```

### 5. ✅ Plane Normal `longest_match` Bug
**Problem:** Called `DataTree.longest_match()` as a class method when it should use the `match_longest()` function.

**Fix:** Changed to use `match_longest(origin_tree, z_axis_tree)` function.

### 6. ✅ List Item Parameter Extraction Bug
**Problem:** Variable-parameter components like "List Item" use `<chunk name="ParameterData">` instead of `param_input`/`param_output`, so 0 parameters were extracted.

**Fix:** Updated `parse_refactored_ghx.py` to handle `ParameterData` chunks:
```python
# Look for ParameterData chunk
param_data_chunk = obj.find('.//chunk[@name="ParameterData"]')
if param_data_chunk:
    # Extract from InputParam and OutputParam sub-chunks
```

## Remaining Errors (7 components)

### Line Components (3 failures)
- **Error:** `ValueError: GH Line: direction vector is None`
- **Root Cause:** Upstream components not providing valid direction vectors

### Plane Normal Components (2 failures)
- **Error 1:** `ValueError: GH Plane Normal: plane dict missing z_axis key`
- **Error 2:** `ValueError: GH Plane Normal: origin must be [x,y,z], got <class 'float'>`
- **Root Cause:** Receiving malformed input data from upstream components

### Divide Length Components (2 failures)
- **Error:** `ValueError: GH Divide Length: curve must be a dict, got <class 'int'>`
- **Root Cause:** Receiving integer 0 instead of curve geometry (cascade from Line failures)

## Next Steps
1. Trace the Line components to find why direction vectors are None
2. Fix upstream data flow issues causing malformed inputs to Plane Normal
3. Once Line components work, Divide Length should cascade and work automatically

## Progress Timeline
- Started: 0/56 (0%)
- After initial implementation: 47/56 (83.9%)
- After topological sort fix: **49/56 (87.5%)**
- Target: 56/56 (100%)

