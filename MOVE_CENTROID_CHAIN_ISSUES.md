# Move → Centroid Chain Issues and Fixes

## Exact GHX Chain (from trace_exact_ghx_chain.py)

1. **First Move "Slats original" (ddb9e6ae-7d3e-41ae-8c75-fc726c984724)**
   - Motion input source: `07dcee6c-9ef1-4893-a77f-18130fa2c9ea` (Vector 2Pt output)
   - Geometry output: `47af807c-369d-4bd2-bbbb-d53a4605f8e6`

2. **Polar Array (7ad636cc-e506-4f77-bb82-4a86ba2a3fea)**
   - Geometry input source: `47af807c-369d-4bd2-bbbb-d53a4605f8e6` (from first Move)
   - Count: 10
   - Angle: 2π radians
   - Geometry output: `1a00d7ad-1003-4dfa-a933-6a7a60dfb0b1`

3. **List Item (27933633-dbab-4dc0-a4a2-cfa309c03c45)**
   - List input source: `1a00d7ad-1003-4dfa-a933-6a7a60dfb0b1` (Polar Array output)
   - Index: 0, Wrap: true
   - Item output: `a72418c4-eb29-4226-9dea-f076720da34f`

4. **Second Move "Slats original" (0532cbdf-875b-4db9-8c88-352e21051436)**
   - Geometry input source: `a72418c4-eb29-4226-9dea-f076720da34f` (List Item output)
   - Motion input source: `d0668a07-838c-481c-88eb-191574362cc2` (Amplitude output)
   - Motion PersistentData: `[0, 0, 10]` (should be overridden by source)
   - Geometry output: `4218a4e5-b5a7-477b-b7e2-dfc59ff7b896`

5. **Area (3bd2c1d3-149d-49fb-952c-8db272035f9e)**
   - Geometry input source: `4218a4e5-b5a7-477b-b7e2-dfc59ff7b896` (Second Move output)
   - Centroid output: `01fd4f89-2b73-4e61-a51f-9c3df0c876fa`

## Current Issues

### Issue 1: Motion Vector Y Coordinate
- **Expected**: Y = -27.416834
- **Actual**: Y = -27.346834
- **Difference**: 0.07 (Vector 2Pt Y component)
- **Root Cause**: Motion vector combination is correct (`[11.32743, -27.416834, 3.8]`), but centroid calculation is using wrong Y value
- **Fix**: Ensure combined motion vector is actually used in Move component

### Issue 2: Motion Vector Z Coordinate
- **Expected**: Z = 3.8, 3.722222, 3.644444, etc. (varying per slat)
- **Actual**: Z = 7.6 (constant for all slats)
- **Difference**: 3.8 (geometry already has Z=3.8, motion Z=3.8 is added, giving 7.6)
- **Root Cause**: Geometry input to Move already has Z=3.8 (from first Move), and motion vector Z=3.8 is being added to it
- **Fix**: Motion vector Z should be relative to geometry's current Z position, OR geometry input Z should be 0.0 (not 3.8)

## Expected Centroids (from user)

All 10 centroids should have:
- X = 11.32743
- Y = -27.416834
- Z = 3.8, 3.722222, 3.644444, 3.566667, 3.488889, 3.411111, 3.333333, 3.255556, 3.177778, 3.1

## Current Implementation Status

1. ✅ Motion vector combination: Correctly combines Amplitude with Vector 2Pt
2. ✅ Motion vector X: Correct (11.32743)
3. ❌ Motion vector Y: Correct in combination (-27.416834), but not used in centroid
4. ❌ Motion vector Z: Wrong (3.8 absolute, should be relative or geometry Z should be 0.0)
5. ✅ Move component: Correctly handles list of geometries with list of motion vectors
6. ✅ Area component: Correctly handles list of geometries and returns list of centroids

## Next Steps

1. Verify that combined motion vector is actually passed to Move component
2. Check if geometry input to Move has Z=3.8 already, and if so, make motion Z relative
3. Verify List Item output: should it return a single geometry or list of geometries?
4. Check Polar Array output structure: is it a nested list `[[{rectangles}]]` or flat list `[{rectangles}]`?

