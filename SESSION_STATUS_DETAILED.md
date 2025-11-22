# Detailed Session Status - Rotatingslats Evaluation Chain

**Last Updated**: Current Session  
**Goal**: Make `evaluate_rotatingslats.py` run end-to-end without exceptions, using tree-aware versions of Move, Polar Array, List Item, and Area components.

---

## Executive Summary

### ✅ Completed Tasks

1. **Topological Sort Fix**: Fixed to ensure all components are included, even isolated ones
2. **Input Name Mapping**: Added mappings for Construct Point, Rectangle 2Pt, Polygon, Rotate, Mirror, PolyLine, Divide Length, Box 2Pt
3. **DataTree Handling**: Fixed `resolve_input_value` to preserve DataTree for tree-aware components (Move, Polar Array, List Item, Area)
4. **Polygon Component**: Verified working correctly, returns dict with vertices
5. **Rotate Component**: Fixed to receive full geometry dict instead of string
6. **Input Resolution**: Added geometry dict detection in `resolve_input_value` to prioritize full dicts over string values
7. **Series Component**: Fixed to handle `0` as valid start value
8. **Negative Component**: Fixed external input resolution for `0.0` values

### ⚠️ Current Issues

1. **Mirror → Area Chain**: Mirror component is outputting a **string** instead of a **geometry dict** to Area component
   - **Location**: `evaluate_rotatingslats.py` line ~1163 (Mirror output handling)
   - **Impact**: Area component receives string, returns `{'Area': 0.0, 'Centroid': [0.0, 0.0, 0.0]}`
   - **Root Cause**: Mirror output extraction in `resolve_input_value` or Mirror's return value handling

2. **Other Errors** (non-blocking for Rotatingslats chain):
   - Vector 2Pt component: Missing Point B input
   - Construct Plane component: Type error with list operations

### 🔄 In Progress

- Fixing Mirror component output format for Area component consumption

---

## Technical Details

### Component Chain (Rotatingslats)

```
Rectangle 2Pt → Move (first) → Polar Array → List Item → Move (second) → Area
                                                                    ↓
                                                              Polygon → Rotate → Mirror → Area
```

**Key Component GUIDs:**
- **First Move**: `ddb9e6ae-...` (converts list to 10-branch tree)
- **Polar Array**: `7ad636cc-e506-4f77-bb82-4a86ba2a3fea` (10 branches, 8 items per branch)
- **List Item**: `27933633-dbab-4dc0-a4a2-cfa309c03c45` (10 branches)
- **Second Move**: `0532cbdf-875b-4db9-8c88-352e21051436` (10-branch geometry tree)
- **Area (Rotatingslats)**: `3bd2c1d3-149d-49fb-952c-8db272035f9e` (10 centroid branches)
- **Polygon**: `a2151ddb-...` (8 segments, radius 3.0)
- **Rotate**: `5a77f108-b5a1-429b-9d22-0a14d7945abd` (67.5 degrees)
- **Mirror**: `47650d42-5fa9-44b3-b970-9f28b94bb031` (mirrors across YZ plane)
- **Area (after Mirror)**: `16022012-569d-4c58-a081-6d57649a1720` (receives from Mirror)

### DataTree Semantics

**Tree-Aware Components** (preserve DataTree):
- Move (`move_component`)
- Polar Array (`polar_array_component`)
- List Item (`list_item_component`)
- Area (`area_component`)

**Non-Tree-Aware Components** (flatten DataTree to list):
- All other components

**Key Functions**:
- `is_tree(value)`: Check if value is DataTree
- `to_tree(value)`: Convert list to DataTree
- `from_tree(tree)`: Convert DataTree to list (for non-tree-aware components)

### Input Resolution Flow

1. **Check sources** (component outputs):
   - Look up source component in `evaluated` dict
   - Extract output using `source_param_name` or geometry keys
   - **For tree-aware components**: Return DataTree unchanged
   - **For non-tree-aware components**: Flatten DataTree to list

2. **Check external inputs** (sliders, panels):
   - Look up by parameter GUID in `external_inputs.json`
   - Handle `0.0` as valid value (not falsy)

3. **Check persistent values**:
   - From `persistent_values` or `values` in param_info
   - Parse JSON for vectors/planes

