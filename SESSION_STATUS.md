# Rotatingslats Reconstruction - Session Status

## Current Progress ✅

### Completed Components
- **78 components** loaded in the dependency graph
- **Topological sort** working correctly
- **Negative component** now working (fixed 0.0 falsy value issue)
- **Number Slider** input resolution working
- **External inputs** extraction complete

### Key Fixes Applied
1. ✅ Fixed `resolve_input_value` to check both `'guid'` and `'source_guid'` keys
2. ✅ Fixed input resolution to prefer `inputs` structure sources (have `source_guid`)
3. ✅ Fixed Negative component to check `value is None` instead of `or` (0.0 is falsy!)
4. ✅ Added Number component source dependencies to topological sort
5. ✅ Added missing Negative and Division components to graph

## Current Issue 🔧

**Number component "Distance between slats" (06d478b1...)** needs value from:
- **Panel** (d019d2ee...) which has **Source** connection to:
- **Output parameter** (20f5465a...) from:
- **Division component** (f9a68fee...) - **NOT IN GRAPH**

The Division component `f9a68fee-bd6c-477a-9d8e-ae9e35697ab1` needs to be added to the graph.

## Key Findings from Screenshot/GHX Analysis

### Division/Subtraction Chain Structure
From the GHX file and screenshot:
1. **Subtraction component** (e11dd9b3...):
   - Input A: `537142d8...` = "Number of slats" (10.0) ✅
   - Input B: Constant = 1 ✅
   - Output Result: `a7dd54c8...` → Division Input B

2. **Division component** (524ba570...):
   - Input A: `8cb00f94...` (from another Subtraction)
   - Input B: `a7dd54c8...` (from Subtraction above)
   - Output Result: `133aa1b3...`

3. **Another Division component** (f9a68fee...):
   - Output Result: `20f5465a...` → Panel "Distance between slats" source
   - **This component is NOT in the graph!**

## Files and Their Purposes

### Core Files
- `evaluate_rotatingslats.py` - Main evaluator with graph-based evaluation
- `gh_components.py` - Component function implementations (25+ types)
- `rebuild_complete_graph.py` - Builds complete dependency graph
- `parse_ghx_v2.py` - Parses GHX file and extracts component data

### Data Files
- `rotatingslats_data.json` - Extracted Rotatingslats group data
- `complete_component_graph.json` - Full dependency graph (78 components)
- `external_inputs.json` - All external inputs (sliders, panels, constants)
- `number_component_sources.json` - Number component Source connections

### Helper Scripts (for tracing)
- `find_panel_source.py` - Find what Panel sources point to
- `trace_panel_sources.py` - Trace Panel Source connections
- `analyze_division_subtraction_chain.py` - Analyze component chains

## Next Steps

### Immediate
1. **Add Division component `f9a68fee...` to graph**
   - It's the parent of output parameter `20f5465a...`
   - Panel `d019d2ee...` needs this value
   - Update `rebuild_complete_graph.py` to add Panel source components

2. **Fix indentation error in `rebuild_complete_graph.py`** (line 311)

3. **Continue evaluation chain** - handle remaining Panel sources

### Future
- Extract Value List "Orientations" values from screenshots
- Verify final angle outputs against screenshots
- Handle any remaining missing component types

## Important Code Patterns

### Input Resolution Order
```python
1. Check constant values (persistent_values, values)
2. Check sources -> external_inputs (by GUID or object_guid)
3. Check sources -> output_params -> parent component
4. Check sources -> evaluated components
5. Check external_inputs by component GUID
```

### Component Input Structure
- `comp_info['inputs']` has sources with `'source_guid'` key
- `comp_info['obj']['params']` has sources with `'guid'` key
- Always prefer `inputs` structure for sources (has `source_guid`)

### Falsy Value Bug
- **Fixed**: `value = inputs.get('Value') or inputs.get('Number')` fails when value is 0.0
- **Solution**: Check `if value is None:` explicitly

## Component Types Implemented

✅ Angle, Degrees, Line, Plane, Vector 2Pt, Unitize, Construct Point, Point
✅ Addition, Subtraction, Multiply, Division, Negative
✅ Series, List Item, Value List
✅ Number, Number Slider, MD Slider
✅ Surface, Area, Move, Polar Array
✅ Box 2Pt, Rectangle 2Pt, PolyLine, Deconstruct Brep, Point On Curve

## External Inputs Extracted

✅ Room width = 5.0
✅ Number of slats = 10.0
✅ Horizontal shift between slats = 0.0
✅ All Number Slider values
✅ Number component Source connections

## Remaining Issues

1. **Panel sources** - Need to trace and add parent components to graph
2. **Value List "Orientations"** - Needs values from screenshots
3. **Some Division/Subtraction components** - Not in graph, need to add

## Evaluation Status

- ✅ Graph building: Working
- ✅ Topological sort: Working
- ✅ Input resolution: Working (with fixes)
- ✅ Component evaluation: Working
- ⚠️ Missing components: Some Division components not in graph
- ⚠️ Panel sources: Need tracing and graph updates

## Quick Commands

```bash
# Rebuild graph
python rebuild_complete_graph.py

# Run evaluator
python evaluate_rotatingslats.py

# Find Panel source
python find_panel_source.py

# Trace Panel sources
python trace_panel_sources.py
```

