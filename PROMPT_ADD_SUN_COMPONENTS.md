# Prompt: Add Sun Path Analysis Components to Grasshopper Evaluator

## Context

You are working on a Grasshopper (GHX) evaluator project that currently evaluates the "Rotatingslats" group from a GHX file. The project uses a generic parser (`parse_refactored_ghx.py`) and a generic evaluator (`gh_evaluator_wired.py`) that can handle any registered components through a component registry system.

**Current Project Structure:**
- `parse_refactored_ghx.py` - Generic GHX parser (works for any GHX file)
- `isolate_rotatingslats.py` - Extracts Rotatingslats group (currently hardcoded to one group)
- `gh_evaluator_core.py` - Core evaluation engine with COMPONENT_REGISTRY (generic)
- `gh_evaluator_wired.py` - Main evaluator (generic, works with any component graph)
- `gh_components_rotatingslats.py` - Component implementations (can be extended)

**Current Status:**
- All existing components work correctly
- 56 components in Rotatingslats group evaluate successfully
- Angle values, rotations, and all geometric operations verified

## Task: Add Sun Path Analysis Components

### Overview

A new GHX file will be provided that includes a "Sun" group (purple group labeled "sunGroup" in the screenshot) containing components for sun path analysis. You need to:

1. **Parse the new GHX file** using the existing parser
2. **Extract the Sun group** (similar to how Rotatingslats group is extracted)
3. **Implement new components** needed for sun path analysis
4. **Connect the Sun group output** to the existing "New Sun" component in Rotatingslats group
5. **Ensure no existing functionality breaks**

### Components to Implement

From the screenshot analysis, the Sun group contains:

1. **DownloadEPW** (Stub Implementation)
   - **Purpose**: Download EPW weather file from URL
   - **Action**: **STUB THIS** - Don't implement actual download
   - **Behavior**: Should output the local EPW file path `GBR_SCT_Salsburgh.031520_TMYx.epw` that exists in the project root
   - **Inputs**: 
     - `_weather_URL`: URL string (can be ignored for stub)
     - `_folder_`: Optional folder path
   - **Outputs**:
     - `epw_file`: Path to local EPW file (hardcode to `GBR_SCT_Salsburgh.031520_TMYx.epw`)
     - `stat_file`: Can return empty/None
     - `ddy_file`: Can return empty/None

2. **ImportEPW** (Full Implementation)
   - **Purpose**: Import and parse EPW weather file
   - **Inputs**:
     - `_epw_file`: Path to EPW file (from DownloadEPW)
   - **Outputs**:
     - `location`: Location data (dict with lat, lon, elevation, timezone, etc.)
     - Many other outputs (temperature, radiation, etc.) - **Only `location` is needed for now**
   - **Implementation**: Parse EPW file format (see EPW file in project root for structure)
   - **EPW File**: `GBR_SCT_Salsburgh.031520_TMYx.epw` exists in project root

3. **HOY** (Hour of Year - Full Implementation)
   - **Purpose**: Convert month/day/hour to hour of year (0-8759)
   - **Inputs**:
     - `_month_`: Month (1-12) - from slider, value 8 in screenshot
     - `_day_`: Day (1-31) - from slider, value 13 in screenshot
     - `_hour_`: Hour (0-23) - from slider, value 11 in screenshot
     - `_minute_`: Optional minute (default 0)
   - **Outputs**:
     - `hoy`: Hour of year (integer 0-8759)
     - `doy`: Day of year (optional, can implement)
     - `date`: Date object (optional, can implement)
   - **Formula**: Calculate days from Jan 1 to given month/day, multiply by 24, add hours

4. **Sunpath** (Full Implementation)
   - **Purpose**: Calculate sun position vectors for given location and hour of year
   - **Inputs**:
     - `_location`: Location dict from ImportEPW (contains lat, lon, elevation, timezone)
     - `hoys_`: Hour of year from HOY component (single value or list)
     - `north_`: Optional north direction (default 0)
     - Other inputs are optional/unused in this case
   - **Outputs**:
     - `sun_pts`: Sun position points/vectors (this is what we need)
     - `vectors`: Sun direction vectors
     - `altitudes`: Sun altitude angles
     - `azimuths`: Sun azimuth angles
     - Many other outputs (only `sun_pts` is needed)
   - **Implementation**: Use solar position algorithms (solar declination, hour angle, etc.)
   - **Expected Output**: Vector `[33219.837229, -61164.521016, 71800.722722]` for the given inputs

