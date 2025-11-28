// Derived from evaluate_construct_plane in gh_components_stripped.py

#include "ConstructPlane.h"
#include <math.h>

static void normalize_vec(const float vec[3], float out[3]) {
    float length = sqrtf(vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2]);
    if (length > 0.0f) {
        out[0] = vec[0] / length;
        out[1] = vec[1] / length;
        out[2] = vec[2] / length;
    } else {
        out[0] = 1.0f;
        out[1] = 0.0f;
        out[2] = 0.0f;
    }
}

void ConstructPlane_eval(const ConstructPlaneInput *in, ConstructPlaneOutput *out) {
    // GH Construct Plane: create plane from origin and X, Y axes
    out->origin[0] = in->origin[0];
    out->origin[1] = in->origin[1];
    out->origin[2] = in->origin[2];
    
    // Normalize X-axis
    normalize_vec(in->x_axis, out->x_axis);
    
    // Normalize Y-axis
    normalize_vec(in->y_axis, out->y_axis);
    
    // Z = X cross Y
    out->z_axis[0] = out->x_axis[1] * out->y_axis[2] - out->x_axis[2] * out->y_axis[1];
    out->z_axis[1] = out->x_axis[2] * out->y_axis[0] - out->x_axis[0] * out->y_axis[2];
    out->z_axis[2] = out->x_axis[0] * out->y_axis[1] - out->x_axis[1] * out->y_axis[0];
    
    float z_len = sqrtf(out->z_axis[0]*out->z_axis[0] +
                       out->z_axis[1]*out->z_axis[1] +
                       out->z_axis[2]*out->z_axis[2]);
    
    if (z_len > 0.0f) {
        out->z_axis[0] = out->z_axis[0] / z_len;
        out->z_axis[1] = out->z_axis[1] / z_len;
        out->z_axis[2] = out->z_axis[2] / z_len;
    } else {
        out->z_axis[0] = 0.0f;
        out->z_axis[1] = 0.0f;
        out->z_axis[2] = 1.0f;
    }
}

