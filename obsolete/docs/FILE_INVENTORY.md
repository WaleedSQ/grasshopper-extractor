# File Inventory - Used vs Obsolete

## Active Files (Required for Evaluation)

### Core Evaluation Files
| File | Purpose | Status |
|------|---------|--------|
| `parse_refactored_ghx.py` | Phase 1: Parse GHX file | ✅ Active |
| `isolate_rotatingslats.py` | Phase 2: Extract Rotatingslats group | ✅ Active |
| `gh_evaluator_core.py` | Core data structures and matching | ✅ Active |
| `gh_evaluator_wired.py` | Phase 5: Main evaluator | ✅ Active |
| `gh_components_rotatingslats.py` | Component implementations | ✅ Active |

### Input Files
| File | Purpose | Status |
|------|---------|--------|
| `refactored-no-sun.ghx` | Source Grasshopper file | ✅ Required |

### Generated Files (Output)
| File | Purpose | Status |
|------|---------|--------|
| `ghx_graph.json` | Full component graph | ✅ Generated |
| `component_index.json` | Component lookup index | ✅ Generated |
| `wire_index.json` | Wire lookup index | ✅ Generated |
| `rotatingslats_graph.json` | Rotatingslats group graph | ✅ Generated |
| `rotatingslats_inputs.json` | External inputs | ✅ Generated |
| `rotatingslats_evaluation_results.json` | Final results | ✅ Generated |

### Documentation Files
| File | Purpose | Status |
|------|---------|--------|
| `README.md` | Main documentation | ✅ Active |
| `PROJECT_STATUS.md` | Current project status | ✅ Active |
| `FILE_INVENTORY.md` | This file | ✅ Active |

---

## Obsolete Files (Not Used in Current Workflow)

### Old Parsers
| File | Purpose | Status |
|------|---------|--------|
| `parse_ghx_v2.py` | Old GHX parser (different file) | ❌ Obsolete |
| `extract_all_external_inputs_from_ghx.py` | Old extraction script | ❌ Obsolete |
| `extract_external_inputs_from_ghx.py` | Old extraction script | ❌ Obsolete |
| `extract_external_inputs.py` | Old extraction script | ❌ Obsolete |

### Old Evaluators
| File | Purpose | Status |
|------|---------|--------|
| `evaluate_rotatingslats.py` | Old evaluator (different architecture) | ❌ Obsolete |
| `evaluate_with_wired.py` | Old wired evaluator | ❌ Obsolete |
| `gh_components.py` | Old component implementations | ❌ Obsolete |
| `gh_data_tree.py` | Old data tree implementation | ❌ Obsolete |

### Old Extraction Scripts
| File | Purpose | Status |
|------|---------|--------|
| `extract_construct_point_values.py` | Extract construct point values | ❌ Obsolete |
| `extract_external_division.py` | Extract division component | ❌ Obsolete |
| `extract_panel_sources_from_trimmed.py` | Extract panel sources | ❌ Obsolete |
| `extract_slider_values.py` | Extract slider values | ❌ Obsolete |
| `extract_vector_components.py` | Extract vector components | ❌ Obsolete |

### Utility Scripts (May be useful for debugging)
| File | Purpose | Status |
|------|---------|--------|
| `add_nicknames_to_results.py` | Add nicknames to results | ⚠️ Optional |
| `show_sample_results.py` | Display sample results | ⚠️ Optional |
| `validate_all_components.py` | Validate components | ⚠️ Optional |
| `rebuild_complete_graph.py` | Rebuild graph structure | ⚠️ Optional |
| `create_full_project_evaluation.py` | Full project evaluation | ⚠️ Optional |

### External Component JSON Files (Reference)
| File | Purpose | Status |
|------|---------|--------|
| `external_area_component.json` | Area component definition | 📚 Reference |
| `external_division_component.json` | Division component definition | 📚 Reference |
| `external_mirror_component.json` | Mirror component definition | 📚 Reference |
| `external_polygon_component.json` | Polygon component definition | 📚 Reference |
| `external_rotate_component.json` | Rotate component definition | 📚 Reference |
| `external_subtraction_components.json` | Subtraction components | 📚 Reference |
| `external_subtraction_e2671ced.json` | Subtraction component | 📚 Reference |
| `external_vector_2pt_1f794702_component.json` | Vector 2Pt component | 📚 Reference |
| `external_vector_d0668a07_component.json` | Vector component | 📚 Reference |
| `external_vector_xyz_component.json` | Vector XYZ component | 📚 Reference |

