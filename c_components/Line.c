// Derived from evaluate_line in gh_components_stripped.py

#include "Line.h"
#include <math.h>
#include <stdbool.h>
#include <string.h>

void Line_eval(const LineInput *in, LineOutput *out) {
    memset(out, 0, sizeof(LineOutput));

    // List mode: use_two_points with arrays of start/end
    if (in->use_two_points && in->line_count > 0) {
        int count = in->line_count;
        if (count > LINE_MAX_ITEMS) count = LINE_MAX_ITEMS;

        for (int i = 0; i < count; ++i) {
            out->starts[i][0] = in->start_points[i][0];
            out->starts[i][1] = in->start_points[i][1];
            out->starts[i][2] = in->start_points[i][2];

            out->ends[i][0] = in->end_points[i][0];
            out->ends[i][1] = in->end_points[i][1];
            out->ends[i][2] = in->end_points[i][2];
        }
        out->line_count = count;

        // Backward-compatible single line = first element
        out->start[0] = out->starts[0][0];
        out->start[1] = out->starts[0][1];
        out->start[2] = out->starts[0][2];

        out->end[0] = out->ends[0][0];
        out->end[1] = out->ends[0][1];
        out->end[2] = out->ends[0][2];
        return;
    }

    // Single-geometry mode (unchanged behavior)
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


