// Derived from evaluate_plane_normal in gh_components_stripped.py

#include "PlaneNormal.h"
#include <math.h>

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

void PlaneNormal_eval(const PlaneNormalInput *in, PlaneNormalOutput *out) {
    // GH Plane Normal: constructs a plane from origin + z-axis
    out->origin[0] = in->origin[0];
    out->origin[1] = in->origin[1];
    out->origin[2] = in->origin[2];
    
    // Normalize Z-axis
    normalize_vec(in->z_axis, out->z_axis);
    
    // GH Plane Normal: construct X and Y axes perpendicular to Z
    // Find the axis that is least aligned with Z to use as reference
    float ref[3];
    if (fabsf(out->z_axis[0]) <= fabsf(out->z_axis[1]) && 
        fabsf(out->z_axis[0]) <= fabsf(out->z_axis[2])) {
        ref[0] = 1.0f;
        ref[1] = 0.0f;
        ref[2] = 0.0f;
    } else if (fabsf(out->z_axis[1]) <= fabsf(out->z_axis[2])) {
        ref[0] = 0.0f;
        ref[1] = 1.0f;
        ref[2] = 0.0f;
    } else {
        ref[0] = 0.0f;
        ref[1] = 0.0f;
        ref[2] = 1.0f;
    }
    
    // X-axis = ref projected onto plane perpendicular to Z, normalized
    float ref_dot_z = ref[0]*out->z_axis[0] + ref[1]*out->z_axis[1] + ref[2]*out->z_axis[2];
    float x_axis[3] = {
        ref[0] - ref_dot_z * out->z_axis[0],
        ref[1] - ref_dot_z * out->z_axis[1],
        ref[2] - ref_dot_z * out->z_axis[2]
    };
    normalize_vec(x_axis, out->x_axis);
    
    // Y-axis = cross(Z, X)
    out->y_axis[0] = out->z_axis[1] * out->x_axis[2] - out->z_axis[2] * out->x_axis[1];
    out->y_axis[1] = out->z_axis[2] * out->x_axis[0] - out->z_axis[0] * out->x_axis[2];
    out->y_axis[2] = out->z_axis[0] * out->x_axis[1] - out->z_axis[1] * out->x_axis[0];
}

