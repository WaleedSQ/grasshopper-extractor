#ifndef CIRCLE_H
#define CIRCLE_H

// Derived from evaluate_circle in gh_components_stripped.py

#define CIRCLE_MAX_ITEMS 100

typedef struct {
    // Single circle mode (backward compatible)
    float plane_origin[3];
    float plane_x_axis[3];
    float plane_y_axis[3];
    float plane_z_axis[3];
    float radius;

    // List mode: multiple circles (all with same radius)
    float plane_origins[CIRCLE_MAX_ITEMS][3];
    float plane_x_axes[CIRCLE_MAX_ITEMS][3];
    float plane_y_axes[CIRCLE_MAX_ITEMS][3];
    float plane_z_axes[CIRCLE_MAX_ITEMS][3];
    int circle_count;  // 0 => use single plane_origin/axes/radius above
} CircleInput;

typedef struct {
    // Single circle output (backward compatible)
    float center[3];
    float radius;

    // List mode outputs
    float centers[CIRCLE_MAX_ITEMS][3];
    int circle_count;
} CircleOutput;

void Circle_eval(const CircleInput *in, CircleOutput *out);

#endif // CIRCLE_H

