// Derived from evaluate_box_2pt in gh_components_stripped.py

#include "Box2Pt.h"

void Box2Pt_eval(const Box2PtInput *in, Box2PtOutput *out) {
    // GH Box 2Pt: create box from corners
    out->corner_a[0] = in->point_a[0];
    out->corner_a[1] = in->point_a[1];
    out->corner_a[2] = in->point_a[2];
    
    out->corner_b[0] = in->point_b[0];
    out->corner_b[1] = in->point_b[1];
    out->corner_b[2] = in->point_b[2];
}