### Geometry Dict Structure

Components that work with geometry dicts:
- **Polygon**: `{'polygon': 'polygon_geometry', 'vertices': [...], 'radius': ..., 'segments': ..., 'plane': {...}}`
- **Rotate**: Expects dict with `'vertices'` key, returns same structure
- **Mirror**: Expects dict with `'vertices'` key, returns same structure
- **Area**: Can process dict with `'vertices'` key (for boxes, polygons)

**Key Detection**:
```python
has_geometry_keys = 'vertices' in comp_outputs or 'points' in comp_outputs or 'corners' in comp_outputs
if has_geometry_keys:
    source_value = comp_outputs  # Use full dict
```

---

## File Structure

### Core Files

1. **`evaluate_rotatingslats.py`** (Main evaluation script)
   - `load_component_graph()`: Loads `complete_component_graph.json`
   - `topological_sort()`: Orders components by dependencies
   - `resolve_input_value()`: Resolves component inputs from various sources
   - `evaluate_component()`: Evaluates a single component
   - `evaluate_graph()`: Main evaluation loop

2. **`gh_components.py`** (Component implementations)
   - `move_component()`: Tree-aware Move
   - `polar_array_component()`: Tree-aware Polar Array
   - `list_item_component()`: Tree-aware List Item
   - `area_component()`: Tree-aware Area
   - `polygon_component()`: Polygon generation
   - `rotate_component()`: Geometry rotation
   - `mirror_component()`: Geometry mirroring

3. **`gh_data_tree.py`** (DataTree utilities)
   - `DataTree` class: Tree structure with paths
   - `is_tree()`: Check if value is DataTree
   - `to_tree()`: Convert list to DataTree
   - `from_tree()`: Convert DataTree to list

### Data Files

- **`complete_component_graph.json`**: Full component dependency graph
- **`external_inputs.json`**: External input values (sliders, panels)
- **`rotatingslats_data.json`**: Component definitions and persistent data

### Verification Scripts

- **`verify_area_after_mirror.py`**: Checks Area component after Mirror
- **`verify_polygon.py`**: Verifies Polygon component
- **`verify_rotate_mirror.py`**: Verifies Rotate and Mirror components
- **`verify_polar_array.py`**: Verifies Polar Array component
- **`verify_all_list_items.py`**: Verifies all List Item components

---

## Current Issue: Mirror → Area Chain

### Problem

The Area component (`16022012-569d-4c58-a081-6d57649a1720`) that receives input from Mirror is getting a **string** instead of a **geometry dict**.

**Verification Output**:
```
Mirror (47650d42...) found in evaluated results
  Geometry type: str
  Is DataTree: False

Area (16022012...) found in evaluated results
  Area output: 0.0
  Centroid output: [0.0, 0.0, 0.0]
```

**Root Cause Identified**:
Debug output shows:
```
DEBUG [ROTATE] Input geometry type: str  (first call - wrong)
DEBUG [ROTATE] Input geometry type: dict (second call - correct)
DEBUG [MIRROR] Input geometry type: str  (receives string from Rotate)
```

The issue is that **Rotate is being called twice**:
1. First call receives a **string** (incorrect) → outputs string
2. Second call receives a **dict** (correct) → outputs dict correctly

Mirror is resolving its input from the **first (incorrect) Rotate call**, which received a string. This suggests:
- Rotate is being evaluated multiple times (possibly in different contexts)
- The first evaluation path is getting incorrect input (string instead of dict)
- Mirror is picking up the wrong Rotate output

### Expected Behavior

1. **Mirror** should output a dict with `'vertices'` key (mirrored geometry)
2. **Area** should receive this dict and compute area/centroid
3. **Area** should output numeric values (not 0.0)

### Root Cause Analysis

**Possible causes**:

1. **Mirror output extraction**: `resolve_input_value` is extracting a string from Mirror's output dict
   - Similar to the Polygon → Rotate issue that was fixed
   - Need to check if geometry dict detection is working for Mirror output

2. **Mirror return value**: `mirror_component()` might be returning a string in some cases
   - Check `gh_components.py` line ~2236: `return geometry` (pass-through)
   - If geometry is a string, it passes through unchanged

