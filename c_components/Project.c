// Derived from evaluate_project in gh_components_stripped.py

#include "Project.h"
#include <math.h>
#include <string.h>

static void normalize_vec(const float vec[3], float out[3]) {
    float length = sqrtf(vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2]);
    if (length > 0.0f) {
        out[0] = vec[0] / length;
        out[1] = vec[1] / length;
        out[2] = vec[2] / length;
    } else {
        out[0] = vec[0];
        out[1] = vec[1];
        out[2] = vec[2];
    }
}

static float vec_length(const float vec[3]) {
    return sqrtf(vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2]);
}

static void extract_plane_from_brep(const ProjectInput *in, float plane_origin[3], float plane_normal[3]) {
    if (in->brep_type == 0) {
        // Plane
        plane_origin[0] = in->plane_origin[0];
        plane_origin[1] = in->plane_origin[1];
        plane_origin[2] = in->plane_origin[2];
        normalize_vec(in->plane_z_axis, plane_normal);
    } else {
        // Box - determine which plane the box lies in
        float ca[3] = {in->box_corner_a[0], in->box_corner_a[1], in->box_corner_a[2]};
        float cb[3] = {in->box_corner_b[0], in->box_corner_b[1], in->box_corner_b[2]};
        float tol = 1e-6f;

        if (fabsf(ca[0] - cb[0]) < tol) {
            // YZ plane (x is constant)
            plane_origin[0] = ca[0];
            plane_origin[1] = (ca[1] + cb[1]) / 2.0f;
            plane_origin[2] = (ca[2] + cb[2]) / 2.0f;
            plane_normal[0] = 1.0f;
            plane_normal[1] = 0.0f;
            plane_normal[2] = 0.0f;
        } else if (fabsf(ca[1] - cb[1]) < tol) {
            // XZ plane (y is constant)
            plane_origin[0] = (ca[0] + cb[0]) / 2.0f;
            plane_origin[1] = ca[1];
            plane_origin[2] = (ca[2] + cb[2]) / 2.0f;
            plane_normal[0] = 0.0f;
            plane_normal[1] = 1.0f;
            plane_normal[2] = 0.0f;
        } else if (fabsf(ca[2] - cb[2]) < tol) {
            // XY plane (z is constant)
            plane_origin[0] = (ca[0] + cb[0]) / 2.0f;
            plane_origin[1] = (ca[1] + cb[1]) / 2.0f;
            plane_origin[2] = ca[2];
            plane_normal[0] = 0.0f;
            plane_normal[1] = 0.0f;
            plane_normal[2] = 1.0f;
        } else {
            // Non-planar box - use XY plane through center
            plane_origin[0] = (ca[0] + cb[0]) / 2.0f;
            plane_origin[1] = (ca[1] + cb[1]) / 2.0f;
            plane_origin[2] = (ca[2] + cb[2]) / 2.0f;
            plane_normal[0] = 0.0f;
            plane_normal[1] = 0.0f;
            plane_normal[2] = 1.0f;
        }
    }
}

