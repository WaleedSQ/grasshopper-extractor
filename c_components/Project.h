#ifndef PROJECT_H
#define PROJECT_H

// Derived from evaluate_project in gh_components_stripped.py

typedef struct {
    int curve_type;  // 0=point, 1=line
    float point[3];
    float line_start[3];
    float line_end[3];
    int brep_type;  // 0=plane, 1=box
    float plane_origin[3];
    float plane_z_axis[3];
    float box_corner_a[3];
    float box_corner_b[3];
    float direction[3];
} ProjectInput;

typedef struct {
    int curve_type;  // 0=point, 1=line
    float point[3];
    float line_start[3];
    float line_end[3];
} ProjectOutput;

void Project_eval(const ProjectInput *in, ProjectOutput *out);

#endif // PROJECT_H

