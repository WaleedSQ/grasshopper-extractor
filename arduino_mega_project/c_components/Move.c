// Derived from evaluate_move in gh_components_stripped.py

#include "Move.h"
#include <string.h>

void Move_eval(const MoveInput *in, MoveOutput *out) {
    // Initialize everything
    memset(out, 0, sizeof(MoveOutput));

    out->geometry_type = in->geometry_type;

    float mx = in->motion[0];
    float my = in->motion[1];
    float mz = in->motion[2];

    // List mode for points (matches Python per-item loop over points with a shared motion)
    if (in->geometry_type == 0 && in->point_count > 0) {
        int count = in->point_count;
        if (count > MOVE_MAX_ITEMS) count = MOVE_MAX_ITEMS;

        for (int i = 0; i < count; ++i) {
            out->points[i][0] = in->points[i][0] + mx;
            out->points[i][1] = in->points[i][1] + my;
            out->points[i][2] = in->points[i][2] + mz;
        }
        out->point_count = count;

        // Backward-compatible single point = first element
        out->point[0] = out->points[0][0];
        out->point[1] = out->points[0][1];
        out->point[2] = out->points[0][2];
        return;
    }

    // List mode for rectangles (each rectangle moved by its corresponding motion)
    if (in->geometry_type == 2 && in->rectangle_count > 0) {
        int count = in->rectangle_count;
        if (count > MOVE_MAX_ITEMS) count = MOVE_MAX_ITEMS;

        for (int i = 0; i < count; ++i) {
            float mxi = in->motions[i][0];
            float myi = in->motions[i][1];
            float mzi = in->motions[i][2];
            for (int k = 0; k < 4; k++) {
                out->rectangles[i][k][0] = in->rectangles[i][k][0] + mxi;
                out->rectangles[i][k][1] = in->rectangles[i][k][1] + myi;
                out->rectangles[i][k][2] = in->rectangles[i][k][2] + mzi;
            }
        }
        out->rectangle_count = count;

        // Backward-compatible single rectangle = first element
        for (int k = 0; k < 4; k++) {
            out->rectangle_corners[k][0] = out->rectangles[0][k][0];
            out->rectangle_corners[k][1] = out->rectangles[0][k][1];
            out->rectangle_corners[k][2] = out->rectangles[0][k][2];
        }
        return;
    }

    // Single-geometry mode (existing behavior)
    if (in->geometry_type == 0) {
        // Point
        out->point[0] = in->point[0] + mx;
        out->point[1] = in->point[1] + my;
        out->point[2] = in->point[2] + mz;
    } else if (in->geometry_type == 1) {
        // Line
        out->line_start[0] = in->line_start[0] + mx;
        out->line_start[1] = in->line_start[1] + my;
        out->line_start[2] = in->line_start[2] + mz;

        out->line_end[0] = in->line_end[0] + mx;
        out->line_end[1] = in->line_end[1] + my;
        out->line_end[2] = in->line_end[2] + mz;
    } else if (in->geometry_type == 2) {
        // Rectangle
        for (int i = 0; i < 4; i++) {
            out->rectangle_corners[i][0] = in->rectangle_corners[i][0] + mx;
            out->rectangle_corners[i][1] = in->rectangle_corners[i][1] + my;
            out->rectangle_corners[i][2] = in->rectangle_corners[i][2] + mz;
        }
    } else if (in->geometry_type == 3) {
        // Box
        out->box_corner_a[0] = in->box_corner_a[0] + mx;
        out->box_corner_a[1] = in->box_corner_a[1] + my;
        out->box_corner_a[2] = in->box_corner_a[2] + mz;

        out->box_corner_b[0] = in->box_corner_b[0] + mx;
        out->box_corner_b[1] = in->box_corner_b[1] + my;
        out->box_corner_b[2] = in->box_corner_b[2] + mz;
    }
}


