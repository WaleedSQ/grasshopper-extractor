#ifndef AREA_H
#define AREA_H

// Derived from evaluate_area in gh_components_stripped.py

#define AREA_MAX_CORNERS 100

typedef struct {
    int geometry_type;  // 0=line, 1=polyline, 2=rectangle, 3=box
    float line_start[3];
    float line_end[3];
    float polyline_vertices[AREA_MAX_CORNERS][3];
    int polyline_count;
    float rectangle_corners[4][3];
    float box_corner_a[3];
    float box_corner_b[3];
} AreaInput;

typedef struct {
    float centroid[3];
} AreaOutput;

void Area_eval(const AreaInput *in, AreaOutput *out);

#endif // AREA_H

