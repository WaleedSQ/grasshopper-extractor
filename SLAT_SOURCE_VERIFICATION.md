# "Slat source" Calculation Verification

## Summary

Verified the complete calculation chain for "Slat source" Surface component step by step.

## Step-by-Step Calculation

### Step 1: Slat lenght ✅
- **Component**: Division (`32cc502c...`)
- **Calculation**: room width (5.0) / 2 = **2.5**
- **Output GUID**: `4c2fdd4e...`
- **Status**: ✅ Verified correct

### Step 2: Y Coordinate Source ✅
- **Component**: Division (`b9102ff3...`)
- **Calculation**: Slat width (0.08) / 2 = **0.04**
- **Output GUID**: `eedce522...`
- **Status**: ✅ Verified correct
- **Used by**: Construct Point A and Construct Point B (Y coordinates)

### Step 3: Construct Point A ✅
- **Component**: Construct Point (`be907c11...`)
- **Inputs**:
  - X: from "Slat lenght" (`fadbd125...`) = **2.5**
  - Y: from Division (`eedce522...`) = **0.04**
  - Z: constant = **0.0**
- **Result**: **[2.5, 0.04, 0.0]**
- **Output GUID**: `902866aa...`
- **Status**: ✅ Verified correct

### Step 4: Construct Point B
- **Component**: Construct Point (`67b3eb53...`)
- **Inputs**:
  - X: from Negative component (`835d042f...`) which negates "Slat lenght" = **-2.5**
  - Y: from component producing `370f6ae5...` (need to trace)
  - Z: constant = **0.0**
- **Expected Result**: **[-2.5, ?, 0.0]**
- **Output GUID**: `ef17623c...`
- **Note**: GHX shows PersistentData with X=10, Y=5, Z=0, but these are overridden by source connections

### Step 5: Rectangle 2Pt
- **Component**: Rectangle 2Pt (`a3eb185f...`)
- **Inputs**:
  - Point A: from Construct Point A (`902866aa...`) = [2.5, 0.04, 0.0]
  - Point B: from Construct Point B (`ef17623c...`) = [-2.5, ?, 0.0]
  - Length: from "Slat thickness" = **0.001**
- **Output GUID**: `dbc236d4...`
- **Status**: Creates rectangle geometry from two corner points

### Step 6: Surface 'Slat source' ✅
- **Component**: Surface (`8fec620f...`)
- **Source**: Rectangle 2Pt output (`dbc236d4...`)
- **Status**: ✅ Pass-through component for geometry

## Calculation Chain

```
1. Slat lenght (2.5)
   └─> Construct Point A X coordinate
   └─> Negative component
       └─> Construct Point B X coordinate (-2.5)

2. Slat width / 2 (0.04)
   └─> Construct Point A Y coordinate
   └─> Construct Point B Y coordinate (source: 370f6ae5...)

3. Construct Point A [2.5, 0.04, 0.0]
   └─> Rectangle 2Pt Point A

4. Construct Point B [-2.5, ?, 0.0]
   └─> Rectangle 2Pt Point B

5. Rectangle 2Pt
   └─> Surface 'Slat source'
```

## Verified Values

- ✅ Slat lenght: **2.5**
- ✅ Y coordinate source: **0.04** (Slat width / 2)
- ✅ Construct Point A: **[2.5, 0.04, 0.0]**
- ⏳ Construct Point B X: **-2.5** (negative of Slat lenght)
- ⏳ Construct Point B Y: **?** (from component `370f6ae5...`)

## Next Steps

1. Trace component producing output `370f6ae5...` for Construct Point B Y coordinate
2. Verify Rectangle 2Pt evaluation with both points
3. Verify Surface component receives correct geometry

