#ifndef ROTATE_H
#define ROTATE_H

// Derived from evaluate_rotate in gh_components_stripped.py

typedef struct {
    int geometry_type;  // 0=point, 1=line, 2=rectangle, 3=box, 4=plane
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
} RotateInput;

typedef struct {
    int geometry_type;
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
} RotateOutput;

void Rotate_eval(const RotateInput *in, RotateOutput *out);

#endif // ROTATE_H

