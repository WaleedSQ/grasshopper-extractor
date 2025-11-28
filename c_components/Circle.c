// Derived from evaluate_circle in gh_components_stripped.py

#include "Circle.h"

void Circle_eval(const CircleInput *in, CircleOutput *out) {
    // GH Circle: create circle from plane and radius
    // Circle center is at plane origin
    out->center[0] = in->plane_origin[0];
    out->center[1] = in->plane_origin[1];
    out->center[2] = in->plane_origin[2];
    out->radius = in->radius;
}

