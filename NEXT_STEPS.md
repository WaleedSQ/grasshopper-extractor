# Next Steps for Rotatingslats Evaluation

## Immediate Fixes Needed

### 1. Fix Indentation Error
**File**: `rebuild_complete_graph.py` line 311
**Issue**: Indentation error after `if panel_source_guid in output_params:`
**Fix**: Properly indent the block

### 2. Add Missing Division Component
**Component**: `f9a68fee-bd6c-477a-9d8e-ae9e35697ab1`
**Output Parameter**: `20f5465a-8288-49ad-acd1-2eb24e1f8765`
**Needed by**: Panel `d019d2ee-57d3-4d51-ba22-5ed7ca4fa4f8` ("Distance between slats")

**Action**: Update `rebuild_complete_graph.py` to:
1. Check if `20f5465a...` is in `output_params`
2. Get parent component GUID (`f9a68fee...`)
3. Add it to graph if not present
4. Add its dependencies recursively

### 3. Continue Evaluation Chain
After adding the Division component, the evaluator should progress further.
Handle any new errors as they appear.

## Panel Source Tracing

For each Panel that needs a value:
1. Find Panel's Source GUID from GHX
2. Check if Source is in `output_params`
3. If yes, add parent component to graph
4. If no, trace further (might be external slider or another component)

## Known Panel Sources to Trace

1. **Panel "Distance between slats"** (d019d2ee...)
   - Source: `20f5465a...` = Output param from Division `f9a68fee...`
   - **Status**: Need to add Division to graph

2. **Panel "Distance between targets"** (0e96a9e7...)
   - Source: `bd56a2ba...` (needs tracing)

3. **Panel "Number of slats"** (5c6b726b...)
   - Source: `537142d8...` (already have - Number of slats slider)

## Code Patterns to Use

### Adding Component to Graph
```python
if panel_source_guid in output_params:
    source_info = output_params[panel_source_guid]
    parent_obj_guid = source_info['obj'].get('instance_guid')
    if parent_obj_guid and parent_obj_guid not in graph:
        comp_info = get_component_full_info(parent_obj_guid)
        if comp_info:
            graph[parent_obj_guid] = comp_info
            # Add dependencies recursively...
```

### Checking Input Resolution
- Always check `value is None` explicitly (not `or`)
- Check both `'guid'` and `'source_guid'` in sources
- Prefer `inputs` structure sources over `obj.params` sources

