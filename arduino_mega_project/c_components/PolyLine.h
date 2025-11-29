#ifndef POLYLINE_H
#define POLYLINE_H

#include <stdbool.h>

// Derived from evaluate_polyline in gh_components_stripped.py

#define POLYLINE_MAX_VERTICES 1000
#define POLYLINE_MAX_ITEMS 100

typedef struct {
    // Single polyline mode (backward compatible)
    float vertices[POLYLINE_MAX_VERTICES][3];
    int vertex_count;
    bool closed;

    // List mode: multiple polylines (each with 2 vertices)
    float polyline_vertices[POLYLINE_MAX_ITEMS][2][3];  // [item][vertex_index][xyz]
    int polyline_count;  // 0 => use single vertices/vertex_count above
} PolyLineInput;

typedef struct {
    // Single polyline output (backward compatible)
    float vertices[POLYLINE_MAX_VERTICES][3];
    int vertex_count;
    bool closed;

    // List mode outputs
    float polyline_vertices[POLYLINE_MAX_ITEMS][2][3];
    int polyline_count;
} PolyLineOutput;

void PolyLine_eval(const PolyLineInput *in, PolyLineOutput *out);

#endif // POLYLINE_H