3. **Output storage**: Mirror's output might be stored incorrectly in `evaluated` dict
   - Check `evaluate_component()` line ~1163: `return {'Geometry': result}`
   - If `result` is a string, it's stored as a string

### Investigation Steps

1. **Check Mirror input**: Verify what Mirror receives from Rotate
   ```python
   # In verify_area_after_mirror.py, add:
   if mirror_guid in evaluated:
       mirror_inputs = ...  # Get inputs to Mirror
       print(f"Mirror input type: {type(mirror_inputs.get('Geometry'))}")
   ```

2. **Check Mirror output**: Verify what Mirror returns
   ```python
   # In evaluate_component, add debug for Mirror:
   if comp_type == 'Mirror':
       print(f"DEBUG [MIRROR] Input geometry type: {type(geometry)}")
       print(f"DEBUG [MIRROR] Output result type: {type(result)}")
   ```

3. **Check resolve_input_value**: Verify how Area resolves Mirror output
   ```python
   # In resolve_input_value, add debug:
   if source_comp_type == 'Mirror':
       print(f"DEBUG [RESOLVE] Mirror output type: {type(comp_outputs)}")
       print(f"DEBUG [RESOLVE] Extracted value type: {type(source_value)}")
   ```

### Fix Strategy

1. **Fix Rotate input resolution**: Ensure Rotate receives geometry dict from Polygon, not string
   - Check why Rotate is being called with string input
   - Verify Polygon output extraction in `resolve_input_value`
   - Ensure geometry dict detection works for Rotate input

2. **Fix Mirror input resolution**: Ensure Mirror receives geometry dict from Rotate
   - Check output parameter GUID resolution (`3560b89d-9e35-4df7-8bf6-1be7f9ab2e19`)
   - Ensure `resolve_input_value` extracts 'Geometry' key correctly when it's a dict
   - Add check: if Rotate output is `{'Geometry': dict_with_vertices}`, use the dict

3. **Fix Mirror output extraction**: Ensure Area receives geometry dict from Mirror
   - Already added: Check if 'Geometry' value is a geometry dict before extracting
   - Ensure Mirror always returns dict structure (not pass-through for strings)

4. **Debug logging added**: 
   - Rotate: Logs input/output types and keys
   - Mirror: Logs input/output types and keys
   - resolve_input_value: Logs when extracting Mirror/Rotate outputs

---

## Verification Results

### ✅ Working Components

1. **Polar Array** (`7ad636cc-...`):
   - Input: 10-branch tree (rectangles)
   - Output: 10 branches, 8 items per branch ✅
   - Status: **VERIFIED**

2. **List Item** (`27933633-...`):
   - Input: 10-branch tree (8 items per branch)
   - Output: 10 branches (1 item per branch) ✅
   - Status: **VERIFIED**

3. **Polygon** (`a2151ddb-...`):
   - Output: Dict with 9 vertices, radius 3.0, 8 segments ✅
   - Status: **VERIFIED**

4. **Rotate** (`5a77f108-...`):
   - Input: Polygon dict with vertices ✅
   - Output: Rotated dict with vertices ✅
   - Status: **VERIFIED** (when receiving dict)

5. **Area (Rotatingslats)** (`3bd2c1d3-...`):
   - Input: 10-branch geometry tree ✅
   - Output: 10-branch centroid tree ✅
   - First branch centroid Y: `-0.018417927971181088` ✅
   - Status: **VERIFIED**

### ⚠️ Issues Found

1. **Mirror** (`47650d42-...`):
   - Input: Rotate dict with vertices ✅
   - Output: **String instead of dict** ❌
   - Status: **NEEDS FIX**

2. **Area (after Mirror)** (`16022012-...`):
   - Input: String from Mirror ❌
   - Output: `{'Area': 0.0, 'Centroid': [0.0, 0.0, 0.0]}` ❌
   - Status: **BLOCKED BY MIRROR ISSUE**

---

## Next Steps

### Immediate (Priority 1)

1. **Fix Rotate input resolution**:
   - [x] Added debug logging to Rotate component evaluation
   - [ ] Identify why Rotate is being called with string input (first call)
   - [ ] Fix `resolve_input_value` to ensure Rotate always receives geometry dict from Polygon
   - [ ] Ensure Rotate evaluation order is correct (after Polygon is fully evaluated)
   - [ ] Verify Rotate only stores correct (dict) output in `evaluated` dict

