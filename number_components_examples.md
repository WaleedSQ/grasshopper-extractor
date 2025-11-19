# Examples of Number Components Without Direct Values

## Summary

Number components in Grasshopper can get their values in two ways:
1. **Direct value** - stored in the component itself (like a constant)
2. **Source connection** - value comes from another component (indicated by a `Source` item in the GHX)

## Examples Found

### 1. "Slats hight" (GUID: 0554769c-8547-45c4-b96b-c1aef99b5d53)
- **Type**: Number component
- **Has direct value**: ❌ No
- **Has source**: ✅ Yes
- **Source GUID**: `456d176f-14cf-4134-9062-b4623202c00e`
- **Source component**: Number Slider "Slats height (top)" (external to Rotatingslats group)
- **Source value**: 3.8 (already extracted in external_inputs.json)
- **Issue**: The evaluator needs to resolve the source connection instead of looking for a direct value

### 2. "Horisontal shift between slats" (GUID: d1793081...)
- **Type**: Number component
- **Has direct value**: ❌ No
- **Has source**: ✅ Yes
- **Source**: Output parameter from a Negative component's "Result" output
- **Issue**: The evaluator needs to trace back through the Negative component

### 3. "Slat lenght" (GUID: fadbd125...)
- **Type**: Number component
- **Has direct value**: ❌ No
- **Has source**: ✅ Yes
- **Source**: Output parameter from a Division component's "Result" output
- **Issue**: The evaluator needs to trace back through the Division component

### 4. "Number of slats" (GUID: 2959ea40-ab1b-4321-979b-7101ceda46d6)
- **Type**: Number component
- **Has direct value**: ❌ No
- **Has source**: ✅ Yes
- **Source GUID**: `537142d8...`
- **Note**: This source is likely a Number Slider outside the group

### 5. "Distance between slats" (GUID: 06d478b1-5fdf-4861-8f0e-1772b5bbf067)
- **Type**: Number component
- **Has direct value**: ❌ No
- **Has source**: ✅ Yes
- **Source**: Panel "Distance between slats"
- **Note**: Panels can contain values that need to be extracted

## Solution

The evaluator needs to be updated to:
1. Check if a Number component has a `Source` connection
2. If it has a source, resolve that source's value instead of looking for a direct value
3. Handle sources that are:
   - External sliders (already in external_inputs.json)
   - Output parameters from other components
   - Panels with stored values

## Code Location

The issue is in `evaluate_rotatingslats.py` in the `resolve_input_value` function and `evaluate_component` function for Number components. Currently, it only checks for:
- Constant values in params
- External inputs by GUID
- Source connections in params

But Number components with a `Source` item in the GHX need special handling - they should resolve the source component's output value.

