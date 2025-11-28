// Derived from evaluate_area in gh_components_stripped.py

#include "Area.h"

void Area_eval(const AreaInput *in, AreaOutput *out) {
    // GH Area: compute centroid based on geometry type
    if (in->geometry_type == 0) {
        // Line segment - Grasshopper returns midpoint as "centroid"
        out->centroid[0] = (in->line_start[0] + in->line_end[0]) / 2.0f;
        out->centroid[1] = (in->line_start[1] + in->line_end[1]) / 2.0f;
        out->centroid[2] = (in->line_start[2] + in->line_end[2]) / 2.0f;
    } else if (in->geometry_type == 1) {
        // Polyline - centroid is average of all vertices
        if (in->polyline_count > 0) {
            float sum_x = 0.0f, sum_y = 0.0f, sum_z = 0.0f;
            for (int i = 0; i < in->polyline_count; i++) {
                sum_x += in->polyline_vertices[i][0];
                sum_y += in->polyline_vertices[i][1];
                sum_z += in->polyline_vertices[i][2];
            }
            out->centroid[0] = sum_x / in->polyline_count;
            out->centroid[1] = sum_y / in->polyline_count;
            out->centroid[2] = sum_z / in->polyline_count;
        } else {
            out->centroid[0] = 0.0f;
            out->centroid[1] = 0.0f;
            out->centroid[2] = 0.0f;
        }
    } else if (in->geometry_type == 2) {
        // Rectangle - centroid is average of corners
        out->centroid[0] = (in->rectangle_corners[0][0] + in->rectangle_corners[1][0] +
                           in->rectangle_corners[2][0] + in->rectangle_corners[3][0]) / 4.0f;
        out->centroid[1] = (in->rectangle_corners[0][1] + in->rectangle_corners[1][1] +
                           in->rectangle_corners[2][1] + in->rectangle_corners[3][1]) / 4.0f;
        out->centroid[2] = (in->rectangle_corners[0][2] + in->rectangle_corners[1][2] +
                           in->rectangle_corners[2][2] + in->rectangle_corners[3][2]) / 4.0f;
    } else if (in->geometry_type == 3) {
        // Box - centroid is midpoint of diagonal
        out->centroid[0] = (in->box_corner_a[0] + in->box_corner_b[0]) / 2.0f;
        out->centroid[1] = (in->box_corner_a[1] + in->box_corner_b[1]) / 2.0f;
        out->centroid[2] = (in->box_corner_a[2] + in->box_corner_b[2]) / 2.0f;
    } else {
        out->centroid[0] = 0.0f;
        out->centroid[1] = 0.0f;
        out->centroid[2] = 0.0f;
    }
}

