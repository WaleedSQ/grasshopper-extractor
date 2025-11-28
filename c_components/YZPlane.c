// Derived from evaluate_yz_plane in gh_components_stripped.py

#include "YZPlane.h"

void YZPlane_eval(const YZPlaneInput *in, YZPlaneOutput *out) {
    // GH YZ Plane: plane with origin and X-axis normal
    // Plane axes lie in the YZ plane; normal points along +X
    out->origin[0] = in->origin[0];
    out->origin[1] = in->origin[1];
    out->origin[2] = in->origin[2];
    
    out->x_axis[0] = 0.0f;
    out->x_axis[1] = 1.0f;
    out->x_axis[2] = 0.0f;  // Along world Y
    
    out->y_axis[0] = 0.0f;
    out->y_axis[1] = 0.0f;
    out->y_axis[2] = 1.0f;  // Along world Z
    
    out->z_axis[0] = 1.0f;
    out->z_axis[1] = 0.0f;
    out->z_axis[2] = 0.0f;  // Normal to YZ plane (+X)
}

