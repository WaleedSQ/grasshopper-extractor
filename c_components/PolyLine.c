// Derived from evaluate_polyline in gh_components_stripped.py

#include "PolyLine.h"
#include <stdbool.h>

void PolyLine_eval(const PolyLineInput *in, PolyLineOutput *out) {
    // GH PolyLine: create polyline from vertices
    // Copy vertices and closed flag
    out->vertex_count = in->vertex_count;
    out->closed = in->closed;
    
    for (int i = 0; i < in->vertex_count && i < POLYLINE_MAX_VERTICES; i++) {
        out->vertices[i][0] = in->vertices[i][0];
        out->vertices[i][1] = in->vertices[i][1];
        out->vertices[i][2] = in->vertices[i][2];
    }
}

