// Derived from evaluate_move in gh_components_stripped.py

#include "Move.h"

void Move_eval(const MoveInput *in, MoveOutput *out) {
    // GH Move: translate geometry by motion vector
    out->geometry_type = in->geometry_type;
    
    float mx = in->motion[0];
    float my = in->motion[1];
    float mz = in->motion[2];
    
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

