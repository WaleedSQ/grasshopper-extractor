#ifndef CIRCLE_H
#define CIRCLE_H

// Derived from evaluate_circle in gh_components_stripped.py

typedef struct {
    float plane_origin[3];
    float plane_x_axis[3];
    float plane_y_axis[3];
    float plane_z_axis[3];
    float radius;
} CircleInput;

typedef struct {
    float center[3];
    float radius;
} CircleOutput;

void Circle_eval(const CircleInput *in, CircleOutput *out);

#endif // CIRCLE_H

