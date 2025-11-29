#ifndef ROTATE_H
#define ROTATE_H

// Derived from evaluate_rotate in gh_components_stripped.py

#define ROTATE_MAX_ITEMS 100

typedef struct {
    int geometry_type;  // 0=point, 1=line, 2=rectangle, 3=box, 4=plane

    // Single-geometry fields (backward compatible)
    float point[3];
    float line_start[3];
    float line_end[3];
    float rectangle_corners[4][3];
    float box_corner_a[3];
    float box_corner_b[3];
    float plane_origin[3];
    float plane_x_axis[3];
    float plane_y_axis[3];
    float plane_z_axis[3];
    float angle;  // Rotation angle in radians
    float rot_origin[3];
    float rot_axis[3];

    // List mode for points
    float points[ROTATE_MAX_ITEMS][3];
    int point_count;  // 0 => use single point above

    // List mode for rectangles (all rotated by same angle)
    float rectangles[ROTATE_MAX_ITEMS][4][3];
    int rectangle_count;  // 0 => use single rectangle_corners above
} RotateInput;

typedef struct {
    int geometry_type;

    // Single-geometry outputs (backward compatible)
    float point[3];
    float line_start[3];
    float line_end[3];
    float rectangle_corners[4][3];
    float box_corner_a[3];
    float box_corner_b[3];
    float plane_origin[3];
    float plane_x_axis[3];
    float plane_y_axis[3];
    float plane_z_axis[3];

    // List mode outputs for points
    float points[ROTATE_MAX_ITEMS][3];
    int point_count;

    // List mode outputs for rectangles
    float rectangles[ROTATE_MAX_ITEMS][4][3];
    int rectangle_count;
} RotateOutput;

void Rotate_eval(const RotateInput *in, RotateOutput *out);

#endif // ROTATE_H

