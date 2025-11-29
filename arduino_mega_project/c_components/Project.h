#ifndef PROJECT_H
#define PROJECT_H

// Derived from evaluate_project in gh_components_stripped.py
//
// List mode notes:
// - When curve_type == 1 (line) and line_count > 0, Project_eval
//   projects each (line_starts[i], line_ends[i]) pair and fills
//   line_starts/line_ends in the output, plus a single line_start/end
//   from the first item for backward compatibility.
// - When line_count == 0, existing single-geometry behavior is used.
//
#define PROJECT_MAX_ITEMS 100

typedef struct {
    int curve_type;  // 0=point, 1=line

    // Single-curve fields
    float point[3];
    float line_start[3];
    float line_end[3];

    int brep_type;  // 0=plane, 1=box
    float plane_origin[3];
    float plane_z_axis[3];
    float box_corner_a[3];
    float box_corner_b[3];
    float direction[3];

    // List mode (used for multiple lines onto common brep)
    float line_starts[PROJECT_MAX_ITEMS][3];
    float line_ends[PROJECT_MAX_ITEMS][3];
    int line_count;  // 0 => use single line_start/line_end
} ProjectInput;

typedef struct {
    int curve_type;  // 0=point, 1=line

    // Single-curve outputs
    float point[3];
    float line_start[3];
    float line_end[3];

    // List mode outputs
    float line_starts[PROJECT_MAX_ITEMS][3];
    float line_ends[PROJECT_MAX_ITEMS][3];
    int line_count;
} ProjectOutput;

void Project_eval(const ProjectInput *in, ProjectOutput *out);

#endif // PROJECT_H


