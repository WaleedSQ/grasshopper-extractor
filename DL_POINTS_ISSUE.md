# CRITICAL FINDING: Divide Length Points Structure

## The Problem

### Current DL Output Structure:
```
DL (Start Point source): 145 points in 1 branch
  Path {0}: [point0, point1, point2, ..., point144]

DL (End Point source): 510 points in 1 branch  
  Path {0}: [point0, point1, ..., point509]
```

### What's Needed for 10 Varying Angles:
```
DL (Start Point): 10 branches with ~14-15 points each
  Path {0;0}: [points for slat 0]
  Path {0;1}: [points for slat 1]
  ...
  Path {0;9}: [points for slat 9]

DL (End Point): 10 branches with 51 points each
  Path {0;0}: [51 points for slat 0]
  Path {0;1}: [51 points for slat 1]
  ...
  Path {0;9}: [51 points for slat 9]
```

## Current Flow (Broken):

```
DL Points (510 items, 1 branch {0})
    ↓
List Item [Index=1]  →  Extracts item at index 1  →  1 point
    ↓
Line "Between" →  Creates 1 line
    ↓
Angle →  Replicates same angle 10 times = All identical
```

## Expected Flow (Correct):

```
DL Points (510 items in 10 branches)
  {0;0}: [51 points]
  {0;1}: [51 points]
  ...
  {0;9}: [51 points]
    ↓
List Item [Index=1, Access=Item]
    Applied to each branch separately
    ↓
10 different points (one from each branch)
    ↓
Line "Between" →  Creates 10 lines
    ↓
Angle →  Calculates 10 different angles
```

## Why This Matters

For the angle calculation to vary:
1. **Start Point** must provide 10 different points (one per slat)
2. **End Point** must provide 10 different points (one per slat)
3. **Line** creates 10 different lines
4. **Angle** calculates angle between each line's direction and plane normal
5. **Result**: 10 varying angles (43.7° to 23.0°)

## Current Math:

- **510 points ÷ 10 slats = 51 points per slat** ✅
- **145 points ÷ 10 slats = 14.5 points per slat** (doesn't divide evenly!)

This suggests:
- The 510-point DL is divided into 10 groups of 51
- The 145-point DL might not be evenly divided, OR...
- There's another operation (Partition, Split List, or Grafting) that should organize these points

## Missing Operation

**Most Likely**: There should be a **Partition List** or **Split Tree** component after each DL that:
1. Takes the flat list of points
2. Divides them into 10 branches based on "Number of slats" slider
3. Creates the {0;0}, {0;1}, ... {0;9} structure

**OR**: The DL components themselves might need **Graft** applied to their output, combined with the Series component generating [0,1,2,...,9].

## Access Parameter

List Item components have an **Access** parameter:
- **Access = 1 (Item)**: Extract one item from list
- **Access = 2 (List)**: Extract entire list

Current: **Access = 1** → Extracts single item from each branch

If DL outputs were properly branched (10 branches), then:
- List Item with Index=1, Access=Item
- Would extract item[1] from EACH of the 10 branches
- Producing 10 different points!

## Solution Options

### Option 1: Partition DL Outputs (Most Likely Correct)
Add Partition List component after each DL:
- Input: 510 points (or 145 points)
- Size: 51 (or 14-15)
- Output: 10 branches

### Option 2: Grafting + Series Index
Apply Graft to DL output + use Series [0,1,2,...,9] as List Item index
- Creates cross-product matching
- Results in 10 extracted points

### Option 3: Data Tree Restructuring
The DL components themselves might output branched data in Grasshopper,
but our evaluator is flattening them to a single branch.

## Next Step

Check the GHX file to see if:
1. DL components have Graft/Flatten applied to their outputs
2. There's a Partition/Split component between DL and List Item
3. The List Item Access parameter is set differently

---

*Critical Finding Date: November 22, 2025*  
*This explains why all angles are identical!*

