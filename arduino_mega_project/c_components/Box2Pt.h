#ifndef BOX2PT_H
#define BOX2PT_H

// Derived from evaluate_box_2pt in gh_components_stripped.py

typedef struct {
    float plane_origin[3];
    float plane_x_axis[3];
    float plane_y_axis[3];
    float plane_z_axis[3];
    float point_a[3];
    float point_b[3];
} Box2PtInput;

typedef struct {
    float corner_a[3];
    float corner_b[3];
} Box2PtOutput;

void Box2Pt_eval(const Box2PtInput *in, Box2PtOutput *out);

#endif // BOX2PT_H

