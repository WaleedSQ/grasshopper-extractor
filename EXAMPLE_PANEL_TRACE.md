# Example: How to Trace Panel Sources

## Problem
Panel "Distance between slats" (d019d2ee...) has Source connection to `20f5465a-8288-49ad-acd1-2eb24e1f8765`, but we need to find what value this source provides.

## Step-by-Step Trace Process

### Step 1: Find the Panel in GHX
```xml
<chunk name="Object">
  <item name="InstanceGuid">d019d2ee-57d3-4d51-ba22-5ed7ca4fa4f8</item>
  <item name="NickName">Distance between slats</item>
  <item name="Source">20f5465a-8288-49ad-acd1-2eb24e1f8765</item>  <!-- This is what we need to trace -->
</chunk>
```

### Step 2: Check what `20f5465a...` is

**Option A: Check if it's an output parameter**
- Search in `rotatingslats_data.json` for any parameter with `InstanceGuid == 20f5465a...`
- If found, note the parent component and parameter name
- Example format:
```json
{
  "some_component_guid": {
    "params": {
      "param_output_0": {
        "data": {
          "InstanceGuid": "20f5465a-8288-49ad-acd1-2eb24e1f8765",
          "NickName": "Result"
        }
      }
    }
  }
}
```

**Option B: Check if it's a component**
- Search in `rotatingslats_data.json` for component with `instance_guid == 20f5465a...`
- Check its type (Number Slider, Number, Panel, etc.)
- If it's a Number Slider, check `external_inputs.json` for its value

**Option C: Check GHX file directly**
- Search for `<item name="InstanceGuid">20f5465a-8288-49ad-acd1-2eb24e1f8765</item>`
- Check the component type and extract its value

### Step 3: Extract the Value

**If source is a Number Slider:**
- Value is in `external_inputs.json` under key `20f5465a...`
- Format: `{"value": 0.5, "object_type": "GH_NumberSlider", ...}`

**If source is an output parameter:**
- Need to evaluate the parent component first
- Then get the output parameter value from the component's result
- Example: If parent is "Division" component, evaluate it, then get its "Result" output

**If source is a Number component:**
- Check `external_inputs.json` or `number_component_sources.json`
- Or check if it has a Source connection itself (recursive trace)

### Step 4: Add to external_inputs.json

Once you find the value, add it like this:

```json
{
  "d019d2ee-57d3-4d51-ba22-5ed7ca4fa4f8": {
    "value": 0.5,
    "object_type": "Panel",
    "object_nickname": "Distance between slats",
    "source_guid": "20f5465a-8288-49ad-acd1-2eb24e1f8765",
    "source_type": "Number Slider",
    "object_guid": "d019d2ee-57d3-4d51-ba22-5ed7ca4fa4f8"
  }
}
```

## Example Output Format

For Panel "Distance between slats" (d019d2ee...):
1. Panel has Source: `20f5465a...`
2. `20f5465a...` is a Number Slider "Some slider name"
3. Value from external_inputs: `0.5`
4. Add to external_inputs.json:
   ```json
   "d019d2ee-57d3-4d51-ba22-5ed7ca4fa4f8": {
     "value": 0.5,
     "object_type": "Panel",
     "object_nickname": "Distance between slats",
     "source_guid": "20f5465a-8288-49ad-acd1-2eb24e1f8765",
     "source_type": "Number Slider",
     "object_guid": "d019d2ee-57d3-4d51-ba22-5ed7ca4fa4f8"
   }
   ```

## Tools to Help

1. **Search in rotatingslats_data.json:**
   ```bash
   grep -A 20 "20f5465a" rotatingslats_data.json
   ```

2. **Search in external_inputs.json:**
   ```bash
   grep -A 5 "20f5465a" external_inputs.json
   ```

3. **Search in GHX file:**
   ```bash
   grep -A 30 "20f5465a" core-only_fixed.ghx
   ```

## Current Panels That Need Tracing

1. **Panel "Distance between slats"** (d019d2ee...)
   - Source: `20f5465a-8288-49ad-acd1-2eb24e1f8765`
   - Status: Source type unknown, needs manual trace

2. **Panel "Distance between targets"** (0e96a9e7...)
   - Source: `bd56a2ba...`
   - Status: Source type unknown, needs manual trace

3. **Panel "Number of slats"** (5c6b726b...)
   - Source: `537142d8...`
   - Status: Source type unknown, needs manual trace

