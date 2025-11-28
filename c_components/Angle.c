// Derived from evaluate_angle in gh_components_stripped.py

#include "Angle.h"
#include <math.h>
#include <stdbool.h>

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

void Angle_eval(const AngleInput *in, AngleOutput *out) {
    // GH Angle: compute angle between vectors using dot product
    float a_unit[3], b_unit[3];
    normalize_vec(in->vector_a, a_unit);
    normalize_vec(in->vector_b, b_unit);
    
    float dot_raw = in->vector_a[0] * in->vector_b[0] +
                    in->vector_a[1] * in->vector_b[1] +
                    in->vector_a[2] * in->vector_b[2];
    
    float mag_a = sqrtf(in->vector_a[0]*in->vector_a[0] +
                       in->vector_a[1]*in->vector_a[1] +
                       in->vector_a[2]*in->vector_a[2]);
    float mag_b = sqrtf(in->vector_b[0]*in->vector_b[0] +
                       in->vector_b[1]*in->vector_b[1] +
                       in->vector_b[2]*in->vector_b[2]);
    
    if (mag_a == 0.0f || mag_b == 0.0f) {
        out->angle = 0.0f;
        return;
    }
    
    float cos_angle = dot_raw / (mag_a * mag_b);
    // Clamp to [-1, 1] to avoid numerical errors
    if (cos_angle > 1.0f) cos_angle = 1.0f;
    if (cos_angle < -1.0f) cos_angle = -1.0f;
    
    float angle = acosf(cos_angle);
    
    // If plane normal provided and use_oriented is true, compute oriented angle
    if (in->use_oriented) {
        float n_unit[3];
        normalize_vec(in->plane_normal, n_unit);
        
        // Cross product: a_unit × b_unit
        float cross[3] = {
            a_unit[1] * b_unit[2] - a_unit[2] * b_unit[1],
            a_unit[2] * b_unit[0] - a_unit[0] * b_unit[2],
            a_unit[0] * b_unit[1] - a_unit[1] * b_unit[0]
        };
        
        float sign = cross[0] * n_unit[0] + cross[1] * n_unit[1] + cross[2] * n_unit[2];
        
        // GH oriented angle: if cross is aligned with plane normal, keep angle; otherwise take reflex
        if (sign <= 0.0f) {
            angle = (2.0f * 3.14159265358979323846f) - angle;
        }
    }
    
    out->angle = angle;
}

