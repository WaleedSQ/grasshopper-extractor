# ROOT CAUSE: Missing Graft/Flatten Implementation

## Executive Summary

**The angle values are all identical because the evaluator does not implement Grasshopper's Graft/Flatten data tree operations.**

Specifically, the **Project component has `Mapping=1` (Graft) on its output**, which should split 10 curves into 10 branches, but our evaluator outputs them as 1 branch with 10 items.

---

## Complete Chain Analysis

### Expected Behavior (with Graft):
```
Project: "Project" 
  Output: Curve [Mapping=1 = GRAFT]
  → Should output: 10 branches {0;0}, {0;1}, ..., {0;9} with 1 curve each
  ↓
Divide Length: "DL"
  → Processes each branch separately
  → Should output: 10 branches with 51 points each
  ↓
List Item: "LI" [Index=1]
  → Extracts item[1] from EACH of the 10 branches
  → Should output: 10 different points (one from each branch)
  ↓
Line: "Between"
  → Creates 10 different lines
  ↓
Angle
  → Calculates 10 different angles
  ✓ Result: [43.7°, 41.2°, ..., 23.0°]
```

### Current Behavior (without Graft):
```
Project: "Project"
  Output: Curve [Mapping=1 IGNORED]
  → Actually outputs: 1 branch {0} with 10 curves
  ↓
Divide Length: "DL"
  → Processes the single branch with all 10 curves mixed
  → Outputs: 1 branch {0} with 510 points (all curves combined)
  ↓
List Item: "LI" [Index=1]
  → Extracts item[1] from the SINGLE branch
  → Outputs: 1 point
  ↓
Line: "Between"
  → Creates 1 line (replicated to 10 by Angle's grafted inputs)
  ↓
Angle
  → Calculates angle with same line 10 times
  ✗ Result: [43.67°, 43.67°, ..., 43.67°] (all identical!)
```

---

## GHX Evidence

### Project Component (GUID: 9cd053c9-3dd2-432b-aa46-a29a4b05c339)

**Line 5431: Curve INPUT**
```xml
<item name="Mapping" type_name="gh_int32" type_code="3">2</item>
```
→ Mapping=2 = **FLATTEN** (input)

**Line 5538: Curve OUTPUT**
```xml
<item name="Mapping" type_name="gh_int32" type_code="3">1</item>
```
→ Mapping=1 = **GRAFT** (output) ← **THIS IS THE CRITICAL ONE!**

### Line Component "In Ray" (GUID: c7dba531-36f1-4a2d-8e0e-ed94b3873bba)

**Line 5898: Start Point INPUT**
```xml
<item name="Mapping" type_name="gh_int32" type_code="3">1</item>
```
→ Mapping=1 = **GRAFT** (input)

**Output "Line" has NO Mapping** → Default (0)

---

## Mapping Values

| Value | Meaning | Effect |
|-------|---------|--------|
| 0 | None (default) | No operation, pass data tree as-is |
| 1 | Graft | Each item becomes its own branch |
| 2 | Flatten | All items merged into one branch |

---

## Current Parser/Evaluator Issues

### Issue 1: Parser Does Not Extract Mapping
**File**: `parse_refactored_ghx.py`
**Problem**: The `extract_param_data()` function does not read the `Mapping` item from parameters.

**Fix Required**:
```python
def extract_param_data(param_chunk, param_type):
    # ... existing code ...
    mapping = items.get('Mapping', 0)  # Add this line
    
    param = {
        'param_guid': param_guid,
        'name': name,
        'type': param_type,
        'persistent_data': persistent_data,
        'sources': sources,
        'expression': expression,
        'mapping': mapping  # Add this line
    }
    return param
```

### Issue 2: Evaluator Does Not Apply Graft/Flatten
**File**: `gh_evaluator_wired.py`
**Problem**: After a component is evaluated, the output DataTree is not grafted/flattened based on the output parameter's `mapping` value.

