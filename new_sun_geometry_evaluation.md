# New Sun Component - Geometry Input Evaluation

## Summary

The **New Sun** component (Move component, GUID: `0f529988-b68b-4d48-9a48-cf099af69050`) receives its **Geometry** input from an **Area** component's **Centroid** output.

## Evaluation Chain

### 1. New Sun Component (Move)
- **Component Type**: Move
- **Component GUID**: `0f529988-b68b-4d48-9a48-cf099af69050`
- **NickName**: "New Sun"
- **Geometry Input Source**: `01fd4f89-2b73-4e61-a51f-9c3df0c876fa` (Area Centroid output)

### 2. Area Component (Centroid Output)
- **Component Type**: Area
- **Component GUID**: `3bd2c1d3-149d-49fb-952c-8db272035f9e`
- **NickName**: "Area"
- **Output Parameter**: Centroid (GUID: `01fd4f89-2b73-4e61-a51f-9c3df0c876fa`)
- **Geometry Input Source**: `4218a4e5-b5a7-477b-b7e2-dfc59ff7b896` (Move "Slats original" Geometry output)

### 3. Move Component "Slats original"
- **Component Type**: Move
- **Component GUID**: `0532cbdf-875b-4db9-8c88-352e21051436`
- **NickName**: "Slats original"
- **Output Parameter**: Geometry (GUID: `4218a4e5-b5a7-477b-b7e2-dfc59ff7b896`)

## Evaluated Values

### Final Geometry Input Value
```
[0.0, 0.0, 0.0]
```

This is the **Centroid** output from the Area component, which computes the centroid of the geometry from "Slats original" Move component.

### Area Component Output
```python
{
    'Area': 0.0,
    'Centroid': [0.0, 0.0, 0.0]
}
```

**Note**: The Area component currently returns placeholder values because:
1. The "Slats original" Move component receives geometry from a Surface component (`8fec620f-ff7f-4b94-bb64-4c7fce2fcb34`) which is treated as external
2. The Surface component has no inputs defined in the GHX and is treated as an external placeholder
3. The Area component's simplified implementation returns `0.0` for area and `[0.0, 0.0, 0.0]` for centroid when geometry is not properly defined

## Motion Input

The **Motion** input to New Sun is:
- **GHX PersistentData**: `[0.0, 0.0, 10.0]`
- **Override**: `SUN_VECTOR = [33219.837229, -61164.521016, 71800.722722]`
- **Final Value Used**: `[33219.837229, -61164.521016, 71800.722722]`

## New Sun Component Output

```python
{
    'Geometry': [0.0, 0.0, 0.0]
}
```

This is the result of moving the input geometry `[0.0, 0.0, 0.0]` by the motion vector `[33219.837229, -61164.521016, 71800.722722]`.

**Note**: The current `move_component` implementation is simplified and returns the input geometry unchanged. A full implementation would translate the point by the motion vector, resulting in:
```python
[0.0 + 33219.837229, 0.0 + (-61164.521016), 0.0 + 71800.722722]
= [33219.837229, -61164.521016, 71800.722722]
```

