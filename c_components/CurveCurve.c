// Derived from evaluate_curve_curve in gh_components_stripped.py

#include "CurveCurve.h"
#include <math.h>
#include <stdbool.h>
#include <string.h>

#define PI 3.14159265358979323846f
#define TOL 1e-6f

static void line_line_intersection(const float p1[3], const float p2[3],
                                   const float p3[3], const float p4[3],
                                   float out[3], bool *found) {
    float d1[3] = {p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]};
    float d2[3] = {p4[0] - p3[0], p4[1] - p3[1], p4[2] - p3[2]};
    
    // Check if lines are parallel
    float cross[3] = {
        d1[1] * d2[2] - d1[2] * d2[1],
        d1[2] * d2[0] - d1[0] * d2[2],
        d1[0] * d2[1] - d1[1] * d2[0]
    };
    float cross_len = sqrtf(cross[0]*cross[0] + cross[1]*cross[1] + cross[2]*cross[2]);
    
    if (cross_len < TOL) {
        *found = false;
        return;
    }
    
    // Use XY plane projection
    float denom = d1[0] * d2[1] - d1[1] * d2[0];
    float t, s;
    
    if (fabsf(denom) < TOL) {
        // Try XZ plane
        denom = d1[0] * d2[2] - d1[2] * d2[0];
        if (fabsf(denom) < TOL) {
            // Try YZ plane
            denom = d1[1] * d2[2] - d1[2] * d2[1];
            if (fabsf(denom) < TOL) {
                *found = false;
                return;
            }
            // Use YZ
            t = ((p3[1] - p1[1]) * d2[2] - (p3[2] - p1[2]) * d2[1]) / denom;
            s = ((p3[1] - p1[1]) * d1[2] - (p3[2] - p1[2]) * d1[1]) / denom;
        } else {
            // Use XZ
            t = ((p3[0] - p1[0]) * d2[2] - (p3[2] - p1[2]) * d2[0]) / denom;
            s = ((p3[0] - p1[0]) * d1[2] - (p3[2] - p1[2]) * d1[0]) / denom;
        }
    } else {
        // Use XY
        t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / denom;
        s = ((p3[0] - p1[0]) * d1[1] - (p3[1] - p1[1]) * d1[0]) / denom;
    }
    
    // Check if intersection is within both segments
    if (t >= 0.0f && t <= 1.0f && s >= 0.0f && s <= 1.0f) {
        out[0] = p1[0] + t * d1[0];
        out[1] = p1[1] + t * d1[1];
        out[2] = p1[2] + t * d1[2];
        *found = true;
    } else {
        *found = false;
    }
}