2. **Fix Mirror → Area chain**:
   - [x] Added debug logging to Mirror component evaluation
   - [x] Added geometry dict detection in `resolve_input_value` for Mirror output
   - [ ] Verify Mirror receives correct input from Rotate (dict, not string)
   - [ ] Verify Mirror returns correct output (dict with vertices)
   - [ ] Verify Area receives geometry dict from Mirror
   - [ ] Verify Area computes correct area/centroid

### Follow-up (Priority 2)

2. **Fix other errors** (non-blocking):
   - [ ] Vector 2Pt: Fix missing Point B input
   - [ ] Construct Plane: Fix type error with list operations

3. **Final verification**:
   - [ ] Run full evaluation without exceptions
   - [ ] Verify all Rotatingslats chain components output correctly
   - [ ] Generate summary with branch counts and centroid values

---

## Code Locations

### Key Functions

1. **`resolve_input_value()`** (`evaluate_rotatingslats.py` ~line 250-550):
   - Handles input resolution from sources, external inputs, persistent values
   - **Geometry dict detection**: Lines ~320-330
   - **Tree-aware component check**: Lines ~280-300

2. **`evaluate_component()`** (`evaluate_rotatingslats.py` ~line 561-1225):
   - Evaluates individual components
   - **Mirror handling**: Lines ~1154-1163
   - **Area handling**: Lines ~835-862
   - **Error logging**: Lines ~1202-1225

3. **`mirror_component()`** (`gh_components.py` ~line 2175-2236):
   - Mirrors geometry across a plane
   - **Dict handling**: Lines ~2198-2233
   - **Pass-through**: Line ~2236 (returns geometry unchanged if not dict)

4. **`area_component()`** (`gh_components.py` ~line 1140-1300):
   - Computes area and centroid
   - **DataTree handling**: Lines ~1162-1181
   - **Dict handling**: Lines ~1206-1250

### Key Data Structures

1. **`evaluated` dict**: Stores component outputs
   - Key: Component GUID or instance_guid
   - Value: Component output (dict, list, DataTree, etc.)

2. **`output_params` dict**: Maps output parameter GUIDs to components
   - Key: Parameter GUID (InstanceGuid)
   - Value: Component info and param info

3. **`external_inputs` dict**: External input values
   - Key: Parameter GUID
   - Value: Input value (number, string, dict, etc.)

---

## Debugging Commands

### Run Full Evaluation
```bash
python evaluate_rotatingslats.py
```

### Check Mirror Output
```bash
python verify_area_after_mirror.py
```

### Check Specific Component
```bash
python -c "
from evaluate_rotatingslats import *
graph = load_component_graph('complete_component_graph.json')
# ... check specific component
"
```

### Filter Debug Output
```powershell
python evaluate_rotatingslats.py 2>&1 | Select-String -Pattern "DEBUG.*Mirror|DEBUG.*Area|ERROR"
```

---

## Notes

- **Tree-aware components** must preserve DataTree structure
- **Geometry dicts** should be detected by `'vertices'`, `'points'`, or `'corners'` keys
- **External inputs** with value `0.0` are valid (not falsy)
- **Topological sort** includes all components, even isolated ones
- **Error logging** includes component GUID, type, nickname, and raw inputs

---

## Related Documents

- `ROTATE_MIRROR_VERIFICATION.md`: Rotate and Mirror component verification
- `POLYGON_VERIFICATION.md`: Polygon component verification
- `POLAR_ARRAY_VERIFICATION.md`: Polar Array component verification
- `LIST_ITEM_VERIFICATION.md`: List Item component verification
- `AREA_CENTROID_FIX_SUMMARY.md`: Area component fix summary

---

**Status**: ⚠️ **IN PROGRESS** - Root cause identified: Rotate is being called with string input in one evaluation path. Need to fix Rotate input resolution to ensure it always receives geometry dict from Polygon.

**Latest Debug Findings**:
- Rotate is called twice: once with string (wrong), once with dict (correct)
- Mirror receives string from the first (incorrect) Rotate call
- Fix needed: Ensure Rotate input resolution always extracts geometry dict from Polygon output
- Added debug logging to trace Rotate/Mirror input/output types

