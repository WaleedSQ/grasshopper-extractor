# Angle Chain Diagnosis - Green Components

## Status Summary

| Component | Status | Items | Values | Issue |
|-----------|--------|-------|--------|-------|
| Plane Normal | ✅ CORRECT | 10 | Varying (Z: 3.1) | Working correctly |
| Line "Between" | ❌ WRONG | 1 | Single line | Should output 10 lines |
| Angle | ❌ WRONG | 10 | All identical (43.47°) | Replicated, not varying |
| Degrees | ❌ WRONG | 10 | All identical (43.47°) | Cascade from Angle |

## Expected vs Current

### Screenshot (Expected)
```
10 varying degree values:
43.707519°
43.033895°
42.213797°
41.218013°
39.968747°
38.335501°
36.180578°
33.323467°
29.029873°
22.969535°

Range: 22.97° to 43.71° (20.74° variation)
```

### Current Output
```
10 identical values:
43.473359° (all 10)

Range: No variation
```

## Root Cause Analysis

### Chain Flow

```
Divide Length (145 pts) ──> List Item [Index=1] ──┐
                                                    ├──> Line "Between" (1 line) ──┐
Divide Length (510 pts) ──> List Item [Index=1] ──┘                                │
                                                                                    ├──> Angle (10 identical)
Area Centroids (10 pts) ──> List Item [x-1] ──> Plane Normal (10 varying) ────────┘
```

### The Problem

**List Items feeding Line "Between"**:
- **Current**: Extract index [1] from their lists
- **Output**: 1 point each → 1 line total
- **Result**: Line produces 1 output, replicated 10 times by match_longest

**What's Needed**:
- List Items should extract 10 items each (indices 0-9)
- Would produce 10 different points → 10 different lines
- Would create 10 different angles

### List Item Configurations

#### LI (Start Point) - GUID: ed4878fc...
- Position: (12348, 2795)
- List: From Divide Length (145 items)
- **Index: [1]** (persistent, no source, no expression)
- Output: 1 item

#### LI (End Point) - GUID: 3f21b46a...
- Position: (12349, 2870)
- List: From Divide Length (510 items)
- **Index: [1]** (persistent, no source, no expression)
- Output: 1 item

#### List Item (Plane Origin) - GUID: 9ff79870... ✅
- Position: (11880, 3147)
- List: From Area Centroid (10 items)
- **Index: [0]** with expression **"x-1"**
- Source: "Number of slats" slider = 10.0
- Calculated index: 10 - 1 = 9
- Output: 1 item (the last centroid at Z=3.1) ✅ CORRECT

## Missing Component

**Hypothesis**: There should be a **Series** or **Range** component generating `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` feeding the Index inputs of the two List Items before the Line.

**Evidence**:
1. The screenshot shows 10 varying angles
2. There are 10 slats (from slider)
3. Plane Normal correctly has 10 varying planes
4. For angles to vary, Vector B must also vary (10 different lines)

## Possible Solutions

### Option A: Add Series Component to Index Inputs
1. Create Series: Start=0, Step=1, Count=10
2. Feed Series output to both List Item Index inputs
3. Each List Item would extract 10 items
4. Line would produce 10 lines
5. Angle would calculate 10 different angles

### Option B: Check if Components Are Outside Group
1. The Series component might exist but be outside "Rotatingslats" group
2. Check if it's treated as external input
3. Verify wire connections in GHX

### Option C: Grafting Behavior (Not Implemented)
1. With proper grafting, a single index could be cross-producted with 10 planes
2. Requires full grafting implementation (Mapping=1)
3. Would create combinatorial expansion

## Current Behavior Explained

With `match_longest(Vector A[1], Vector B[1], Plane[10])`:
1. Vector A replicated 10 times → same vector
2. Vector B replicated 10 times → same line direction
3. Plane provides 10 items → all identical except origin

Result: All 10 angle calculations use:
- Same Vector A
- Same Vector B (line direction)
- Different Plane origins (but this doesn't affect angle between two vectors!)

**This is why all angles are identical!**

## Next Steps

1. ✅ Verify Plane Normal outputs correct Z-axis (-1, 0, 0)
2. ✅ Verify Plane Normal receives varying origins
3. ❌ **Fix**: List Items need to extract multiple items, not single items
4. ❌ **Investigate**: Find if Series component exists and should feed Index inputs

---

*Diagnosis Date: November 22, 2025*  
*Status: Angle calculation chain identified, root cause confirmed*

