# Series Component Step Input Issue

## Problem
Series component (680b290d) should output: `[-0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07, -0.07]`

Currently outputs: `[-0.07, 0.9299999999999999, 1.93, 2.93, 3.93, 4.93, 5.93, 6.93, 7.93, 8.93]`

## Root Cause
The Series component's **Step** input should come from:
- **Negative component** (a69d2e4a...) output (bdac63ee...)
- Expected value: **0.0** (negating "Horizontal shift between slats" = 0.0)

But it's currently resolving to:
- **Division component** (524ba570...) output (133aa1b3...)
- Current value: **0.3888888888888889** (3.5 / 9.0)

## Component Chain

1. **Series Component** (680b290d-e662-4a76-9b3c-e5e921230589)
   - Start: -0.07 (from "Distance from window" slider) ✅
   - Step: Should be 0.0 (from Negative component) ❌ Currently 0.3888888888888889
   - Count: 10 (from "Number of slats" slider) ✅

2. **Negative Component** (a69d2e4a-b63b-40d0-838f-dff4d90a83ce)
   - Value input: Should be 0.0 (from "Horizontal shift between slats" slider) ❌ Currently None
   - Output: Should be 0.0 ❌ Currently None
   - Output GUID: bdac63ee-60a4-4873-8860-06e887053c0e

3. **External Input**: "Horizontal shift between slats" (08edbcda-c850-40fd-9900-c6ab83acca1b)
   - Value: 0.0 ✅ (in external_inputs.json)

## Issue Analysis

The Negative component is outputting **None** because its Value input is not being resolved from the external input. The resolver should find the external input at:
- Source GUID: `08edbcda-c850-40fd-9900-c6ab83acca1b`
- External inputs key: `08edbcda-c850-40fd-9900-c6ab83acca1b` ✅ (matches)

But the resolver is not finding it, causing:
1. Negative component gets None for Value input
2. Negative component outputs None
3. Series component can't resolve Step from Negative output (None)
4. Series component falls back to Division output or persistent_values

## Expected Behavior

In Grasshopper:
- "Horizontal shift between slats" = 0.0
- Negative component negates it → 0.0
- Series Step = 0.0
- Series with Start=-0.07, Step=0.0, Count=10 → `[-0.07, -0.07, -0.07, ...]`

## Fix Required

1. Fix `resolve_input_value` to correctly resolve external inputs for Negative component
2. Ensure Negative component correctly handles 0.0 input (not None)
3. Ensure Series component correctly resolves Step from Negative output (not Division output)

