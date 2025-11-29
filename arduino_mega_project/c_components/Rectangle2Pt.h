#ifndef RECTANGLE2PT_H
#define RECTANGLE2PT_H

// Derived from evaluate_rectangle_2pt in gh_components_stripped.py

typedef struct {
    float plane_origin[3];
    float plane_x_axis[3];
    float plane_y_axis[3];
    float plane_z_axis[3];
    float point_a[3];
    float point_b[3];
} Rectangle2PtInput;

typedef struct {
    float corners[4][3];
} Rectangle2PtOutput;

void Rectangle2Pt_eval(const Rectangle2PtInput *in, Rectangle2PtOutput *out);

#endif // RECTANGLE2PT_H

