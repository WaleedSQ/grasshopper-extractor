// Derived from evaluate_vector_2pt in gh_components_stripped.py

#include "Vector2Pt.h"
#include <math.h>
#include <stdbool.h>

void Vector2Pt_eval(const Vector2PtInput *in, Vector2PtOutput *out) {
    // Initialize output
    out->vector[0] = 0.0f;
    out->vector[1] = 0.0f;
    out->vector[2] = 0.0f;
    out->vector_count = 0;
    for (int i = 0; i < VECTOR2PT_MAX_COUNT; i++) {
        out->vectors[i][0] = 0.0f;
        out->vectors[i][1] = 0.0f;
        out->vectors[i][2] = 0.0f;
    }
    
    if (in->point_count > 0) {
        // Process array of point pairs (matching Python: for a_pt, b_pt, unitize in zip(...))
        int count = in->point_count;
        if (count > VECTOR2PT_MAX_COUNT) {
            count = VECTOR2PT_MAX_COUNT;
        }
        for (int i = 0; i < count; i++) {
            // GH Vector 2Pt: vector = B - A
            float vx = in->points_b[i][0] - in->points_a[i][0];
            float vy = in->points_b[i][1] - in->points_a[i][1];
            float vz = in->points_b[i][2] - in->points_a[i][2];
            
            // GH Vector 2Pt: unitize if requested
            if (in->unitize) {
                float length = sqrtf(vx*vx + vy*vy + vz*vz);
                if (length > 0.0f) {
                    vx = vx / length;
                    vy = vy / length;
                    vz = vz / length;
                }
            }
            
            out->vectors[i][0] = vx;
            out->vectors[i][1] = vy;
            out->vectors[i][2] = vz;
        }
        out->vector_count = count;
        // Also set single vector to first value for backward compatibility
        out->vector[0] = out->vectors[0][0];
        out->vector[1] = out->vectors[0][1];
        out->vector[2] = out->vectors[0][2];
    } else {
        // Single point pair mode (backward compatibility)
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
        out->vector_count = 0;
    }
}

