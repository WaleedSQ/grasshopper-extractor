# Grasshopper (GHX) Evaluator

A Python-based evaluation engine that replicates Grasshopper component behavior by parsing `.ghx` files and evaluating component graphs with proper data tree handling, wire resolution, and topological sorting.

## Project Overview

This project evaluates Grasshopper definition files (currently `refactored-sun-simple.ghx`), accurately replicating the behavior of individual components including data tree matching, grafting/flattening, and geometric calculations.

## Project Structure

### Core Files (Active)

#### Parsing & Graph Extraction
- **`parse_refactored_ghx.py`** - Phase 1: Parses GHX XML files (e.g., `refactored-sun-simple.ghx`)
  - Extracts components, parameters, wires, persistent data
  - Filters out non-functional components (Scribble, Sketch, Group)
  - Outputs: `ghx_graph.json`, `component_index.json`, `wire_index.json`
  
- **`isolate_rotatingslats.py`** - Phase 2: Extracts Rotatingslats group subgraph
  - Reads: `ghx_graph.json`
  - Outputs: `rotatingslats_graph.json`, `rotatingslats_inputs.json`

#### Evaluation Engine
- **`gh_evaluator_core.py`** - Core data structures and matching logic
  - `DataTree`: Hierarchical data structure (branches and items)
  - `match_longest`: Longest List data matching with replication
  - `COMPONENT_REGISTRY`: Component function registry
  - `EvaluationContext`: Evaluation state management

- **`gh_evaluator_wired.py`** - Phase 5: Main evaluation engine
  - Topological sort of component graph
  - Wire resolution (internal and external)
  - Input mapping (Graft/Flatten)
  - Component evaluation orchestration
  - Reads: `rotatingslats_graph.json`, `rotatingslats_inputs.json`
  - Outputs: `rotatingslats_evaluation_results.json`

- **`gh_components_rotatingslats.py`** - Component implementations
  - All component evaluation functions (Angle, Rotate, Plane Normal, etc.)
  - Geometric calculations (vectors, planes, rotations)
  - Data tree handling per component

### Input/Output Files

#### Input Files
- **`refactored-sun-simple.ghx`** - Source Grasshopper definition file

#### Intermediate Files (Generated)
- **`ghx_graph.json`** - Full component graph from GHX parsing (used by Phase 2)
  - Contains all components, parameters, wires, and persistent data
- **`component_index.json`** - Component lookup index (reference/debugging)
  - **Purpose**: Quick lookup table mapping component GUIDs to their metadata
  - **Structure**: Dictionary with component GUID as key, containing:
    - `guid`: Component GUID
    - `type_name`: Component type (e.g., "Angle", "Rotate", "List Item")
    - `nickname`: Component nickname/label
    - `container`: Group container (if any)
    - `position`: X/Y position in canvas
    - `params`: Parameter names mapped to their GUIDs
  - **Use Cases**: 
    - Quick component lookup by GUID
    - Understanding graph structure without parsing full graph
    - Debugging component relationships
  - **Note**: Not used in pipeline execution, but valuable for reference and debugging

- **`wire_index.json`** - Wire connection index (reference/debugging)
  - **Purpose**: Flat list of all wire connections in the graph
  - **Structure**: Array of wire objects, each containing:
    - `from`: Source component GUID
    - `to`: Target component GUID
    - `to_param`: Target parameter name
  - **Use Cases**:
    - Tracing data flow between components
    - Understanding connection topology
    - Debugging wire resolution issues
    - Visualizing component dependencies
  - **Note**: Not used in pipeline execution, but valuable for reference and debugging
- **`rotatingslats_graph.json`** - Isolated Rotatingslats group graph (used by Phase 5)
- **`rotatingslats_inputs.json`** - External inputs (sliders, panels, etc.) (used by Phase 5)

#### Output Files (Generated)
- **`rotatingslats_evaluation_results.json`** - Final evaluation results with component outputs

### Utility Scripts (Optional)

- **`show_sample_results.py`** - Displays sample evaluation results
- **`validate_all_components.py`** - Validates component outputs

### Project Organization

- **`obsolete/`** - Folder containing 57 obsolete files from earlier development phases
  - Old parsers, evaluators, and extraction scripts
  - Historical documentation
  - Reference files no longer used in the pipeline

## Workflow

### Step 1: Parse GHX File
```bash
python parse_refactored_ghx.py
```
Parses `refactored-sun-simple.ghx` and extracts:
- All functional components with their parameters, wires, and persistent data
- Filters out non-functional components (Scribble, Sketch, Group)
- Component index for quick lookup
- Wire index for connection resolution

