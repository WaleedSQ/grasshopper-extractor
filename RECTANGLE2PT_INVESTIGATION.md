# Rectangle 2Pt Investigation

## Problem
Rectangle 2Pt component (a3eb185f-a7cb-4727-aeaf-d5899f934b99) is NOT being evaluated, causing the first Move component to receive None for Geometry input.

## Findings

### 1. Rectangle 2Pt is in the graph
- **Location**: `complete_component_graph.json` under `components` key
- **Component GUID**: `a3eb185f-a7cb-4727-aeaf-d5899f934b99`
- **Type**: Rectangle 2Pt
- **Status**: ✅ Found in graph

### 2. Graph Structure Issue
The graph has this structure:
```json
{
  "components": {
    "a3eb185f-a7cb-4727-aeaf-d5899f934b99": {
      "type": "component",
      "obj": { ... }
    },
    ...
  }
}
```

### 3. Topological Sort Issue
The `topological_sort` function was iterating over `graph.items()` directly, which would only see the top-level `"components"` key, not the actual component entries.

**Fix Applied**: Modified `topological_sort` to handle graph structure:
```python
components_dict = graph.get('components', graph) if isinstance(graph, dict) and 'components' in graph else graph
```

### 4. Rectangle 2Pt Dependencies
Rectangle 2Pt has these inputs:
- **Plane**: Has persistent_values (default plane)
- **Point A**: Has source (Construct Point A output)
- **Point B**: Has source (Construct Point B output)  
- **Length**: Has source (from "Slat thickness")

### 5. Why It's Not Being Evaluated
Possible reasons:
1. **Dependencies not evaluated**: If Construct Point A/B or "Slat thickness" aren't evaluated, Rectangle 2Pt won't be in the sort
2. **Topological sort bug**: The sort might not be including all components
3. **Component type check**: The `type == 'component'` check might be failing

## Next Steps

1. Verify topological_sort is now correctly accessing components
2. Check if Rectangle 2Pt's dependencies (Construct Point A/B) are being evaluated
3. Add debug output to see which components are in the sort
4. Verify Rectangle 2Pt appears in evaluation results after fix

