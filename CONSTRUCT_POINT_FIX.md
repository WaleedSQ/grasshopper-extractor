# Construct Point Fix - External Input Bug

## Issue
Construct Point component (GUID: 9754db2b-c513-48b6-bbf7-0d06f53b3ce4) was outputting `[0, 0, 0]` instead of the expected `[0, 4.5, 4.0]`.

## Root Causes

### Bug 1: External Input Loading ❌
**Location:** `gh_evaluator_wired.py` lines 342-354  

**Problem:** When loading external inputs from `rotatingslats_inputs.json`, the code attempted to find a `params` field to extract output parameter GUIDs:

```python
for param in input_data.get('params', []):  # params doesn't exist for sliders!
    if param.get('type') == 'output':
        param_guid = param.get('param_guid')
        if param_guid:
            external_inputs[param_guid] = input_data['data']
```

For Number Sliders, the JSON structure is:
```json
{
  "guid": "125e7c20-d243-4cdc-927b-568ceb6315b5",
  "type": "Number Slider",
  "nickname": "Last target from slats",
  "data": [4.5]
}
```

There is NO `params` field - the `guid` field IS the output parameter GUID.

**Fix:** ✅
```python
# For sliders/panels, the GUID itself is both component AND parameter GUID
external_inputs[input_data['guid']] = input_data['data']
```

### Bug 2: Parameter Name Mismatch ❌
**Location:** `gh_components_rotatingslats.py` lines 463-465

**Problem:** Construct Point implementation used incorrect parameter names:

```python
x_tree = inputs.get('X', DataTree.from_scalar(0))      # WRONG
y_tree = inputs.get('Y', DataTree.from_scalar(0))      # WRONG
z_tree = inputs.get('Z', DataTree.from_scalar(0))      # WRONG
```

But the actual GHX parameters (lines 12828, 12874, 12921) are named:
- `X coordinate`
- `Y coordinate`
- `Z coordinate`

**Fix:** ✅
```python
x_tree = inputs.get('X coordinate', DataTree.from_scalar(0))
y_tree = inputs.get('Y coordinate', DataTree.from_scalar(0))
z_tree = inputs.get('Z coordinate', DataTree.from_scalar(0))
```

## Verification

### Before Fix:
```json
{
  "Point": {
    "branches": {
      "(0,)": [[0, 0, 0]]
    }
  }
}
```

### After Fix: ✅
```json
{
  "Point": {
    "branches": {
      "(0,)": [[0, 4.5, 4.0]]
    }
  }
}
```

## Impact
- ✅ External slider inputs now work correctly
- ✅ Construct Point uses correct parameter names
- ✅ Component outputs match Grasshopper exactly
- ✅ All 56/56 components still evaluate successfully

## Lessons Learned
1. **Parameter names must match GHX exactly** - even small differences like "X" vs "X coordinate" cause silent failures
2. **External inputs from sliders** - the slider's GUID is both the component GUID and the output parameter GUID
3. **Always verify against source GHX** - implementation assumptions must be validated against actual XML structure

---

*Fixed: November 22, 2025*  
*Status: VERIFIED ✅*

