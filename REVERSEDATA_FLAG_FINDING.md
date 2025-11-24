# ReverseData Flag - Missing Implementation

## Critical Finding

The GHX file contains a **`ReverseData="true"`** flag on parameter inputs that our parser is NOT extracting or applying!

## Location in GHX

**File**: `refactored-no-sun.ghx`  
**Line**: 11782  
**Component**: PolyLine (GUID: 910c335c-b5e8-41bf-bfb4-576cb17432c7)  
**Position**: (11867, 3064)

```xml
<item name="ReverseData" type_name="gh_bool" type_code="1">true</item>
```

This flag is on the **Vertices** input parameter of the second PolyLine component.

## What ReverseData Does

In Grasshopper, when `ReverseData=true` is set on an input parameter:
- The data received from the source is reversed before being used
- For a list input, the order of items is reversed
- This affects how components process the data

## Current Implementation Gap

### Our Parser (`parse_refactored_ghx.py`)
- ✗ Does NOT extract the `ReverseData` flag
- Only extracts: `name`, `type`, `persistent_data`, `sources`, `expression`, `mapping`

### Our Evaluator (`gh_evaluator_wired.py`)
- ✗ Does NOT apply data reversal
- Even if we parse it, we're not reversing the data before passing it to components

## Impact on PolyLine

### Second PolyLine (with ReverseData=true)
**Current vertices order** (NOT reversed):
```
First: [0, 0.07, 3.8]
Last:  [0, 0.07, 3.1]
Direction: (0, 0, -1)
```

**Should be** (with reversal):
```
First: [0, 0.07, 3.1]
Last:  [0, 0.07, 3.8]
Direction: (0, 0, 1)
```

## Impact on Plane Normal and Angle Calculation

However, even with ReverseData implemented, this particular PolyLine would give direction `(0, 0, 1)`, which still doesn't match the screenshot's `(-1, 0, 0)`.

The screenshot showing `(-1, 0, 0)` comes from the **second Plane Normal** (at position 12184, 3075) which uses **Construct Plane** as input (not either PolyLine).

## Required Fixes

### 1. Parser Update
Add `ReverseData` extraction to `parse_refactored_ghx.py`:

```python
def extract_parameter_from_chunk(param_chunk, param_type):
    # ... existing code ...
    
    # Extract ReverseData flag (default to False)
    reverse_data = items.get('ReverseData', 'false')
    try:
        reverse_data = reverse_data.lower() == 'true'
    except:
        reverse_data = False
    
    param = {
        'param_guid': param_guid,
        'name': name,
        'type': param_type,
        'persistent_data': persistent_data,
        'sources': sources,
        'expression': expression,
        'mapping': mapping,
        'reverse_data': reverse_data  # NEW
    }
```

### 2. Evaluator Update
Apply reversal in `gh_evaluator_wired.py`:

```python
def resolve_input(param: dict, context: EvaluationContext, 
                 external_inputs: Dict[str, any]) -> DataTree:
    # ... existing resolution logic ...
    
    # Apply ReverseData if flagged
    if param.get('reverse_data', False):
        resolved_data_tree = reverse_data_tree(resolved_data_tree)
    
    return resolved_data_tree

def reverse_data_tree(data_tree: DataTree) -> DataTree:
    """Reverse the items in each branch of a DataTree."""
    result = DataTree()
    for path in data_tree.get_paths():
        items = data_tree.get_branch(path)
        result.set_branch(path, list(reversed(items)))
    return result
```

## Broader Question

Since implementing ReverseData won't fix the angle mismatch (we'd get `(0,0,1)` not `(-1,0,0)`), the real question is:

**Are the screenshots showing the correct/expected output for the current GHX file?**

Or:
- Has the GHX been modified since the screenshots were taken?
- Are the screenshots showing a different part of the graph?
- Should the Angle Vector A be using a different Plane Normal?

---

**Status**: ReverseData flag found but not implemented  
**Priority**: HIGH - This is a fundamental Grasshopper feature  
**Next Steps**: 
1. Implement ReverseData parsing and application
2. Clarify which Plane Normal should feed the Angle Vector A
3. Re-evaluate with all flags correctly applied

