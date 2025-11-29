// Derived from evaluate_circle in gh_components_stripped.py

#include "Circle.h"
#include <string.h>

void Circle_eval(const CircleInput *in, CircleOutput *out) {
    memset(out, 0, sizeof(CircleOutput));

    // List mode: multiple circles
    if (in->circle_count > 0) {
        int count = in->circle_count;
        if (count > CIRCLE_MAX_ITEMS) count = CIRCLE_MAX_ITEMS;

        for (int i = 0; i < count; ++i) {
            // Circle center is at plane origin
            out->centers[i][0] = in->plane_origins[i][0];
            out->centers[i][1] = in->plane_origins[i][1];
            out->centers[i][2] = in->plane_origins[i][2];
        }
        out->circle_count = count;
        out->radius = in->radius;

        // Backward-compatible single circle = first element
        out->center[0] = out->centers[0][0];
        out->center[1] = out->centers[0][1];
        out->center[2] = out->centers[0][2];
        return;
    }

    // Single circle mode (backward compatible)
    out->center[0] = in->plane_origin[0];
    out->center[1] = in->plane_origin[1];
    out->center[2] = in->plane_origin[2];
    out->radius = in->radius;
}

