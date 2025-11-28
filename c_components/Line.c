// Derived from evaluate_line in gh_components_stripped.py

#include "Line.h"
#include <math.h>
#include <stdbool.h>

void Line_eval(const LineInput *in, LineOutput *out) {
    if (in->use_two_points) {
        // Mode 1: Start Point + End Point
        out->start[0] = in->start_point[0];
        out->start[1] = in->start_point[1];
        out->start[2] = in->start_point[2];
        
        out->end[0] = in->end_point[0];
        out->end[1] = in->end_point[1];
        out->end[2] = in->end_point[2];
    } else {
        // Mode 2: Start Point + Direction (+ optional Length)
        out->start[0] = in->start_point[0];
        out->start[1] = in->start_point[1];
        out->start[2] = in->start_point[2];
        
        float dx = in->direction[0];
        float dy = in->direction[1];
        float dz = in->direction[2];
        float dir_len = sqrtf(dx*dx + dy*dy + dz*dz);
        
        float use_len = (in->length > 0.0f) ? in->length : dir_len;
        
        if (dir_len == 0.0f) {
            out->end[0] = in->start_point[0];
            out->end[1] = in->start_point[1];
            out->end[2] = in->start_point[2];
        } else {
            float scale = use_len / dir_len;
            out->end[0] = in->start_point[0] + dx * scale;
            out->end[1] = in->start_point[1] + dy * scale;
            out->end[2] = in->start_point[2] + dz * scale;
        }
    }
}

