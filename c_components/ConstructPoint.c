// Derived from evaluate_construct_point in gh_components_stripped.py

#include "ConstructPoint.h"

void ConstructPoint_eval(const ConstructPointInput *in, ConstructPointOutput *out) {
    // GH Construct Point: point = [x, y, z]
    out->point[0] = in->x;
    out->point[1] = in->y;
    out->point[2] = in->z;
}