**Fix Required**:
Add a function to apply mapping:
```python
def apply_mapping(data_tree: DataTree, mapping: int) -> DataTree:
    """
    Apply Graft/Flatten to a DataTree
    
    mapping:
        0 = None (return as-is)
        1 = Graft (each item gets its own branch)
        2 = Flatten (all items in one branch)
    """
    if mapping == 0:
        return data_tree
    
    elif mapping == 1:  # GRAFT
        result = DataTree()
        for path in data_tree.get_paths():
            items = data_tree.get_branch(path)
            for i, item in enumerate(items):
                new_path = path + (i,)  # Append index to path
                result.set_branch(new_path, [item])
        return result
    
    elif mapping == 2:  # FLATTEN
        all_items = []
        for path in data_tree.get_paths():
            all_items.extend(data_tree.get_branch(path))
        result = DataTree()
        result.set_branch((0,), all_items)
        return result
    
    return data_tree
```

Then, after component evaluation, apply mapping to each output:
```python
# In evaluate_component()
outputs = eval_func(resolved_inputs)

# Apply mapping to outputs
mapped_outputs = {}
for output_name, output_tree in outputs.items():
    # Find the output parameter definition
    output_param = next((p for p in component['params'] 
                         if p['type'] == 'output' and p['name'] == output_name), None)
    if output_param:
        mapping = output_param.get('mapping', 0)
        mapped_outputs[output_name] = apply_mapping(output_tree, mapping)
    else:
        mapped_outputs[output_name] = output_tree

return mapped_outputs
```

---

## Impact

### Components Affected
All components that have non-zero `Mapping` on their input or output parameters.

### Criticality
**HIGH** - This is a fundamental Grasshopper feature that affects data tree structure throughout the graph. Without it, many calculations produce incorrect results.

### Other Potential Issues
- The Angle component also has `Mapping=1` (Graft) on its Vector A and Vector B inputs (confirmed in GHX line 7854, 7866)
- This creates cross-product matching, which we've partially worked around but not properly implemented
- There may be dozens of other components in the full graph affected by missing Graft/Flatten

---

## Solution Priority

### Phase 1: Parse Mapping (Required)
Update `parse_refactored_ghx.py` to extract the `Mapping` field for all parameters.

### Phase 2: Implement Graft/Flatten (Required)
Update `gh_evaluator_wired.py` to:
1. Implement `apply_mapping()` function
2. Apply mapping after component evaluation for outputs
3. Apply mapping before component evaluation for inputs (if needed)

### Phase 3: Re-evaluate (Required)
Re-run the evaluator and verify:
- Project outputs 10 branches
- DL outputs 10 branches with ~51 points each
- List Item extracts 10 different points
- Angle calculates 10 different angles

### Phase 4: Full Validation
Check all other components for Mapping values and verify correct behavior.

---

## Expected Results After Fix

### DL Points Output
```
Branch {0;0}: [51 points for slat 0]
Branch {0;1}: [51 points for slat 1]
...
Branch {0;9}: [51 points for slat 9]
```

### List Item Output (Index=1)
```
Branch {0;0}: [Point from slat 0]
Branch {0;1}: [Point from slat 1]
...
Branch {0;9}: [Point from slat 9]
```

### Angle Output
```
Branch {0;0}: [43.67°]
Branch {0;1}: [41.23°]
...
Branch {0;9}: [23.02°]
```

### Degrees Output
```
Branch {0;0}: [43.67]
Branch {0;1}: [41.23]
...
Branch {0;9}: [23.02]
```

---

## Additional Notes

### Grafting on Inputs vs Outputs
- **Graft on INPUT**: Affects how the component receives data (splits before processing)
- **Graft on OUTPUT**: Affects how the component sends data (splits after processing)

Both need to be implemented for complete Grasshopper compatibility.

### Data Matching
With proper grafting, Grasshopper performs cross-product matching:
- If component A outputs 10 branches (grafted)
- And component B receives this with grafted input
- The data structure is preserved through the chain

This is WHY the Angle component has grafting on its inputs - to preserve the 10-branch structure created upstream!

---

**Date**: November 22, 2025  
**Status**: ROOT CAUSE IDENTIFIED - FIX PENDING  
**Priority**: CRITICAL

