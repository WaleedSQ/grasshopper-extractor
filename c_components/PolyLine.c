// Derived from evaluate_polyline in gh_components_stripped.py

#include "PolyLine.h"
#include <stdbool.h>
#include <string.h>

void PolyLine_eval(const PolyLineInput *in, PolyLineOutput *out) {
    memset(out, 0, sizeof(PolyLineOutput));

    // List mode: multiple 2-vertex polylines
    if (in->polyline_count > 0) {
        int count = in->polyline_count;
        if (count > POLYLINE_MAX_ITEMS) count = POLYLINE_MAX_ITEMS;

        for (int i = 0; i < count; ++i) {
            for (int k = 0; k < 2; k++) {
                out->polyline_vertices[i][k][0] = in->polyline_vertices[i][k][0];
                out->polyline_vertices[i][k][1] = in->polyline_vertices[i][k][1];
                out->polyline_vertices[i][k][2] = in->polyline_vertices[i][k][2];
            }
        }
        out->polyline_count = count;
        out->closed = in->closed;

        // Backward-compatible single polyline = first element
        out->vertex_count = 2;
        out->vertices[0][0] = out->polyline_vertices[0][0][0];
        out->vertices[0][1] = out->polyline_vertices[0][0][1];
        out->vertices[0][2] = out->polyline_vertices[0][0][2];
        out->vertices[1][0] = out->polyline_vertices[0][1][0];
        out->vertices[1][1] = out->polyline_vertices[0][1][1];
        out->vertices[1][2] = out->polyline_vertices[0][1][2];
        return;
    }

    // Single polyline mode (backward compatible)
    out->vertex_count = in->vertex_count;
    out->closed = in->closed;
    
    for (int i = 0; i < in->vertex_count && i < POLYLINE_MAX_VERTICES; i++) {
        out->vertices[i][0] = in->vertices[i][0];
        out->vertices[i][1] = in->vertices[i][1];
        out->vertices[i][2] = in->vertices[i][2];
    }
}