5. **Ex Tree** (Full Implementation)
   - **Purpose**: Extract specific branch from data tree
   - **Inputs**:
     - `Data`: DataTree input (from Sunpath `sun_pts` output)
   - **Outputs**:
     - `{0;0}`: First branch, first item (this is what we need)
     - `{0;1}`, `{0;2}`, etc.: Other branches/items
   - **Behavior**: Extract branch `(0, 0)` from input DataTree
   - **Expected Output**: Single vector `[33219.837229, -61164.521016, 71800.722722]`

### Integration Point

**Critical Connection:**
- The Ex Tree component's `{0;0}` output should connect to the existing "New Sun" component's `Motion` input
- The "New Sun" component is in the Rotatingslats group and currently has an unconnected `Motion` input
- This connection should be treated as an **external wire** from Sun group to Rotatingslats group

### Sample Values (for Verification)

From the screenshot, the Ex Tree output at `{0;0}` shows:
```
{33219.837229, -61164.521016, 71800.722722}
```

This should be the final output when:
- Month = 8 (August)
- Day = 13
- Hour = 11
- Location = Salsburgh, Scotland (from EPW file)

## Implementation Strategy

### Decision: Use Existing Evaluator

**The current evaluator is generic enough** - it uses `COMPONENT_REGISTRY` and can handle any registered components. **No separate evaluator needed.**

**Approach:**
1. Extend `isolate_rotatingslats.py` to also extract the Sun group (or create a combined extraction)
2. Add new component implementations to `gh_components_rotatingslats.py` (or create `gh_components_sun.py` if preferred)
3. Extend `gh_evaluator_wired.py` to evaluate both groups (Sun group first, then Rotatingslats group)
4. Handle the cross-group wire (Ex Tree → New Sun) as an external wire

### Step-by-Step Implementation Plan

#### Phase 1: Parse and Extract

1. **Parse new GHX file**:
   ```bash
   python parse_refactored_ghx.py
   ```
   (Uses existing parser - should work as-is)

2. **Extend isolation script**:
   - Modify `isolate_rotatingslats.py` to extract both groups
   - Or create `isolate_sun_and_rotatingslats.py` that extracts both
   - Find Sun group by nickname "sunGroup" or similar
   - Extract all components in Sun group
   - Identify external wires (including the Ex Tree → New Sun connection)

#### Phase 2: Implement Components

3. **Add component implementations** to `gh_components_rotatingslats.py`:
   - Follow the pattern in `ADDING_NEW_COMPONENTS.md`
   - Use `@COMPONENT_REGISTRY.register()` decorator
   - Implement each component following existing patterns

4. **Component Implementation Details**:

   **DownloadEPW (Stub)**:
   ```python
   @COMPONENT_REGISTRY.register("DownloadEPW")
   def evaluate_download_epw(inputs: Dict[str, DataTree]) -> Dict[str, DataTree]:
       """GH DownloadEPW component (STUB): returns local EPW file path."""
       # Return hardcoded path to local EPW file
       epw_path = "GBR_SCT_Salsburgh.031520_TMYx.epw"
       return {
           'epw_file': DataTree.from_scalar(epw_path),
           'stat_file': DataTree(),
           'ddy_file': DataTree()
       }
   ```

   **ImportEPW**:
   - Parse EPW file format (see EPW specification)
   - Extract location data from header
   - Return location dict with: latitude, longitude, elevation, timezone, etc.

   **HOY**:
   - Calculate hour of year from month/day/hour
   - Formula: `hoy = (days_from_jan1 * 24) + hour`
   - Handle leap years if needed

   **Sunpath**:
   - Implement solar position calculation
   - Use formulas for: solar declination, hour angle, altitude, azimuth
   - Convert to 3D vector (x, y, z coordinates)
   - Return as DataTree with sun_pts output

   **Ex Tree**:
   - Extract specific branch from DataTree
   - For `{0;0}` output, extract branch `(0, 0)` or first item of first branch
   - Return as DataTree

#### Phase 3: Integration

5. **Modify evaluator** to handle multiple groups:
   - Evaluate Sun group first (it has no dependencies on Rotatingslats)
   - Then evaluate Rotatingslats group
   - Pass Sun group outputs as external inputs to Rotatingslats group
   - Specifically, Ex Tree `{0;0}` output → New Sun `Motion` input

6. **Handle cross-group wiring**:
   - The Ex Tree → New Sun wire should be treated as external
   - When evaluating Rotatingslats group, Ex Tree output should be available in `external_inputs`

