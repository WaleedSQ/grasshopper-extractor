#ifndef POLYLINE_H
#define POLYLINE_H

// Derived from evaluate_polyline in gh_components_stripped.py

#define POLYLINE_MAX_VERTICES 1000

typedef struct {
    float vertices[POLYLINE_MAX_VERTICES][3];
    int vertex_count;
    bool closed;
} PolyLineInput;

typedef struct {
    float vertices[POLYLINE_MAX_VERTICES][3];
    int vertex_count;
    bool closed;
} PolyLineOutput;

void PolyLine_eval(const PolyLineInput *in, PolyLineOutput *out);

#endif // POLYLINE_H