static void line_circle_intersection(const float line_start[3], const float line_end[3],
                                    const float circle_center[3], float circle_radius,
                                    const float circle_x_axis[3], const float circle_y_axis[3],
                                    const float circle_z_axis[3],
                                    float out[3], bool *found) {
    float direction[3] = {
        line_end[0] - line_start[0],
        line_end[1] - line_start[1],
        line_end[2] - line_start[2]
    };
    
    float v[3] = {
        line_start[0] - circle_center[0],
        line_start[1] - circle_center[1],
        line_start[2] - circle_center[2]
    };
    
    float dir_dot_normal = direction[0] * circle_z_axis[0] +
                           direction[1] * circle_z_axis[1] +
                           direction[2] * circle_z_axis[2];
    float v_dot_normal = v[0] * circle_z_axis[0] +
                         v[1] * circle_z_axis[1] +
                         v[2] * circle_z_axis[2];
    
    if (fabsf(dir_dot_normal) < TOL) {
        // Line is parallel to the plane
        if (fabsf(v_dot_normal) < TOL) {
            // Line lies in the circle's plane - 2D line-circle intersection
            float start_2d_x = v[0] * circle_x_axis[0] + v[1] * circle_x_axis[1] + v[2] * circle_x_axis[2];
            float start_2d_y = v[0] * circle_y_axis[0] + v[1] * circle_y_axis[1] + v[2] * circle_y_axis[2];
            
            float dir_2d_x = direction[0] * circle_x_axis[0] + direction[1] * circle_x_axis[1] + direction[2] * circle_x_axis[2];
            float dir_2d_y = direction[0] * circle_y_axis[0] + direction[1] * circle_y_axis[1] + direction[2] * circle_y_axis[2];
            
            float a = dir_2d_x*dir_2d_x + dir_2d_y*dir_2d_y;
            float b = 2.0f * (start_2d_x * dir_2d_x + start_2d_y * dir_2d_y);
            float c = start_2d_x*start_2d_x + start_2d_y*start_2d_y - circle_radius*circle_radius;
            
            if (a < TOL) {
                *found = false;
                return;
            }
            
            float discriminant = b*b - 4.0f*a*c;
            
            if (discriminant < -TOL) {
                *found = false;
                return;
            } else if (discriminant < TOL) {
                // One intersection (tangent)
                float t = -b / (2.0f*a);
                if (t >= 0.0f && t <= 1.0f) {
                    out[0] = line_start[0] + t * direction[0];
                    out[1] = line_start[1] + t * direction[1];
                    out[2] = line_start[2] + t * direction[2];
                    *found = true;
                } else {
                    *found = false;
                }
            } else {
                // Two intersections - keep only the EXIT point (larger t value)
                float sqrt_disc = sqrtf(discriminant);
                float t1 = (-b - sqrt_disc) / (2.0f*a);
                float t2 = (-b + sqrt_disc) / (2.0f*a);
                
                float t = -1.0f;
                if (t2 >= 0.0f && t2 <= 1.0f) {
                    t = t2;
                } else if (t1 >= 0.0f && t1 <= 1.0f) {
                    t = t1;
                }
                
                if (t >= 0.0f) {
                    out[0] = line_start[0] + t * direction[0];
                    out[1] = line_start[1] + t * direction[1];
                    out[2] = line_start[2] + t * direction[2];
                    *found = true;
                } else {
                    *found = false;
                }
            }
        } else {
            *found = false;
        }
    } else {
        // Line intersects the plane at one point
        // Project line onto circle's plane to solve 2D line-circle intersection
        // This handles the case where line starts at center or anywhere else
        
        // Project line start (relative to center) onto circle plane
        float start_2d_x = v[0] * circle_x_axis[0] + v[1] * circle_x_axis[1] + v[2] * circle_x_axis[2];
        float start_2d_y = v[0] * circle_y_axis[0] + v[1] * circle_y_axis[1] + v[2] * circle_y_axis[2];
        
        // Project line direction onto circle plane
        float dir_2d_x = direction[0] * circle_x_axis[0] + direction[1] * circle_x_axis[1] + direction[2] * circle_x_axis[2];
        float dir_2d_y = direction[0] * circle_y_axis[0] + direction[1] * circle_y_axis[1] + direction[2] * circle_y_axis[2];
        
        // 2D line-circle intersection: |P0 + t*d|² = r²
        // where P0 = (start_2d_x, start_2d_y), d = (dir_2d_x, dir_2d_y)
        // a*t² + b*t + c = 0
        float a = dir_2d_x*dir_2d_x + dir_2d_y*dir_2d_y;
        
        if (a < TOL) {
            // Line has zero length in plane
            *found = false;
            return;
        }
        
        float b = 2.0f * (start_2d_x * dir_2d_x + start_2d_y * dir_2d_y);
        float c = start_2d_x*start_2d_x + start_2d_y*start_2d_y - circle_radius*circle_radius;
        
        float discriminant = b*b - 4.0f*a*c;
        
        if (discriminant < -TOL) {
            // No intersection
            *found = false;
            return;
        } else if (discriminant < TOL) {
            // One intersection (tangent)
            float t = -b / (2.0f*a);
            if (t >= 0.0f && t <= 1.0f) {
                out[0] = line_start[0] + t * direction[0];
                out[1] = line_start[1] + t * direction[1];
                out[2] = line_start[2] + t * direction[2];
                *found = true;
            } else {
                *found = false;
            }
        } else {
            // Two intersections - keep only the EXIT point (larger t value)
            // This matches Grasshopper's CCX behavior for line-circle intersections
            float sqrt_disc = sqrtf(discriminant);
            float t1 = (-b - sqrt_disc) / (2.0f*a);  // entry point (smaller t)
            float t2 = (-b + sqrt_disc) / (2.0f*a);  // exit point (larger t)
            
            // Prefer exit point (t2), fall back to entry point (t1) if exit is out of bounds
            float t = -1.0f;
            if (t2 >= 0.0f && t2 <= 1.0f) {
                t = t2;
            } else if (t1 >= 0.0f && t1 <= 1.0f) {
                t = t1;
            }
            
            if (t >= 0.0f) {
                out[0] = line_start[0] + t * direction[0];
                out[1] = line_start[1] + t * direction[1];
                out[2] = line_start[2] + t * direction[2];
                *found = true;
            } else {
                *found = false;
            }
        }
    }
}