#### Phase 4: Testing

7. **Verify output**:
   - Run full pipeline with new GHX file
   - Check that Ex Tree output matches: `[33219.837229, -61164.521016, 71800.722722]`
   - Verify New Sun component receives the correct Motion input
   - Ensure all existing Rotatingslats components still work correctly

## Files to Modify/Create

### Modify Existing Files:
1. **`isolate_rotatingslats.py`** - Extend to extract both groups OR create new `isolate_both_groups.py`
2. **`gh_components_rotatingslats.py`** - Add new component implementations
3. **`gh_evaluator_wired.py`** - Extend to evaluate both groups in sequence

### Create New Files (if needed):
1. **`sun_group_graph.json`** - Extracted Sun group (similar to rotatingslats_graph.json)
2. **`sun_group_inputs.json`** - External inputs for Sun group (sliders: Month, Day, Hour)

### Keep Unchanged:
- `parse_refactored_ghx.py` - Works as-is (generic parser)
- `gh_evaluator_core.py` - Works as-is (generic registry)
- All existing component implementations - Don't modify

## Important Constraints

1. **DO NOT BREAK EXISTING FUNCTIONALITY**
   - All existing Rotatingslats components must continue to work
   - All existing tests/verifications must still pass
   - Angle values, rotations, etc. must still match Grasshopper

2. **Use Existing Patterns**
   - Follow component implementation patterns in `gh_components_rotatingslats.py`
   - Use `match_longest()` for multiple inputs
   - Return `Dict[str, DataTree]` for outputs
   - Use `@COMPONENT_REGISTRY.register()` decorator

3. **Handle Data Trees Correctly**
   - All inputs/outputs are DataTrees
   - Use `DataTree.from_scalar()` for single values
   - Use `DataTree.from_list()` for lists
   - Match inputs with `match_longest()` when needed

4. **EPW File Parsing**
   - EPW file `GBR_SCT_Salsburgh.031520_TMYx.epw` exists in project root
   - Parse header section for location data
   - Format: First 8 lines contain metadata, line 1 has location info

## Verification Checklist

After implementation, verify:

- [ ] New GHX file parses successfully
- [ ] Sun group extracts correctly
- [ ] DownloadEPW stub returns correct file path
- [ ] ImportEPW parses location correctly
- [ ] HOY calculates correct hour of year for month=8, day=13, hour=11
- [ ] Sunpath calculates correct sun position vector
- [ ] Ex Tree extracts correct branch `{0;0}`
- [ ] Ex Tree output matches: `[33219.837229, -61164.521016, 71800.722722]`
- [ ] New Sun component receives Motion input correctly
- [ ] All existing Rotatingslats components still work
- [ ] Angle values still match (10 unique values)
- [ ] No regressions in existing functionality

## Reference Files

- **EPW File**: `GBR_SCT_Salsburgh.031520_TMYx.epw` in project root
- **Component Guide**: `ADDING_NEW_COMPONENTS.md` - Comprehensive guide for adding components
- **Existing Components**: `gh_components_rotatingslats.py` - Reference implementations
- **Parser**: `parse_refactored_ghx.py` - Generic GHX parser
- **Evaluator**: `gh_evaluator_wired.py` - Generic evaluator

## Expected Deliverables

1. **Modified/Extended Files**:
   - Extended isolation script (or new combined script)
   - Extended component implementations file
   - Extended evaluator (or new combined evaluator)

2. **New Generated Files**:
   - `sun_group_graph.json` (or combined graph)
   - `sun_group_inputs.json` (or combined inputs)
   - Updated evaluation results

3. **Verification**:
   - Ex Tree output matches screenshot value
   - New Sun component works with Motion input
   - All existing functionality preserved

## Notes

- The Sun group is independent - it can be evaluated first
- The connection Ex Tree → New Sun is the only cross-group dependency
- Sliders (Month, Day, Hour) are external inputs to Sun group
- The EPW file is local, so DownloadEPW can be a simple stub
- Focus on getting the correct sun position vector - other Sunpath outputs can be stubbed if needed

## Start Here

1. First, parse the new GHX file provided by the user
2. Identify the Sun group and its components
3. Check which components are already registered vs need implementation
4. Follow the implementation plan above
5. Test incrementally - verify each component before moving to the next
6. Finally, verify the end-to-end flow matches the screenshot values

Good luck! The existing codebase is well-structured and generic enough to handle this extension cleanly.

