// Derived from evaluate_area in gh_components_stripped.py

#include "Area.h"
#include <string.h>

void Area_eval(const AreaInput *in, AreaOutput *out) {
    // Initialize output
    memset(out, 0, sizeof(AreaOutput));

    // List mode: multiple rectangles
    if (in->rectangle_count > 0) {
        int count = in->rectangle_count;
        if (count > AREA_MAX_ITEMS) {
            count = AREA_MAX_ITEMS;
        }

        for (int idx = 0; idx < count; idx++) {
            float sum_x = 0.0f, sum_y = 0.0f, sum_z = 0.0f;
            for (int k = 0; k < 4; k++) {
                sum_x += in->rectangles[idx][k][0];
                sum_y += in->rectangles[idx][k][1];
                sum_z += in->rectangles[idx][k][2];
            }
            out->centroids[idx][0] = sum_x / 4.0f;
            out->centroids[idx][1] = sum_y / 4.0f;
            out->centroids[idx][2] = sum_z / 4.0f;
        }
        out->centroid_count = count;

        // Backward-compatible single centroid = first item
        out->centroid[0] = out->centroids[0][0];
        out->centroid[1] = out->centroids[0][1];
        out->centroid[2] = out->centroids[0][2];
        return;
    }

    // Single-geometry mode (existing behavior)
    out->centroid_count = 0;

    if (in->geometry_type == 0) {
        // Line segment - midpoint
        out->centroid[0] = (in->line_start[0] + in->line_end[0]) / 2.0f;
        out->centroid[1] = (in->line_start[1] + in->line_end[1]) / 2.0f;
        out->centroid[2] = (in->line_start[2] + in->line_end[2]) / 2.0f;
        out->centroid_count = 1;
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
        out->centroid_count = 1;
    } else if (in->geometry_type == 2) {
        // Rectangle - centroid is average of corners
        out->centroid[0] = (in->rectangle_corners[0][0] + in->rectangle_corners[1][0] +
                           in->rectangle_corners[2][0] + in->rectangle_corners[3][0]) / 4.0f;
        out->centroid[1] = (in->rectangle_corners[0][1] + in->rectangle_corners[1][1] +
                           in->rectangle_corners[2][1] + in->rectangle_corners[3][1]) / 4.0f;
        out->centroid[2] = (in->rectangle_corners[0][2] + in->rectangle_corners[1][2] +
                           in->rectangle_corners[2][2] + in->rectangle_corners[3][2]) / 4.0f;
        out->centroid_count = 1;
    } else if (in->geometry_type == 3) {
        // Box - centroid is midpoint of diagonal
        out->centroid[0] = (in->box_corner_a[0] + in->box_corner_b[0]) / 2.0f;
        out->centroid[1] = (in->box_corner_a[1] + in->box_corner_b[1]) / 2.0f;
        out->centroid[2] = (in->box_corner_a[2] + in->box_corner_b[2]) / 2.0f;
        out->centroid_count = 1;
    } else {
        // Fallback
        out->centroid[0] = 0.0f;
        out->centroid[1] = 0.0f;
        out->centroid[2] = 0.0f;
        out->centroid_count = 0;
    }
}