**Outputs:**
- `ghx_graph.json` - Complete graph structure (used by Phase 2)
- `component_index.json` - Component lookup index (reference only)
- `wire_index.json` - Wire connection index (reference only)

### Step 2: Isolate Rotatingslats Group
```bash
python isolate_simple.py
```
Extracts the Rotatingslats group subgraph:
- Finds all components within the group
- Identifies external wires (connections to components outside the group)
- Extracts external inputs (sliders, panels, etc.)

**Outputs:**
- `ghx_graph.json` - Group subgraph
- `inputs.json` - External inputs

### Step 3: Evaluate Graph
```bash
python gh_evaluator_wired.py
```
Evaluates the component graph:
- Performs topological sort
- Resolves all input wires
- Applies input mapping (Graft/Flatten)
- Evaluates components in dependency order
- Handles data tree matching (Longest List strategy)

**Outputs:**
- `evaluation_results.json` - Complete evaluation results

## Key Features

### Data Tree Structure
- **Branches**: Hierarchical paths like `(0,)`, `(0, 0)`, `(0, 1)`, etc.
- **Items**: Data items within each branch
- **Matching**: Longest List strategy with replication for mismatched structures

### Input Mapping
- **Graft (Mapping=1)**: Each item gets its own branch
- **Flatten (Mapping=2)**: All items merged into single branch
- **None (Mapping=0)**: No transformation

### Component Evaluation
- **Wire Resolution**: Wired inputs take precedence over persistent data
- **External Inputs**: Sliders, panels, and constants from outside the group
- **Topological Sort**: Components evaluated in dependency order
- **Error Handling**: Graceful handling of missing inputs

## Component Implementations

All components are implemented in `gh_components_rotatingslats.py`:

- **Angle**: Computes angle between two vectors with optional plane normal
- **Rotate**: Rotates geometry around a plane's axis
- **Plane Normal**: Extracts plane normal (Z-axis)
- **Construct Plane**: Creates plane from origin, X-axis, and Y-axis
- **List Item**: Extracts item from list by index
- **Divide Length**: Divides curve into segments
- **Project**: Projects geometry onto target
- **Line**: Creates line from two points
- **Vector 2Pt**: Creates vector from two points
- **Area**: Computes area and centroid
- **Move**: Moves geometry by motion vector
- **Polar Array**: Creates polar array of geometry
- And many more...

## Recent Fixes

### Angle Component Variation Fix
- **Issue**: Angle values were identical within each branch instead of varying
- **Root Cause**: 
  1. `List Item` component wasn't applying scalar index to all branches
  2. `match_longest` was replicating entire parent branches instead of specific items
  3. Input mapping (Graft) wasn't being applied before component evaluation
- **Fix**: 
  - Fixed `List Item` to use scalar index across all branches
  - Fixed `match_longest` to retrieve specific items from parent branches
  - Added input mapping application in `gh_evaluator_wired.py`

### Rotate Component Fix
- **Issue**: Plane rotation not working correctly
- **Fix**: Implemented Rodrigues' rotation formula for rotating plane axes

### Plane Normal & Construct Plane Fix
- **Issue**: Incorrect axis extraction and plane construction
- **Fix**: Corrected to use proper axes (Z-axis for Plane Normal, X/Y for Construct Plane)

## Verification

The evaluator has been verified against Grasshopper screenshots:
- ✅ Angle values match (10 unique values per branch)
- ✅ Plane normals match
- ✅ Construct Plane outputs match
- ✅ Rotate component outputs match
- ✅ Centroid values match

## Dependencies

- Python 3.x
- Standard library only (no external packages required)
  - `xml.etree.ElementTree` - XML parsing
  - `json` - JSON handling
  - `math` - Mathematical functions
  - `collections` - Data structures

## Recent Improvements

### Parser Simplification
- **Simplified code structure**: Reduced from 532 to 401 lines (~25% reduction)
- **Helper functions**: Added reusable utilities (`extract_items`, `find_chunk`, `safe_float`)
- **Non-functional component filtering**: Automatically skips Scribble, Sketch, and Group components
- **Cleaner logic**: Removed redundant code and simplified conditionals

### New Components
- **Circle**: Creates circle from plane and radius
- **Curve | Curve**: Finds intersection points between two curves

## Notes

- The evaluator replicates Grasshopper's "Longest List" data matching strategy
- Grafting creates new branch levels by appending indices
- Flattening merges all branches into a single branch
- External inputs (sliders, panels) are resolved before component evaluation
- Wired connections take precedence over persistent data

## Documentation

- `README.md` - This file (main documentation)
- `PROJECT_STATUS.md` - Current project status and recent fixes
- `FILE_INVENTORY.md` - Complete file inventory and structure
- `ADDING_NEW_COMPONENTS.md` - Comprehensive guide for adding new components

