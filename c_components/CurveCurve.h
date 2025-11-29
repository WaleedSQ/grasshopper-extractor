#ifndef CURVECURVE_H
#define CURVECURVE_H

// Derived from evaluate_curve_curve in gh_components_stripped.py

#define CURVECURVE_MAX_POINTS 100
#define CURVECURVE_MAX_ITEMS 100

typedef struct {
    int curve_a_type;  // 0=line, 1=circle
    int curve_b_type;  // 0=line, 1=circle

    // Single curve mode (backward compatible)
    float line_a_start[3];
    float line_a_end[3];
    float circle_a_center[3];
    float circle_a_radius;
    float circle_a_x_axis[3];
    float circle_a_y_axis[3];
    float circle_a_z_axis[3];
    float line_b_start[3];
    float line_b_end[3];
    float circle_b_center[3];
    float circle_b_radius;
    float circle_b_x_axis[3];
    float circle_b_y_axis[3];
    float circle_b_z_axis[3];

    // List mode: multiple circle-line intersections
    float circle_a_centers[CURVECURVE_MAX_ITEMS][3];
    float circle_a_radii[CURVECURVE_MAX_ITEMS];
    float circle_a_x_axes[CURVECURVE_MAX_ITEMS][3];
    float circle_a_y_axes[CURVECURVE_MAX_ITEMS][3];
    float circle_a_z_axes[CURVECURVE_MAX_ITEMS][3];
    float line_b_starts[CURVECURVE_MAX_ITEMS][3];
    float line_b_ends[CURVECURVE_MAX_ITEMS][3];
    int intersection_count;  // 0 => use single curves above
} CurveCurveInput;

typedef struct {
    // Single intersection output (backward compatible)
    float points[CURVECURVE_MAX_POINTS][3];
    int point_count;

    // List mode outputs: one point per intersection
    float points_list[CURVECURVE_MAX_ITEMS][3];
    int intersection_count;
} CurveCurveOutput;

void CurveCurve_eval(const CurveCurveInput *in, CurveCurveOutput *out);

#endif // CURVECURVE_H

