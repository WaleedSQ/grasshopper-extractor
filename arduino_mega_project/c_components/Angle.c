// Derived from evaluate_angle in gh_components_stripped.py

#include "Angle.h"
#include <math.h>
#include <stdbool.h>
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
        out[2] = 0.0f;
    }
}

static float compute_angle(const float vec_a[3], const float vec_b[3], 
                          const float plane_normal[3], bool use_oriented) {
    float a_unit[3], b_unit[3];
    normalize_vec(vec_a, a_unit);
    normalize_vec(vec_b, b_unit);
    
    float dot_raw = vec_a[0] * vec_b[0] + vec_a[1] * vec_b[1] + vec_a[2] * vec_b[2];
    
    float mag_a = sqrtf(vec_a[0]*vec_a[0] + vec_a[1]*vec_a[1] + vec_a[2]*vec_a[2]);
    float mag_b = sqrtf(vec_b[0]*vec_b[0] + vec_b[1]*vec_b[1] + vec_b[2]*vec_b[2]);
    
    if (mag_a == 0.0f || mag_b == 0.0f) {
        return 0.0f;
    }
    
    float cos_angle = dot_raw / (mag_a * mag_b);
    if (cos_angle > 1.0f) cos_angle = 1.0f;
    if (cos_angle < -1.0f) cos_angle = -1.0f;
    
    float angle = acosf(cos_angle);
    
    if (use_oriented) {
        float n_unit[3];
        normalize_vec(plane_normal, n_unit);
        
        float cross[3] = {
            a_unit[1] * b_unit[2] - a_unit[2] * b_unit[1],
            a_unit[2] * b_unit[0] - a_unit[0] * b_unit[2],
            a_unit[0] * b_unit[1] - a_unit[1] * b_unit[0]
        };
        
        float sign = cross[0] * n_unit[0] + cross[1] * n_unit[1] + cross[2] * n_unit[2];
        
        if (sign <= 0.0f) {
            angle = (2.0f * 3.14159265358979323846f) - angle;
        }
    }
    
    return angle;
}

void Angle_eval(const AngleInput *in, AngleOutput *out) {
    memset(out, 0, sizeof(AngleOutput));

    // List mode: multiple angle calculations
    if (in->angle_count > 0) {
        int count = in->angle_count;
        if (count > ANGLE_MAX_ITEMS) count = ANGLE_MAX_ITEMS;

        for (int i = 0; i < count; ++i) {
            out->angles[i] = compute_angle(in->vectors_a[i], in->vectors_b[i],
                                          in->plane_normals[i], in->use_oriented);
        }
        out->angle_count = count;

        // Backward-compatible single angle = first element
        out->angle = out->angles[0];
        return;
    }

    // Single angle mode (backward compatible)
    out->angle = compute_angle(in->vector_a, in->vector_b, in->plane_normal, in->use_oriented);
}

