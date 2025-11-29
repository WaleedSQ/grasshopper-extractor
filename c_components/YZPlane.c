// Derived from evaluate_yz_plane in gh_components_stripped.py

#include "YZPlane.h"
#include <string.h>

void YZPlane_eval(const YZPlaneInput *in, YZPlaneOutput *out) {
    memset(out, 0, sizeof(YZPlaneOutput));

    // List mode: multiple planes
    if (in->plane_count > 0) {
        int count = in->plane_count;
        if (count > YZPLANE_MAX_ITEMS) count = YZPLANE_MAX_ITEMS;

        for (int i = 0; i < count; ++i) {
            out->origins[i][0] = in->origins[i][0];
            out->origins[i][1] = in->origins[i][1];
            out->origins[i][2] = in->origins[i][2];
            
            // Fixed axes for YZ plane
            out->x_axes[i][0] = 0.0f;
            out->x_axes[i][1] = 1.0f;
            out->x_axes[i][2] = 0.0f;  // Along world Y
            
            out->y_axes[i][0] = 0.0f;
            out->y_axes[i][1] = 0.0f;
            out->y_axes[i][2] = 1.0f;  // Along world Z
            
            out->z_axes[i][0] = 1.0f;
            out->z_axes[i][1] = 0.0f;
            out->z_axes[i][2] = 0.0f;  // Normal to YZ plane (+X)
        }
        out->plane_count = count;

        // Backward-compatible single plane = first element
        out->origin[0] = out->origins[0][0];
        out->origin[1] = out->origins[0][1];
        out->origin[2] = out->origins[0][2];
        out->x_axis[0] = out->x_axes[0][0];
        out->x_axis[1] = out->x_axes[0][1];
        out->x_axis[2] = out->x_axes[0][2];
        out->y_axis[0] = out->y_axes[0][0];
        out->y_axis[1] = out->y_axes[0][1];
        out->y_axis[2] = out->y_axes[0][2];
        out->z_axis[0] = out->z_axes[0][0];
        out->z_axis[1] = out->z_axes[0][1];
        out->z_axis[2] = out->z_axes[0][2];
        return;
    }

    // Single plane mode (backward compatible)
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

