# Guide: Adding New Components to the Evaluator

This guide provides step-by-step instructions for adding new Grasshopper components when the GHX file is updated with new components and wirings.

## Table of Contents

1. [Identifying New Components](#1-identifying-new-components)
2. [Understanding Component Structure](#2-understanding-component-structure)
3. [Component Implementation Pattern](#3-component-implementation-pattern)
4. [Step-by-Step Implementation](#4-step-by-step-implementation)
5. [Data Tree Handling](#5-data-tree-handling)
6. [Input/Output Mapping](#6-inputoutput-mapping)
7. [Testing New Components](#7-testing-new-components)
8. [Common Patterns and Examples](#8-common-patterns-and-examples)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Identifying New Components

### Step 1.1: Parse the Updated GHX File

```bash
python parse_refactored_ghx.py
```

This generates `ghx_graph.json` with all components from the updated GHX file.

### Step 1.2: Find Unregistered Components

Check which components are not yet implemented:

```python
# Check registered components
from gh_evaluator_core import COMPONENT_REGISTRY
registered = COMPONENT_REGISTRY.list_registered()

# Load graph and find unregistered types
import json
with open('ghx_graph.json') as f:
    graph = json.load(f)

all_types = set()
for comp in graph['components']:
    all_types.add(comp['type_name'])

unregistered = sorted(all_types - set(registered))
print("Unregistered components:", unregistered)
```

### Step 1.3: Identify Component Usage

Find where the new component is used in the graph:

```python
# Find components of specific type
target_type = "YourNewComponent"
for comp in graph['components']:
    if comp['type_name'] == target_type:
        print(f"GUID: {comp['guid']}")
        print(f"Nickname: {comp.get('nickname', 'N/A')}")
        print(f"Inputs: {[p['name'] for p in comp['params'] if p['type'] == 'input']}")
        print(f"Outputs: {[p['name'] for p in comp['params'] if p['type'] == 'output']}")
        print("---")
```

---

## 2. Understanding Component Structure

### Component Definition from GHX

Each component in `ghx_graph.json` has this structure:

```json
{
  "guid": "component-guid",
  "type_name": "ComponentType",
  "nickname": "Component Nickname",
  "container": "group-guid-or-null",
  "position": {"x": 100, "y": 200},
  "params": [
    {
      "type": "input",
      "name": "InputName",
      "param_guid": "param-guid",
      "mapping": 0,  // 0=None, 1=Graft, 2=Flatten
      "reverse_data": false,
      "sources": [...]  // Wire connections
    },
    {
      "type": "output",
      "name": "OutputName",
      "param_guid": "param-guid"
    }
  ]
}
```

### Key Fields to Understand

- **`type_name`**: Exact component type name (must match Grasshopper)
- **`params`**: List of input/output parameters
- **`mapping`**: Data tree mapping (0=None, 1=Graft, 2=Flatten)
- **`reverse_data`**: Whether to reverse data order
- **`sources`**: Wire connections from other components

---

## 3. Component Implementation Pattern

### Standard Function Signature

All component functions follow this pattern:

```python
@COMPONENT_REGISTRY.register("ComponentType")
def evaluate_component_type(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH ComponentType component: brief description.
    
    Inputs:
        InputName1: Description of input 1
        InputName2: Description of input 2
    
    Outputs:
        OutputName: Description of output
    
    Grasshopper Behavior:
        - Document exact GH behavior
        - Note any special cases
    """
    # Implementation here
    pass
```

### Required Imports

```python
import math
from typing import Dict, List, Tuple
from gh_evaluator_core import DataTree, match_longest, COMPONENT_REGISTRY
```

---

## 4. Step-by-Step Implementation

### Step 4.1: Extract Input DataTrees

```python
# Get input DataTrees (with defaults if missing)
input1_tree = inputs.get('InputName1', DataTree.from_scalar(default_value))
input2_tree = inputs.get('InputName2', DataTree.from_scalar(default_value))
```

### Step 4.2: Match Input DataTrees

For components with multiple inputs, use `match_longest`:

```python
# Match inputs using longest list strategy
input1_matched, input2_matched = match_longest(input1_tree, input2_tree)
```

**Why**: Grasshopper uses "Longest List" strategy - shorter lists are replicated to match the longest.

### Step 4.3: Process Branch by Branch

```python
result = DataTree()
for path in input1_matched.get_paths():
    items1 = input1_matched.get_branch(path)
    items2 = input2_matched.get_branch(path)
    
    result_items = []
    for item1, item2 in zip(items1, items2):
        # Process each item pair
        result_item = process_items(item1, item2)
        result_items.append(result_item)
    
    result.set_branch(path, result_items)
```

### Step 4.4: Return Output Dictionary

```python
return {'OutputName': result}
```

---

## 5. Data Tree Handling

### DataTree Basics

- **Branch**: A path like `(0,)`, `(0, 0)`, `(0, 1)`, etc.
- **Items**: List of values in each branch
- **Path**: Tuple representing hierarchical structure

### Common Operations

```python
# Create DataTree
tree = DataTree()

# Set branch
tree.set_branch((0,), [1, 2, 3])
tree.set_branch((0, 0), [4, 5])

# Get branch
items = tree.get_branch((0,))

# Get all paths
paths = tree.get_paths()

# Create from scalar
scalar_tree = DataTree.from_scalar(42)

# Create from list
list_tree = DataTree.from_list([1, 2, 3])  # Creates branch (0,) with 3 items
```

### Handling Different Input Structures

**Case 1: Single Input**
```python
input_tree = inputs.get('Input', DataTree.from_scalar(0))
# Process directly, no matching needed
```

**Case 2: Multiple Inputs**
```python
input1_tree = inputs.get('Input1', DataTree.from_scalar(0))
input2_tree = inputs.get('Input2', DataTree.from_scalar(0))
input1_matched, input2_matched = match_longest(input1_tree, input2_tree)
```

**Case 3: Variable Number of Inputs**
```python
# For components that accept lists of inputs
input_trees = [inputs.get(f'Input{i}', DataTree()) for i in range(n)]
matched_trees = match_longest(*input_trees)
```

---

## 6. Input/Output Mapping

### Input Mapping (Graft/Flatten)

Input mapping is **automatically applied** by `gh_evaluator_wired.py` before your function is called. You receive already-mapped DataTrees.

**Mapping Values**:
- `0`: None (no transformation)
- `1`: Graft (each item gets its own branch)
- `2`: Flatten (all items merged into single branch)

### Output Mapping

Output mapping is **automatically applied** by `gh_evaluator_wired.py` after your function returns. You don't need to handle it.

### Reverse Data

If `reverse_data=true` on an input parameter, the data order is reversed before your function receives it. This is handled automatically.

---

## 7. Testing New Components

### Step 7.1: Test with Isolated Component

Create a test script:

```python
from gh_components_rotatingslats import *
from gh_evaluator_core import DataTree

# Test your component
inputs = {
    'Input1': DataTree.from_scalar(10),
    'Input2': DataTree.from_scalar(5)
}

outputs = evaluate_your_component(inputs)
print("Output:", outputs)
```

### Step 7.2: Test in Full Pipeline

1. Ensure component is registered:
```python
from gh_evaluator_core import COMPONENT_REGISTRY
print("Registered:", COMPONENT_REGISTRY.is_registered("YourComponent"))
```

2. Run full pipeline:
```bash
python parse_refactored_ghx.py
python isolate_rotatingslats.py
python gh_evaluator_wired.py
```

3. Check results:
```python
import json
with open('rotatingslats_evaluation_results.json') as f:
    results = json.load(f)

# Find your component's GUID from ghx_graph.json
your_comp_guid = "your-component-guid"
if your_comp_guid in results:
    print("Component evaluated successfully!")
    print("Outputs:", results[your_comp_guid]['outputs'])
else:
    print("Component not found in results")
```

### Step 7.3: Compare with Grasshopper

1. Open the GHX file in Grasshopper
2. Check the component's output values
3. Compare with `rotatingslats_evaluation_results.json`
4. Verify values match exactly

---

## 8. Common Patterns and Examples

### Pattern 1: Simple Arithmetic (Two Inputs)

```python
@COMPONENT_REGISTRY.register("Addition")
def evaluate_addition(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """GH Addition component (A + B)."""
    a_tree = inputs.get('A', DataTree.from_scalar(0))
    b_tree = inputs.get('B', DataTree.from_scalar(0))
    
    a_matched, b_matched = match_longest(a_tree, b_tree)
    
    result = DataTree()
    for path in a_matched.get_paths():
        a_items = a_matched.get_branch(path)
        b_items = b_matched.get_branch(path)
        
        result_items = [a_val + b_val for a_val, b_val in zip(a_items, b_items)]
        result.set_branch(path, result_items)
    
    return {'Result': result}
```

### Pattern 2: Single Input Transformation

```python
@COMPONENT_REGISTRY.register("Negative")
def evaluate_negative(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """GH Negative component (-x)."""
    value_tree = inputs.get('Value', DataTree.from_scalar(0))
    
    result = DataTree()
    for path in value_tree.get_paths():
        items = value_tree.get_branch(path)
        result_items = [-item for item in items]
        result.set_branch(path, result_items)
    
    return {'Result': result}
```

### Pattern 3: Geometry Creation (Multiple Inputs)

```python
@COMPONENT_REGISTRY.register("Line")
def evaluate_line(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """GH Line component: create line from start and end points."""
    start_tree = inputs.get('Start Point', DataTree())
    end_tree = inputs.get('End Point', DataTree())
    
    start_matched, end_matched = match_longest(start_tree, end_tree)
    
    result = DataTree()
    for path in start_matched.get_paths():
        start_items = start_matched.get_branch(path)
        end_items = end_matched.get_branch(path)
        
        result_items = []
        for start_pt, end_pt in zip(start_items, end_items):
            # Create line dict
            line = {
                'start': start_pt if isinstance(start_pt, list) else [0, 0, 0],
                'end': end_pt if isinstance(end_pt, list) else [0, 0, 0]
            }
            result_items.append(line)
        
        result.set_branch(path, result_items)
    
    return {'Line': result}
```

### Pattern 4: List Processing

```python
@COMPONENT_REGISTRY.register("List Item")
def evaluate_list_item(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """GH List Item component: extract item at index from list."""
    list_tree = inputs.get('List', DataTree())
    index_tree = inputs.get('Index', DataTree.from_scalar(0))
    
    list_matched, index_matched = match_longest(list_tree, index_tree)
    
    result = DataTree()
    for path in list_matched.get_paths():
        list_items = list_matched.get_branch(path)
        index_items = index_matched.get_branch(path)
        
        result_items = []
        for list_val, index_val in zip(list_items, index_items):
            if isinstance(list_val, list) and len(list_val) > 0:
                idx = int(index_val) % len(list_val)  # Handle wrap
                result_items.append(list_val[idx])
            else:
                result_items.append(None)
        
        result.set_branch(path, result_items)
    
    return {'Item': result}
```

### Pattern 5: Geometry with Optional Inputs

```python
@COMPONENT_REGISTRY.register("Construct Plane")
def evaluate_construct_plane(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """GH Construct Plane: create plane from origin, X-axis, Y-axis."""
    origin_tree = inputs.get('Origin', DataTree.from_scalar([0, 0, 0]))
    x_axis_tree = inputs.get('X-Axis', DataTree.from_scalar([1, 0, 0]))
    y_axis_tree = inputs.get('Y-Axis', DataTree.from_scalar([0, 1, 0]))
    
    origin_matched, x_matched, y_matched = match_longest(
        origin_tree, x_axis_tree, y_axis_tree
    )
    
    result = DataTree()
    for path in origin_matched.get_paths():
        origins = origin_matched.get_branch(path)
        x_axes = x_matched.get_branch(path)
        y_axes = y_matched.get_branch(path)
        
        result_items = []
        for origin, x_axis, y_axis in zip(origins, x_axes, y_axes):
            # Extract vectors if needed (handle PolyLine inputs)
            x_vec = extract_vector(x_axis)
            y_vec = extract_vector(y_axis)
            
            # Compute Z-axis: Z = X × Y
            z_vec = cross_product(x_vec, y_vec)
            z_vec = normalize(z_vec)
            
            plane = {
                'origin': origin if isinstance(origin, list) else [0, 0, 0],
                'x_axis': normalize(x_vec),
                'y_axis': normalize(y_vec),
                'z_axis': z_vec
            }
            result_items.append(plane)
        
        result.set_branch(path, result_items)
    
    return {'Plane': result}
```

---

## 9. Troubleshooting

### Issue: Component Not Found

**Error**: `KeyError: Component type 'X' not registered`

**Solution**:
1. Check that you used `@COMPONENT_REGISTRY.register("X")` decorator
2. Ensure the type name matches exactly (case-sensitive)
3. Verify the component file is imported: `from gh_components_rotatingslats import *`

### Issue: Wrong Input Names

**Error**: `KeyError: 'InputName'` or inputs are None

**Solution**:
1. Check parameter names in `ghx_graph.json` - they must match exactly
2. Use `inputs.get('InputName', default)` with appropriate defaults
3. Check if input has `mapping` or `reverse_data` flags

### Issue: Data Tree Mismatch

**Error**: Branches don't match or items are None

**Solution**:
1. Always use `match_longest()` for multiple inputs
2. Check branch paths are consistent
3. Handle None values gracefully:
```python
if item is None:
    # Handle None case
    continue  # or use default value
```

### Issue: Output Values Don't Match Grasshopper

**Solution**:
1. Verify you're using the correct mathematical formula
2. Check data types (int vs float)
3. Verify vector normalization where needed
4. Check if Grasshopper uses degrees vs radians
5. Compare intermediate values with Grasshopper

### Issue: Component Evaluates but Output is Empty

**Solution**:
1. Check that you're setting branches correctly:
```python
result.set_branch(path, result_items)  # Not just result_items
```
2. Verify you're returning the correct output name
3. Check if output has mapping applied (should be automatic)

### Debugging Tips

1. **Add debug prints**:
```python
print(f"DEBUG: Input tree paths: {input_tree.get_paths()}")
print(f"DEBUG: Branch (0,) items: {input_tree.get_branch((0,))}")
print(f"DEBUG: Result items: {result_items}")
```

2. **Check component registration**:
```python
from gh_evaluator_core import COMPONENT_REGISTRY
print("Registered:", COMPONENT_REGISTRY.list_registered())
```

3. **Inspect actual inputs**:
```python
# In your component function
print(f"DEBUG: Received inputs: {list(inputs.keys())}")
for name, tree in inputs.items():
    print(f"  {name}: {tree.branch_count()} branches, {tree.item_count()} items")
```

---

## 10. Quick Reference Checklist

When adding a new component:

- [ ] Identify component type name from `ghx_graph.json`
- [ ] Check if component is already registered
- [ ] Understand component inputs/outputs from GHX
- [ ] Research Grasshopper behavior (documentation or testing)
- [ ] Implement function with `@COMPONENT_REGISTRY.register()` decorator
- [ ] Use `match_longest()` for multiple inputs
- [ ] Handle None values appropriately
- [ ] Return dictionary with output name as key
- [ ] Test with simple inputs
- [ ] Test in full pipeline
- [ ] Verify output matches Grasshopper exactly
- [ ] Document any special behavior in docstring

---

## 11. Example: Complete Implementation

Here's a complete example of adding a new "Distance" component:

```python
@COMPONENT_REGISTRY.register("Distance")
def evaluate_distance(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
    """
    GH Distance component: compute distance between two points.
    
    Inputs:
        Point A: First point [x, y, z]
        Point B: Second point [x, y, z]
    
    Outputs:
        Distance: Euclidean distance between points
    
    Grasshopper Behavior:
        - Computes 3D Euclidean distance: sqrt((Bx-Ax)² + (By-Ay)² + (Bz-Az)²)
        - Returns 0 if either point is None
    """
    point_a_tree = inputs.get('Point A', DataTree())
    point_b_tree = inputs.get('Point B', DataTree())
    
    # Match inputs using longest list strategy
    a_matched, b_matched = match_longest(point_a_tree, point_b_tree)
    
    result = DataTree()
    for path in a_matched.get_paths():
        a_items = a_matched.get_branch(path)
        b_items = b_matched.get_branch(path)
        
        result_items = []
        for a_pt, b_pt in zip(a_items, b_items):
            # Handle None values
            if a_pt is None or b_pt is None:
                result_items.append(0.0)
                continue
            
            # Ensure points are lists
            if not isinstance(a_pt, list) or len(a_pt) < 3:
                a_pt = [0, 0, 0]
            if not isinstance(b_pt, list) or len(b_pt) < 3:
                b_pt = [0, 0, 0]
            
            # GH Distance: Euclidean distance
            dx = b_pt[0] - a_pt[0]
            dy = b_pt[1] - a_pt[1]
            dz = b_pt[2] - a_pt[2]
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            result_items.append(distance)
        
        result.set_branch(path, result_items)
    
    return {'Distance': result}
```

---

## Summary

Adding new components requires:
1. **Understanding** the component's inputs/outputs from GHX
2. **Implementing** the function with proper DataTree handling
3. **Registering** with `@COMPONENT_REGISTRY.register()`
4. **Testing** with the full pipeline
5. **Verifying** output matches Grasshopper exactly

Follow the patterns in `gh_components_rotatingslats.py` for consistency. When in doubt, refer to existing similar components as templates.

