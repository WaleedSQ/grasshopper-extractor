# Critical Issues Found: Expressions & Plane Normal

## Issue 1: Parameter Expressions NOT Implemented ⚠️

### Discovery
List Item component (GUID: `9ff79870...`) has expression `x-1` on Index parameter (GHX line 7506):
```xml
<item name="InternalExpression" type_name="gh_string" type_code="10">x-1</item>
```

### Impact
- **List Item** outputs 1 item instead of 10 items
- **Plane Normal** receives 1 origin instead of 10 origins
- **Angle** component receives all identical inputs instead of varying inputs

### Current Behavior
- Index persistent data: `[0]`
- Expression: `x-1` (NOT evaluated)
- Actual index used: `0`
- List Item output: Item at index 0 → `[0.0, 0.07, 3.8]`

### Expected Behavior
- Index persistent data: `[0]`
- Expression: `x-1` applied
- Transformed index: `-1`
- With Wrap=True: wraps to index `9`
- List Item output: Item at index 9 → `[0.0, 0.07, 3.1]`

OR if expression applies to a range:
- If Index somehow receives `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]`
- Expression `x-1` transforms to `[-1, 0, 1, 2, 3, 4, 5, 6, 7, 8]`
- With Wrap=True: `[9, 0, 1, 2, 3, 4, 5, 6, 7, 8]`
- List Item outputs 10 items

---

## Issue 2: Plane Normal Z-Axis Mismatch

### Current Output
```
Origin: (0.00, 0.07, 3.80) - Only 1 value, should be 10
Z-Axis: (0.00, 0.00, 1.00) - Wrong direction!
```

### Expected Output (from screenshot)
```
10 locally defined values:
Origin: (0.00, 0.07, 3.10) - Should vary from 3.8 to 3.1
Z-Axis: (-1.00, 0.00, 0.00) - Should point in -X direction
```

### Root Causes

#### 2a. Origin - Cascading from Issue 1
- List Item with expression outputs 1 item (3.8) instead of 10 items (3.8 to 3.1)
- Plane Normal receives only 1 origin point
- Result: All 10 planes have same origin

#### 2b. Z-Axis - Wrong Value Extraction
- Plane Normal receives 10 planes from Construct Plane
- Implementation extracts Z-axis from plane dict
- But getting `(0, 0, 1)` instead of `(-1, 0, 0)`

Let me check Construct Plane output:

**Construct Plane** (GUID: `30f76ec5...`) outputs 10 planes.
Need to verify what Z-axis these planes actually have.

---

## Parser Updates Needed

### 1. Extract `InternalExpression` from Parameters

**Current parser** (`parse_refactored_ghx.py`):
- ✅ Extracts: Name, Description, Optional, SourceCount, Sources, PersistentData
- ❌ Missing: InternalExpression, Mapping, Access

**Add to parser**:
```python
param_dict['expression'] = items.get('InternalExpression', None)
param_dict['mapping'] = items.get('Mapping', 0)  # 0=none, 1=graft, 2=flatten
```

### 2. Implement Expression Evaluation

**Expression Engine Needed**:
- Parse simple expressions: `x-1`, `x+1`, `x*2`, etc.
- Variable `x` refers to the parameter's input value
- Apply expression to each item in DataTree
- Handle both scalar and list inputs

**Example**:
```python
def evaluate_expression(expr, input_value):
    if expr is None:
        return input_value
    
    # Simple eval (UNSAFE for production, needs proper parser)
    x = input_value
    return eval(expr)  # Danger! Need safe expression evaluator
```

---

## Implementation Options

### Option A: Minimal Fix for This Specific Case
1. Hard-code the expression evaluation for this one List Item
2. Manually apply `x-1` transformation
3. Quick but not scalable

### Option B: Basic Expression Support
1. Implement simple expression parser (+-*/ operators only)
2. Apply to parameter inputs before component evaluation
3. Handles most common cases

### Option C: Full Grasshopper Expression Engine
1. Implement complete Grasshopper expression syntax
2. Support variables, functions, conditionals
3. Significant effort, production-ready

---

## Recommended Approach

**Phase 1: Immediate Fix**
1. Update parser to extract `InternalExpression`
2. For this specific List Item, manually handle `x-1` case
3. Fix Construct Plane Z-axis extraction

**Phase 2: Expression Engine**
1. Implement safe expression evaluator
2. Support basic arithmetic: `+`, `-`, `*`, `/`, `()`
3. Apply expressions in `resolve_input()` function

---

## Testing Checklist

After implementing expressions:

- [ ] List Item with `x-1` outputs 10 items (not 1)
- [ ] Plane Normal receives 10 different origins
- [ ] Plane Normal outputs correct Z-axis `(-1, 0, 0)`
- [ ] Angle component receives 10 varying inputs
- [ ] Degrees outputs 10 different values (43.7° to 23.0°)

---

*Analysis Date: November 22, 2025*  
*Status: Critical feature missing - expressions not implemented*

