# Rotatingslats Evaluation System - Status Summary

## Project Overview

This project evaluates a Grasshopper (GHX) component graph for a rotating slats shading system. The system parses a GHX file, builds a dependency graph, and evaluates components in topological order to compute geometry outputs.

**Main Files:**
- `evaluate_rotatingslats.py` - Main evaluation engine
- `gh_components.py` - Component implementations (Move, Polar Array, Area, etc.)
- `parse_ghx_v2.py` - GHX XML parser
- `complete_component_graph.json` - Component dependency graph
- `rotatingslats_data.json` - Component data from GHX
- `external_inputs.json` - External input values (sliders, panels)

## Current Status

### ✅ Working Components

1. **Topological Sort**: Components are evaluated in correct dependency order
2. **External Inputs**: Sliders, panels, and constants are correctly loaded
3. **Basic Components**: Number operations, Construct Point, Vector operations
4. **Polar Array**: Rotation logic implemented (rotates geometry around plane's z-axis)
5. **Move Component**: Handles single geometry with single/multiple motion vectors
6. **Area Component**: Handles lists of geometries recursively
7. **Output Parameter Extraction**: Correctly extracts values from component outputs

### ⚠️ Known Issues

1. **Rectangle 2Pt Output Extraction** (PARTIALLY FIXED):
   - Issue: First Move "Slats original" receives string `'rectangle'` instead of geometry dict
   - Status: User reverted recent changes; needs careful re-analysis
   - Affected Chain: Rectangle 2Pt → First Move "Slats original" → Polar Array → List Item → Second Move "Slats original" → Area

2. **List Item Components**: Some return `None` (may be expected if list is empty or index out of range)

3. **Area Component**: Some return `{'Area': 0.0, 'Centroid': [0.0, 0.0, 0.0]}` (may be expected for certain geometry types)

## Fixes Implemented

### 1. Polar Array Rotation (FIXED)
- **Problem**: Polar Array was copying geometry without rotation
- **Fix**: Implemented rotation around plane's z-axis using rotation matrix
- **Location**: `gh_components.py` - `polar_array_component()` function
- **Result**: Y-coordinate matches screenshot for "Targets" chain

### 2. Plane PersistentData Parsing (FIXED)
- **Problem**: Polar Array's Plane input had PersistentData in GHX but wasn't parsed
- **Fix**: Added `gh_plane` parsing in `parse_ghx_v2.py` (lines 220-274)
- **Result**: Plane correctly extracted from GHX and used in Polar Array

### 3. Input Resolution Priority (FIXED)
- **Problem**: PersistentData not prioritized when no sources connected
- **Fix**: Updated `resolve_input_value()` to check PersistentData only when sources list is empty
- **Location**: `evaluate_rotatingslats.py` lines 103-126

### 4. Move Component List Handling (FIXED)
- **Problem**: Move component didn't handle single geometry with list of motion vectors
- **Fix**: Updated `move_component()` to produce list of moved geometries when motion is a list
- **Location**: `gh_components.py` lines 926-952

### 5. Area Component List Handling (FIXED)
- **Problem**: Area component didn't handle lists of geometries
- **Fix**: Added recursive handling for lists of geometries
- **Location**: `gh_components.py` lines 844-855

### 6. Amplitude Component Vector Input (FIXED)
- **Problem**: Amplitude component's Vector input wasn't resolving
- **Fix**: Updated output parameter extraction to correctly retrieve vector values
- **Location**: `evaluate_rotatingslats.py` lines 255-260

### 7. Component Input Building (FIXED)
- **Problem**: Components missing `inputs` key in `comp_info` failed to evaluate
- **Fix**: Added fallback to build `inputs` from `obj.params` when missing
- **Location**: `evaluate_rotatingslats.py` lines 655-678

## How to Run

### Prerequisites
- Python 3.7+
- Required files:
  - `complete_component_graph.json`
  - `rotatingslats_data.json`
  - `external_inputs.json`

### Basic Execution

```bash
# Run full evaluation
python evaluate_rotatingslats.py

# Check for errors only
python evaluate_rotatingslats.py 2>&1 | Select-String -Pattern "Total|Final|Error" | Select-Object -First 5

# On Linux/Mac:
python evaluate_rotatingslats.py 2>&1 | grep -E "Total|Final|Error" | head -5
```

### Output

The script outputs:
1. Component evaluation order
2. Evaluation results for each component
3. Final output value (currently Degrees: 0.0)
4. Errors if any occur

Results are also written to `evaluation_results.md` with a table of all evaluated components.

### Tracing Specific Chains

To trace a specific component chain:

```bash
# Trace "Slats original" geometry chain
python trace_slats_geometry_chain.py

# Trace "Targets" chain
python trace_complete_targets_chain.py
```

## Verification Steps

### 1. Verify Targets Chain
**Expected**: Move component `80fd9f48...` (Targets.Geometry) should output:
```
[[11.327429598006665, -22.846834162334087, 4.0], ...]
```

**Check**:
```bash
python evaluate_rotatingslats.py 2>&1 | Select-String -Pattern "80fd9f48|Targets.*11.327"
```

### 2. Verify Slats Original Chain
**Expected**: 
- Rectangle 2Pt outputs geometry dict (not string)
- First Move "Slats original" receives geometry dict
- Area component outputs correct area and centroid

**Check**:
```bash
python trace_slats_geometry_chain.py 2>&1 | Select-String -Pattern "Rectangle|First Move|Geometry|STRING"
```

### 3. Verify Polar Array Rotation
**Expected**: Polar Array rotates geometry correctly (Y-coordinate changes)

**Check**: Compare Y-coordinates before and after Polar Array in Targets chain

### 4. Verify Component Count
**Expected**: All 151 components evaluate without errors

**Check**:
```bash
python evaluate_rotatingslats.py 2>&1 | Select-String -Pattern "Total components"
```

## Current Issue: Rectangle 2Pt Output Extraction

### Problem Description
The first Move "Slats original" component (`ddb9e6ae...`) receives its Geometry input from Rectangle 2Pt (`a3eb185f...`). The Rectangle 2Pt outputs:
```python
{'Rectangle': {geometry_dict}, 'Length': ...}
```

But the Move component receives the string `'rectangle'` instead of the geometry dict.

### Root Cause Analysis Needed
1. Check how output parameter `dbc236d4...` (Rectangle output) is stored in `evaluated`
2. Check how `resolve_input_value()` extracts the value from Rectangle 2Pt output
3. Verify if the output parameter GUID is stored directly or if parent component GUID is used

### Affected Code Sections
- `evaluate_rotatingslats.py` lines 243-277: Output parameter value extraction
- `evaluate_rotatingslats.py` lines 1355-1390: Move component Geometry input resolution

### Debugging Script
Use `trace_slats_geometry_chain.py` to trace the exact flow:
```bash
python trace_slats_geometry_chain.py
```

This will show:
- Rectangle 2Pt output structure
- How Geometry input is resolved for first Move
- What value is actually received

## File Structure

```
shade/
├── evaluate_rotatingslats.py      # Main evaluation engine
├── gh_components.py              # Component implementations
├── parse_ghx_v2.py              # GHX XML parser
├── complete_component_graph.json # Dependency graph
├── rotatingslats_data.json       # Component data
├── external_inputs.json          # External input values
├── evaluation_results.md         # Evaluation results table
├── trace_slats_geometry_chain.py # Debug script for Slats chain
└── trace_complete_targets_chain.py # Debug script for Targets chain
```

## Key Functions

### `evaluate_rotatingslats.py`
- `load_component_graph()`: Loads dependency graph
- `get_external_inputs()`: Loads external input values
- `topological_sort()`: Orders components by dependencies
- `resolve_input_value()`: Resolves input values from sources
- `evaluate_component()`: Evaluates a single component

### `gh_components.py`
- `move_component()`: Moves geometry by motion vector
- `polar_array_component()`: Creates polar array with rotation
- `area_component()`: Computes area and centroid
- `rectangle_2pt_component()`: Creates rectangle from 2 points

## Next Steps

1. **Fix Rectangle 2Pt Output Extraction**:
   - Trace the exact flow from Rectangle 2Pt output to Move input
   - Ensure output parameter extraction correctly gets the 'Rectangle' key value
   - Test that geometry dict is passed correctly

2. **Verify All Chains**:
   - Ensure Targets chain still works after fixes
   - Verify Slats original chain works end-to-end
   - Check that Area component receives correct geometry

3. **Handle Edge Cases**:
   - List Item components returning None
   - Area components with 0.0 area
   - Empty lists in component outputs

## Notes

- The user recently reverted changes that added 'Rectangle' to general key extraction lists
- The fix should be targeted to only the specific Rectangle 2Pt → Move chain
- Other components that were working should remain unaffected
- Always test both "Targets" and "Slats original" chains after any changes