void CurveCurve_eval(const CurveCurveInput *in, CurveCurveOutput *out) {
    memset(out, 0, sizeof(CurveCurveOutput));

    // List mode: multiple circle-line intersections
    if (in->curve_a_type == 1 && in->curve_b_type == 0 && in->intersection_count > 0) {
        int count = in->intersection_count;
        if (count > CURVECURVE_MAX_ITEMS) count = CURVECURVE_MAX_ITEMS;

        for (int i = 0; i < count; ++i) {
            bool found;
            line_circle_intersection(in->line_b_starts[i], in->line_b_ends[i],
                                    in->circle_a_centers[i], in->circle_a_radii[i],
                                    in->circle_a_x_axes[i], in->circle_a_y_axes[i],
                                    in->circle_a_z_axes[i],
                                    out->points_list[i], &found);
            if (!found) {
                // No intersection - set to zero point
                out->points_list[i][0] = 0.0f;
                out->points_list[i][1] = 0.0f;
                out->points_list[i][2] = 0.0f;
            }
        }
        out->intersection_count = count;

        // Backward-compatible single output = first element
        if (count > 0) {
            out->points[0][0] = out->points_list[0][0];
            out->points[0][1] = out->points_list[0][1];
            out->points[0][2] = out->points_list[0][2];
            out->point_count = 1;
        }
        return;
    }

    // Single curve mode (backward compatible)
    out->point_count = 0;
    
    if (in->curve_a_type == 0 && in->curve_b_type == 0) {
        // Line-Line intersection
        bool found;
        line_line_intersection(in->line_a_start, in->line_a_end,
                              in->line_b_start, in->line_b_end,
                              out->points[0], &found);
        if (found) {
            out->point_count = 1;
        }
    } else if (in->curve_a_type == 0 && in->curve_b_type == 1) {
        // Line-Circle intersection
        bool found;
        line_circle_intersection(in->line_a_start, in->line_a_end,
                                in->circle_b_center, in->circle_b_radius,
                                in->circle_b_x_axis, in->circle_b_y_axis,
                                in->circle_b_z_axis,
                                out->points[0], &found);
        if (found) {
            out->point_count = 1;
        }
    } else if (in->curve_a_type == 1 && in->curve_b_type == 0) {
        // Circle-Line intersection (swap)
        bool found;
        line_circle_intersection(in->line_b_start, in->line_b_end,
                                in->circle_a_center, in->circle_a_radius,
                                in->circle_a_x_axis, in->circle_a_y_axis,
                                in->circle_a_z_axis,
                                out->points[0], &found);
        if (found) {
            out->point_count = 1;
        }
    }
    // Circle-Circle intersection not implemented (would need more complex math)
}

