// Derived from evaluate_plane_normal in gh_components_stripped.py

#include "PlaneNormal.h"
#include <math.h>
#include <string.h>

static void normalize_vec(const float vec[3], float out[3]) {
    float length = sqrtf(vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2]);
    if (length > 0.0f) {
        out[0] = vec[0] / length;
        out[1] = vec[1] / length;
        out[2] = vec[2] / length;
    } else {
        out[0] = 0.0f;
        out[1] = 0.0f;
        out[2] = 1.0f;
    }
}

static void compute_plane_axes(const float z_axis[3], float x_axis_out[3], float y_axis_out[3]) {
    // Normalize Z-axis
    float z_norm[3];
    normalize_vec(z_axis, z_norm);
    
    // Find the axis that is least aligned with Z to use as reference
    float ref[3];
    if (fabsf(z_norm[0]) <= fabsf(z_norm[1]) && 
        fabsf(z_norm[0]) <= fabsf(z_norm[2])) {
        ref[0] = 1.0f;
        ref[1] = 0.0f;
        ref[2] = 0.0f;
    } else if (fabsf(z_norm[1]) <= fabsf(z_norm[2])) {
        ref[0] = 0.0f;
        ref[1] = 1.0f;
        ref[2] = 0.0f;
    } else {
        ref[0] = 0.0f;
        ref[1] = 0.0f;
        ref[2] = 1.0f;
    }
    
    // X-axis = ref projected onto plane perpendicular to Z, normalized
    float ref_dot_z = ref[0]*z_norm[0] + ref[1]*z_norm[1] + ref[2]*z_norm[2];
    float x_axis[3] = {
        ref[0] - ref_dot_z * z_norm[0],
        ref[1] - ref_dot_z * z_norm[1],
        ref[2] - ref_dot_z * z_norm[2]
    };
    normalize_vec(x_axis, x_axis_out);
    
    // Y-axis = cross(Z, X)
    y_axis_out[0] = z_norm[1] * x_axis_out[2] - z_norm[2] * x_axis_out[1];
    y_axis_out[1] = z_norm[2] * x_axis_out[0] - z_norm[0] * x_axis_out[2];
    y_axis_out[2] = z_norm[0] * x_axis_out[1] - z_norm[1] * x_axis_out[0];
}

void PlaneNormal_eval(const PlaneNormalInput *in, PlaneNormalOutput *out) {
    memset(out, 0, sizeof(PlaneNormalOutput));

    // List mode: multiple planes
    if (in->plane_count > 0) {
        int count = in->plane_count;
        if (count > PLANENORMAL_MAX_ITEMS) count = PLANENORMAL_MAX_ITEMS;

        for (int i = 0; i < count; ++i) {
            out->origins[i][0] = in->origins[i][0];
            out->origins[i][1] = in->origins[i][1];
            out->origins[i][2] = in->origins[i][2];
            
            compute_plane_axes(in->z_axes[i], out->x_axes[i], out->y_axes[i]);
            normalize_vec(in->z_axes[i], out->z_axes[i]);
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
    
    compute_plane_axes(in->z_axis, out->x_axis, out->y_axis);
    normalize_vec(in->z_axis, out->z_axis);
}