### Old JSON Files (May contain useful data)
| File | Purpose | Status |
|------|---------|--------|
| `complete_component_graph.json` | Old complete graph | 📚 Archive |
| `rotatingslats_data.json` | Old rotatingslats data | 📚 Archive |
| `rotatingslats_chain_info.json` | Chain information | 📚 Archive |
| `rotatingslats_final_output.json` | Old final output | 📚 Archive |
| `full_project_evaluation.json` | Full project evaluation | 📚 Archive |
| `external_inputs.json` | Old external inputs | 📚 Archive |

### Status/Documentation Files (Historical)
| File | Purpose | Status |
|------|---------|--------|
| `ALL_ERRORS_FIXED_SUMMARY.md` | Error fixes summary | 📚 Historical |
| `AREA_CENTROID_FIX_SUMMARY.md` | Area/Centroid fix | 📚 Historical |
| `CURRENT_SESSION_SUMMARY.md` | Session summary | 📚 Historical |
| `CURRENT_STATUS.md` | Old status | 📚 Historical |
| `ENHANCED_RESULTS_FORMAT.md` | Results format | 📚 Historical |
| `EVALUATION_COMPLETE.md` | Evaluation complete | 📚 Historical |
| `EVALUATION_STATUS_CURRENT.md` | Evaluation status | 📚 Historical |
| `EVALUATOR_STATUS_COMPLETE.md` | Evaluator status | 📚 Historical |
| `EXTERNAL_INPUTS_EXTRACTION_COMPLETE.md` | Extraction complete | 📚 Historical |
| `EXTERNAL_INPUTS_EXTRACTION_SUMMARY.md` | Extraction summary | 📚 Historical |
| `FINAL_EVALUATION_RUN.txt` | Final run log | 📚 Historical |
| `FINAL_EVALUATION_SUMMARY.txt` | Final summary | 📚 Historical |
| `FINAL_VALIDATION_REPORT.md` | Validation report | 📚 Historical |
| `FULL_PROJECT_EVALUATION_REPORT.md` | Full report | 📚 Historical |
| `GHX_VERIFICATION_SUMMARY.md` | GHX verification | 📚 Historical |
| `GRAFTING_FIX_COMPLETE.md` | Grafting fix | 📚 Historical |
| `INVESTIGATION_COMPLETE.md` | Investigation | 📚 Historical |
| `new_sun_geometry_evaluation.md` | Sun geometry | 📚 Historical |
| `PHASE_1_TO_5_SUMMARY.md` | Phase summary | 📚 Historical |
| `ROTATINGSLATS_COMPONENT_REFERENCE.md` | Component reference | 📚 Historical |
| `cursor_*.md` | Cursor session notes | 📚 Historical |

---

## File Categories

### ✅ Active (Required)
Files that are part of the current evaluation workflow and must be present.

### ❌ Obsolete
Files from previous development phases that are no longer used. Can be safely deleted or archived.

### ⚠️ Optional
Utility scripts that may be useful for debugging or analysis but are not required for evaluation.

### 📚 Reference/Archive
Files that contain useful reference data or historical information but are not part of the active workflow.

---

## Cleanup Recommendations

### Safe to Delete
- All files marked as ❌ Obsolete
- Old status/documentation files (unless needed for reference)
- Old JSON files that are superseded by current outputs

### Keep for Reference
- External component JSON files (useful for understanding component structures)
- Historical status files (documentation of development process)
- Utility scripts (may be useful for debugging)

### Required Files (Do Not Delete)
- All files marked as ✅ Active
- Input file: `refactored-no-sun.ghx`
- Generated output files (if you want to keep results)

---

## Workflow Summary

```
1. parse_refactored_ghx.py
   └─> ghx_graph.json, component_index.json, wire_index.json

2. isolate_rotatingslats.py
   └─> rotatingslats_graph.json, rotatingslats_inputs.json

3. gh_evaluator_wired.py
   └─> rotatingslats_evaluation_results.json
```

**Total Active Files**: 5 Python files + 1 input file = 6 files  
**Total Generated Files**: 6 JSON files  
**Total Required**: 12 files

