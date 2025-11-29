#ifndef AREA_H
#define AREA_H

// Derived from evaluate_area in gh_components_stripped.py

#define AREA_MAX_CORNERS 100
#define AREA_MAX_ITEMS   100

// Input structure for Area component.
// Supports both single-geometry mode and list mode for rectangles.
typedef struct {
    // Single-geometry mode (backward compatible)
    // geometry_type indicates which of the following fields is valid
    // 0=line, 1=polyline, 2=rectangle, 3=box
    int geometry_type;
    float line_start[3];
    float line_end[3];
    float polyline_vertices[AREA_MAX_CORNERS][3];
    int polyline_count;
    float rectangle_corners[4][3];
    float box_corner_a[3];
    float box_corner_b[3];

    // List mode: multiple rectangles in a single call (matches GH DataTree behavior
    // for this graph, where we have one rectangle per slat).
    // When rectangle_count > 0, Area_eval ignores geometry_type and rectangle_corners
    // and instead processes rectangles[0..rectangle_count-1].
    float rectangles[AREA_MAX_ITEMS][4][3];
    int rectangle_count;  // 0 means use single rectangle_corners
} AreaInput;

// Output structure for Area component.
typedef struct {
    // First centroid (for backward compatibility with single-geometry mode)
    float centroid[3];

    // List mode: centroids for all input rectangles
    float centroids[AREA_MAX_ITEMS][3];
    int centroid_count;  // number of valid centroids in list mode
} AreaOutput;

void Area_eval(const AreaInput *in, AreaOutput *out);

#endif // AREA_H
