# Angle/Degrees Output Mismatch Analysis

## Current Status

**Problem**: Angle component outputs 10 IDENTICAL values instead of 10 DIFFERENT values

### Current Output
```
All 10 items: 43.473359 degrees
```

### Expected Output (from screenshot)
```
[0]: 43.701519 degrees
[1]: 43.033895 degrees  
[2]: 42.213797 degrees
[3]: 41.218013 degrees
[4]: 39.968747 degrees
[5]: 38.335501 degrees
[6]: 36.180578 degrees
[7]: 33.323467 degrees
[8]: 29.029873 degrees
[9]: 22.969535 degrees
```

**Range**: 43.7° → 23.0° (20.7° variation)

---

## Root Cause Analysis

### Data Flow Traced

```
Vector A: List Item[index=0] → 1 plane → extract z-axis → 1 vector
           (Single item)

Vector B: DL → List Item[index=1] → 1 point (Start)
          DL → List Item[index=1] → 1 point (End)
          → Line → 1 line → extract direction → 1 vector
           (Single item)

Plane:    Plane Normal → 10 identical planes  
          All have origin=[0, 0.07, 3.8], z_axis=[0, 0, 1]
           (10 items, all identical)
```

### Current Behavior

With `match_longest(Vector A[1], Vector B[1], Plane[10])`:
- Vector A replicated 10 times → same vector
- Vector B replicated 10 times → same vector  
- Plane provides 10 items → all identical

**Result**: 10 identical angle calculations = 43.47°

---

## Hypothesis: Grafting / Cross-Product Matching

### GHX Parameter Mapping Settings

From `refactored-no-sun.ghx`:
- **Vector A input**: `Mapping = 1` (Graft)
- **Vector B input**: `Mapping = 1` (Graft)
- **Plane input**: No mapping specified (default = 0, no graft)

### Grafting Behavior in Grasshopper

**Without Graft**:
- Data structure: `{0}` with items `[item0, item1, ...]`

**With Graft** (Mapping = 1):
- Data structure: `{0;0}[item0]`, `{0;1}[item1]`, ...
- Each item gets its own sub-branch

### Cross-Product Matching

When **grafted** inputs meet **non-grafted** inputs in Grasshopper:
- Grafted `{0;0}[1 item]` 
- Non-grafted `{0}[10 items]`
- → Cross-product creates `10 × 1 = 10` combinations

**However**, this still doesn't explain how 10 DIFFERENT angles are produced if:
1. Vector A is always the same vector
2. Vector B is always the same vector
3. Plane items are all identical

---

## Alternative Hypotheses

### 1. Different GHX File or Slider Values

The screenshot might be from:
- A different version of the GHX file
- Different slider values (especially "Divide Length" counts)
- Different List Item indices

**Evidence**: First value `43.70°` vs our `43.47°` (0.23° difference)

### 2. Missing Data Variation Upstream

One of the upstream components might actually be producing 10 different values:
- The List Item feeding Vector A might extract 10 items (not 1)
- The Line feeding Vector B might produce 10 lines (not 1)
- The Plane Normal might have different z-axes (currently all `[0,0,1]`)

### 3. Grafting Implementation Needed

The evaluator doesn't currently implement Grasshopper's grafting behavior, which:
- Restructures data trees
- Enables cross-product matching
- Creates combinatorial expansions

---

## Questions to Resolve

1. **Is the screenshot from `refactored-no-sun.ghx` with current slider values?**
   - If not, which GHX file / what slider settings?

2. **Are the List Item indices correct?**
   - Current: Vector A source uses index `[0]`
   - Current: Vector B sources use index `[1]`
   - Should these be ranges like `[0..9]`?

3. **Should grafting be implemented?**
   - This is a significant feature addition
   - Required for cross-product data matching
   - Affects ALL components with grafted inputs

---

## Recommended Next Steps

### Option A: Verify Screenshot Source
1. Confirm screenshot is from `refactored-no-sun.ghx`
2. Check all slider values match current settings
3. Verify List Item index values

### Option B: Implement Grafting
1. Add grafting support to DataTree class
2. Apply grafting based on Mapping parameter values
3. Implement cross-product matching logic
4. Test with Angle component

### Option C: Trace Actual GH Evaluation
1. Open `refactored-no-sun.ghx` in Grasshopper
2. Inspect actual data at each step
3. Use "Data Viewer" to see tree structures
4. Compare with evaluator outputs

---

## Current Evaluator Limitations

✅ **Implemented**:
- Component-level evaluation
- DataTree basic operations
- match_longest replication
- Geometry type handling

❌ **Not Implemented**:
- **Grafting** (Mapping = 1)
- **Flattening** (Mapping = 0)
- **Reverse** (Mapping = 2)
- Cross-product matching
- Complex data tree restructuring

---

*Analysis Date: November 22, 2025*  
*Status: Awaiting clarification on screenshot source and grafting requirements*

