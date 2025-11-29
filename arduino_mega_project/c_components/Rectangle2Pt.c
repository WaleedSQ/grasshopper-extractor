// Derived from evaluate_rectangle_2pt in gh_components_stripped.py

#include "Rectangle2Pt.h"

void Rectangle2Pt_eval(const Rectangle2PtInput *in, Rectangle2PtOutput *out) {
    // GH Rectangle 2Pt: create rectangle from two diagonal corners
    // Compute rectangle corners
    out->corners[0][0] = in->point_a[0];
    out->corners[0][1] = in->point_a[1];
    out->corners[0][2] = in->point_a[2];
    
    out->corners[1][0] = in->point_b[0];
    out->corners[1][1] = in->point_a[1];
    out->corners[1][2] = in->point_a[2];
    
    out->corners[2][0] = in->point_b[0];
    out->corners[2][1] = in->point_b[1];
    out->corners[2][2] = in->point_b[2];
    
    out->corners[3][0] = in->point_a[0];
    out->corners[3][1] = in->point_b[1];
    out->corners[3][2] = in->point_a[2];
}