static void project_line_to_surface(const float start[3], const float end[3],
                                    const float plane_origin[3], const float plane_normal[3],
                                    float out_start[3], float out_end[3]) {
    // Line direction vector
    float line_dir[3] = {
        end[0] - start[0],
        end[1] - start[1],
        end[2] - start[2]
    };
    float line_len = vec_length(line_dir);

    if (line_len < 1e-10f) {
        // Degenerate line - project start point
        float dist = ((start[0] - plane_origin[0]) * plane_normal[0] +
                     (start[1] - plane_origin[1]) * plane_normal[1] +
                     (start[2] - plane_origin[2]) * plane_normal[2]);
        out_start[0] = start[0] - dist * plane_normal[0];
        out_start[1] = start[1] - dist * plane_normal[1];
        out_start[2] = start[2] - dist * plane_normal[2];
        out_end[0] = out_start[0];
        out_end[1] = out_start[1];
        out_end[2] = out_start[2];
        return;
    }

    // Normalize line direction
    float line_dir_norm[3];
    normalize_vec(line_dir, line_dir_norm);

    // Compute t where line intersects plane
    float denom = line_dir[0]*plane_normal[0] + line_dir[1]*plane_normal[1] + line_dir[2]*plane_normal[2];

    if (fabsf(denom) < 1e-10f) {
        // Line is parallel to plane - project the start point
        float dist = ((start[0] - plane_origin[0]) * plane_normal[0] +
                     (start[1] - plane_origin[1]) * plane_normal[1] +
                     (start[2] - plane_origin[2]) * plane_normal[2]);
        out_start[0] = start[0] - dist * plane_normal[0];
        out_start[1] = start[1] - dist * plane_normal[1];
        out_start[2] = start[2] - dist * plane_normal[2];

        // Project line direction onto plane
        float dot_n = line_dir_norm[0]*plane_normal[0] + line_dir_norm[1]*plane_normal[1] + line_dir_norm[2]*plane_normal[2];
        float proj_dir[3] = {
            line_dir_norm[0] - dot_n * plane_normal[0],
            line_dir_norm[1] - dot_n * plane_normal[1],
            line_dir_norm[2] - dot_n * plane_normal[2]
        };
        float proj_dir_len = vec_length(proj_dir);
        if (proj_dir_len > 1e-10f) {
            normalize_vec(proj_dir, proj_dir);
            float segment_len = (line_len * 0.00003f < 3.0f) ? line_len * 0.00003f : 3.0f;
            out_end[0] = out_start[0] + segment_len * proj_dir[0];
            out_end[1] = out_start[1] + segment_len * proj_dir[1];
            out_end[2] = out_start[2] + segment_len * proj_dir[2];
        } else {
            out_end[0] = out_start[0];
            out_end[1] = out_start[1];
            out_end[2] = out_start[2];
        }
        return;
    }

    // Compute intersection parameter
    float t = ((plane_origin[0]-start[0])*plane_normal[0] +
               (plane_origin[1]-start[1])*plane_normal[1] +
               (plane_origin[2]-start[2])*plane_normal[2]) / denom;

    // Intersection point
    float intersection[3] = {
        start[0] + t * line_dir[0],
        start[1] + t * line_dir[1],
        start[2] + t * line_dir[2]
    };

    // Create a short segment around the intersection point
    float dot_n = line_dir_norm[0]*plane_normal[0] + line_dir_norm[1]*plane_normal[1] + line_dir_norm[2]*plane_normal[2];
    float proj_dir[3] = {
        line_dir_norm[0] - dot_n * plane_normal[0],
        line_dir_norm[1] - dot_n * plane_normal[1],
        line_dir_norm[2] - dot_n * plane_normal[2]
    };
    float proj_dir_len = vec_length(proj_dir);

    if (proj_dir_len > 1e-10f) {
        normalize_vec(proj_dir, proj_dir);
        float segment_len = (line_len * 0.00005f < 5.0f) ? line_len * 0.00005f : 5.0f;
        float half_len = segment_len / 2.0f;

        out_start[0] = intersection[0] - half_len * proj_dir[0];
        out_start[1] = intersection[1] - half_len * proj_dir[1];
        out_start[2] = intersection[2] - half_len * proj_dir[2];

        out_end[0] = intersection[0] + half_len * proj_dir[0];
        out_end[1] = intersection[1] + half_len * proj_dir[1];
        out_end[2] = intersection[2] + half_len * proj_dir[2];
    } else {
        out_start[0] = intersection[0];
        out_start[1] = intersection[1];
        out_start[2] = intersection[2];
        out_end[0] = intersection[0];
        out_end[1] = intersection[1];
        out_end[2] = intersection[2];
    }
}

void Project_eval(const ProjectInput *in, ProjectOutput *out) {
    memset(out, 0, sizeof(ProjectOutput));

    // GH Project: project curve onto brep/surface
    out->curve_type = in->curve_type;

    float plane_origin[3], plane_normal[3];
    extract_plane_from_brep(in, plane_origin, plane_normal);

    // List mode: multiple lines projected onto common plane/brep
    if (in->curve_type == 1 && in->line_count > 0) {
        int count = in->line_count;
        if (count > PROJECT_MAX_ITEMS) count = PROJECT_MAX_ITEMS;

        for (int i = 0; i < count; ++i) {
            project_line_to_surface(in->line_starts[i], in->line_ends[i],
                                    plane_origin, plane_normal,
                                    out->line_starts[i], out->line_ends[i]);
        }
        out->line_count = count;

        // Backward-compatible single output from first item
        out->line_start[0] = out->line_starts[0][0];
        out->line_start[1] = out->line_starts[0][1];
        out->line_start[2] = out->line_starts[0][2];

        out->line_end[0] = out->line_ends[0][0];
        out->line_end[1] = out->line_ends[0][1];
        out->line_end[2] = out->line_ends[0][2];
        return;
    }

    // Single-geometry modes (unchanged)
    if (in->curve_type == 0) {
        // Point - find intersection with plane along direction
        float dir_norm[3];
        normalize_vec(in->direction, dir_norm);

        float dn = dir_norm[0]*plane_normal[0] + dir_norm[1]*plane_normal[1] + dir_norm[2]*plane_normal[2];
        if (fabsf(dn) < 1e-10f) {
            // Parallel - project orthogonally
            float dist = ((in->point[0] - plane_origin[0]) * plane_normal[0] +
                         (in->point[1] - plane_origin[1]) * plane_normal[1] +
                         (in->point[2] - plane_origin[2]) * plane_normal[2]);
            out->point[0] = in->point[0] - dist * plane_normal[0];
            out->point[1] = in->point[1] - dist * plane_normal[1];
            out->point[2] = in->point[2] - dist * plane_normal[2];
        } else {
            float t = ((plane_origin[0]-in->point[0]) * plane_normal[0] +
                      (plane_origin[1]-in->point[1]) * plane_normal[1] +
                      (plane_origin[2]-in->point[2]) * plane_normal[2]) / dn;
            out->point[0] = in->point[0] + t * dir_norm[0];
            out->point[1] = in->point[1] + t * dir_norm[1];
            out->point[2] = in->point[2] + t * dir_norm[2];
        }
    } else if (in->curve_type == 1) {
        // Single line - project onto surface
        project_line_to_surface(in->line_start, in->line_end, plane_origin, plane_normal,
                                out->line_start, out->line_end);
    }
}


