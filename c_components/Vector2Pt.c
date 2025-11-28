// Derived from evaluate_vector_2pt in gh_components_stripped.py

#include "Vector2Pt.h"
#include <math.h>
#include <stdbool.h>

void Vector2Pt_eval(const Vector2PtInput *in, Vector2PtOutput *out) {
    // GH Vector 2Pt: vector = B - A
    float vx = in->point_b[0] - in->point_a[0];
    float vy = in->point_b[1] - in->point_a[1];
    float vz = in->point_b[2] - in->point_a[2];
    
    // GH Vector 2Pt: unitize if requested
    if (in->unitize) {
        float length = sqrtf(vx*vx + vy*vy + vz*vz);
        if (length > 0.0f) {
            vx = vx / length;
            vy = vy / length;
            vz = vz / length;
        }
    }
    
    out->vector[0] = vx;
    out->vector[1] = vy;
    out->vector[2] = vz;
}

