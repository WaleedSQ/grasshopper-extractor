#include "core_group.h"
#include "../c_components/Move.h"
#include "../c_components/Line.h"
#include "../c_components/Project.h"
#include "../c_components/PolyLine.h"
#include "../c_components/PlaneNormal.h"
#include "../c_components/ConstructPlane.h"
#include "../c_components/ListItem.h"
#include "../c_components/Circle.h"
#include "../c_components/CurveCurve.h"
#include "../c_components/Angle.h"
#include "../c_components/Degrees.h"
#include "../c_components/YZPlane.h"
#include "../c_components/Rotate.h"
#include "../c_components/Area.h"
#include <string.h>
#include <math.h>
#include <stdio.h>

void core_group_eval(
    const ShadeConfig *cfg,
    const SunGroupOutput *sun,
    const SlatsGroupOutput *slats,
    const DirectionGroupOutput *dir,
    const TargetsGroupOutput *targets,
    CoreGroupOutput *out
) {
    int max_slats = cfg->number_of_slats;
    if (max_slats > MAX_ANGLES) {
        max_slats = MAX_ANGLES;
    }
    out->angle_count = cfg->number_of_slats;

    if (max_slats <= 0) {
        return;
    }

    // ---------------------------------------------------------------------
    // 0. Area from slatsGroup rotated rectangles (slatsGroup Rotate output)
    //    Use list-mode Area to compute centroids for all slats at once.
    // ---------------------------------------------------------------------

    AreaInput area_in;
    memset(&area_in, 0, sizeof(AreaInput));
    area_in.geometry_type = 2; // rectangle (for single mode fallback)

    int rect_count = slats->slat_count;
    if (rect_count > max_slats) {
        rect_count = max_slats;
    }
    if (rect_count <= 0) {
        // Fallback: nothing to do, leave angles at 0
        for (int i = 0; i < max_slats; ++i) {
            out->slat_angles[i] = 0.0f;
        }
        return;
    }

    area_in.rectangle_count = rect_count;
    for (int i = 0; i < rect_count; ++i) {
        memcpy(area_in.rectangles[i], slats->slat_rectangles[i], sizeof(float) * 4 * 3);
    }

    AreaOutput area_out;
    Area_eval(&area_in, &area_out);

    // Copy centroids into a local array for convenience
    float slat_centroids[MAX_ANGLES][3];
    int centroid_count = area_out.centroid_count;
    if (centroid_count > rect_count) {
        centroid_count = rect_count;
    }
    if (centroid_count > max_slats) {
        centroid_count = max_slats;
    }
    for (int i = 0; i < centroid_count; ++i) {
        slat_centroids[i][0] = area_out.centroids[i][0];
        slat_centroids[i][1] = area_out.centroids[i][1];
        slat_centroids[i][2] = area_out.centroids[i][2];
    }

    // Debug for first slat
    printf("  [DEBUG Slat 0] Area (slats): rect_idx=0, centroid_count=%d, first=(%.6f, %.6f, %.6f)\n",
           area_out.centroid_count,
           area_out.centroids[0][0], area_out.centroids[0][1], area_out.centroids[0][2]);
    if (area_out.centroid_count > 1) {
        printf("    [DEBUG Slat 0] Area list: second=(%.6f, %.6f, %.6f)\n",
               area_out.centroids[1][0], area_out.centroids[1][1], area_out.centroids[1][2]);
    }
    if (area_out.centroid_count > 2) {
        int last_idx = area_out.centroid_count - 1;
        printf("    [DEBUG Slat 0] Area list: last=(%.6f, %.6f, %.6f)\n",
               area_out.centroids[last_idx][0], area_out.centroids[last_idx][1], area_out.centroids[last_idx][2]);
    }

    // Number of slats we will actually process through the pipeline
    int n = centroid_count;

    // ---------------------------------------------------------------------
    // 1. Move sun point (New Sun) - list mode over all centroids
    // ---------------------------------------------------------------------

    MoveInput move_sun_in;
    memset(&move_sun_in, 0, sizeof(MoveInput));
    move_sun_in.geometry_type = 0; // point
    memcpy(move_sun_in.motion, sun->sun_vector, sizeof(float) * 3);
    move_sun_in.point_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(move_sun_in.points[i], slat_centroids[i], sizeof(float) * 3);
    }

    MoveOutput move_sun_out;
    Move_eval(&move_sun_in, &move_sun_out);

    printf("  [DEBUG Slat 0] Move (sun): point=(%.6f, %.6f, %.6f), motion=(%.6f, %.6f, %.6f) -> (%.6f, %.6f, %.6f)\n",
           move_sun_in.points[0][0], move_sun_in.points[0][1], move_sun_in.points[0][2],
           move_sun_in.motion[0], move_sun_in.motion[1], move_sun_in.motion[2],
           move_sun_out.points[0][0], move_sun_out.points[0][1], move_sun_out.points[0][2]);

    // ---------------------------------------------------------------------
    // 2. Line from sun to moved sun (Out Ray) - list mode
    // ---------------------------------------------------------------------

    LineInput line_out_in;
    memset(&line_out_in, 0, sizeof(LineInput));
    line_out_in.use_two_points = 1;
    line_out_in.line_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(line_out_in.start_points[i], slat_centroids[i], sizeof(float) * 3);
        memcpy(line_out_in.end_points[i],   move_sun_out.points[i], sizeof(float) * 3);
    }

    LineOutput line_out_out;
    Line_eval(&line_out_in, &line_out_out);

    printf("  [DEBUG Slat 0] Line (out ray): start=(%.6f, %.6f, %.6f), end=(%.6f, %.6f, %.6f)\n",
           line_out_out.starts[0][0], line_out_out.starts[0][1], line_out_out.starts[0][2],
           line_out_out.ends[0][0],   line_out_out.ends[0][1],   line_out_out.ends[0][2]);

    // ---------------------------------------------------------------------
    // 3. Rotate target points (list mode), then Line from centroid to
    //    rotated target (In Ray) - Line in list mode.
    // ---------------------------------------------------------------------

    float orientation_rad = cfg->orientation_deg * M_PI / 180.0f;

    // Build list of target points for Rotate
    RotateInput rot_tgt_in;
    memset(&rot_tgt_in, 0, sizeof(RotateInput));
    rot_tgt_in.geometry_type = 0;  // point
    rot_tgt_in.angle = orientation_rad;
    rot_tgt_in.rot_origin[0] = 0.0f;
    rot_tgt_in.rot_origin[1] = 0.0f;
    rot_tgt_in.rot_origin[2] = 0.0f;
    rot_tgt_in.rot_axis[0] = 0.0f;
    rot_tgt_in.rot_axis[1] = 0.0f;
    rot_tgt_in.rot_axis[2] = 1.0f;
    rot_tgt_in.point_count = n;
    for (int i = 0; i < n; ++i) {
        if (i < targets->target_count) {
            memcpy(rot_tgt_in.points[i], targets->target_points[i], sizeof(float) * 3);
        } else {
            memcpy(rot_tgt_in.points[i], targets->target_points[0], sizeof(float) * 3);
        }
    }

    RotateOutput rot_tgt_out;
    Rotate_eval(&rot_tgt_in, &rot_tgt_out);

    // Copy rotated points to local array
    float rotated_targets[MAX_ANGLES][3];
    for (int i = 0; i < n && i < rot_tgt_out.point_count; ++i) {
        memcpy(rotated_targets[i], rot_tgt_out.points[i], sizeof(float) * 3);
    }

    // Debug output
    printf("  [DEBUG Slat 0] Rotate (target): raw=(%.6f, %.6f, %.6f) -> rotated=(%.6f, %.6f, %.6f)\n",
           rot_tgt_in.points[0][0], rot_tgt_in.points[0][1], rot_tgt_in.points[0][2],
           rot_tgt_out.points[0][0], rot_tgt_out.points[0][1], rot_tgt_out.points[0][2]);
    if (n > 9 && rot_tgt_out.point_count > 9) {
        printf("  [DEBUG Slat 9] Rotate (target): raw=(%.6f, %.6f, %.6f) -> rotated=(%.6f, %.6f, %.6f)\n",
               rot_tgt_in.points[9][0], rot_tgt_in.points[9][1], rot_tgt_in.points[9][2],
               rot_tgt_out.points[9][0], rot_tgt_out.points[9][1], rot_tgt_out.points[9][2]);
    }

    LineInput line_in_in;
    memset(&line_in_in, 0, sizeof(LineInput));
    line_in_in.use_two_points = 1;
    line_in_in.line_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(line_in_in.start_points[i], slat_centroids[i],     sizeof(float) * 3);
        memcpy(line_in_in.end_points[i],   rotated_targets[i],     sizeof(float) * 3);
    }

    LineOutput line_in_out;
    Line_eval(&line_in_in, &line_in_out);

    printf("  [DEBUG Slat 0] Line (in ray): start=(%.6f, %.6f, %.6f), end=(%.6f, %.6f, %.6f)\n",
           line_in_out.starts[0][0], line_in_out.starts[0][1], line_in_out.starts[0][2],
           line_in_out.ends[0][0],   line_in_out.ends[0][1],   line_in_out.ends[0][2]);

    // ---------------------------------------------------------------------
    // 4. Project out-ray curve onto box (Project Curve) - list mode
    // ---------------------------------------------------------------------

    ProjectInput proj_in;
    memset(&proj_in, 0, sizeof(ProjectInput));
    proj_in.curve_type = 1;  // line
    proj_in.brep_type = 1;   // box (we use direction group's plane as box)
    memcpy(proj_in.plane_origin, dir->plane_origin, sizeof(float) * 3);
    memcpy(proj_in.plane_z_axis, dir->plane_z_axis, sizeof(float) * 3);

    proj_in.line_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(proj_in.line_starts[i], line_out_out.starts[i], sizeof(float) * 3);
        memcpy(proj_in.line_ends[i],   line_out_out.ends[i],   sizeof(float) * 3);
    }

    ProjectOutput proj_out;
    Project_eval(&proj_in, &proj_out);

    printf("  [DEBUG Slat 0] Project: line_start=(%.6f, %.6f, %.6f), plane_origin=(%.6f, %.6f, %.6f) -> line_start=(%.6f, %.6f, %.6f)\n",
           proj_in.line_starts[0][0], proj_in.line_starts[0][1], proj_in.line_starts[0][2],
           proj_in.plane_origin[0],   proj_in.plane_origin[1],   proj_in.plane_origin[2],
           proj_out.line_starts[0][0], proj_out.line_starts[0][1], proj_out.line_starts[0][2]);

    // ---------------------------------------------------------------------
    // 5-10. Vectorized stages: PolyLine, PlaneNormal, ConstructPlane,
    //       YZPlane, Circle, CurveCurve (list mode)
    // ---------------------------------------------------------------------

    printf("  [DEBUG Slat 0] Starting angle calculation...\n");

    // 5. PolyLine from projected points (list mode: forward)
    PolyLineInput poly_in;
    memset(&poly_in, 0, sizeof(PolyLineInput));
    poly_in.closed = 0;
    poly_in.polyline_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(poly_in.polyline_vertices[i][0], proj_out.line_starts[i], sizeof(float) * 3);
        memcpy(poly_in.polyline_vertices[i][1], proj_out.line_ends[i],   sizeof(float) * 3);
    }
    PolyLineOutput poly_out;
    PolyLine_eval(&poly_in, &poly_out);
    printf("  [DEBUG Slat 0] PolyLine: vertex[0]=(%.6f, %.6f, %.6f), vertex[1]=(%.6f, %.6f, %.6f)\n",
           poly_out.polyline_vertices[0][0][0], poly_out.polyline_vertices[0][0][1], poly_out.polyline_vertices[0][0][2],
           poly_out.polyline_vertices[0][1][0], poly_out.polyline_vertices[0][1][1], poly_out.polyline_vertices[0][1][2]);

    // 6. Plane Normal from polyline (list mode)
    PlaneNormalInput pn_in;
    memset(&pn_in, 0, sizeof(PlaneNormalInput));
    pn_in.plane_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(pn_in.origins[i], slat_centroids[i], sizeof(float) * 3);
        memcpy(pn_in.z_axes[i], poly_out.polyline_vertices[i][0], sizeof(float) * 3);
    }
    PlaneNormalOutput pn_out;
    PlaneNormal_eval(&pn_in, &pn_out);
    printf("  [DEBUG Slat 0] PlaneNormal (pn): origin=(%.6f, %.6f, %.6f), z_axis=(%.6f, %.6f, %.6f) -> x_axis=(%.6f, %.6f, %.6f)\n",
           pn_in.origins[0][0], pn_in.origins[0][1], pn_in.origins[0][2],
           pn_in.z_axes[0][0], pn_in.z_axes[0][1], pn_in.z_axes[0][2],
           pn_out.x_axes[0][0], pn_out.x_axes[0][1], pn_out.x_axes[0][2]);

    // 7. PolyLine reversed (list mode)
    PolyLineInput poly_rev_in;
    memset(&poly_rev_in, 0, sizeof(PolyLineInput));
    poly_rev_in.closed = 0;
    poly_rev_in.polyline_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(poly_rev_in.polyline_vertices[i][0], proj_out.line_ends[i],   sizeof(float) * 3);
        memcpy(poly_rev_in.polyline_vertices[i][1], proj_out.line_starts[i], sizeof(float) * 3);
    }
    PolyLineOutput poly_rev_out;
    PolyLine_eval(&poly_rev_in, &poly_rev_out);

    // 7. Construct Plane (list mode)
    ConstructPlaneInput cp_in;
    memset(&cp_in, 0, sizeof(ConstructPlaneInput));
    cp_in.plane_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(cp_in.origins[i], slat_centroids[i], sizeof(float) * 3);
        memcpy(cp_in.x_axes[i], poly_out.polyline_vertices[i][0], sizeof(float) * 3);
        memcpy(cp_in.y_axes[i], poly_rev_out.polyline_vertices[i][0], sizeof(float) * 3);
    }
    ConstructPlaneOutput cp_out;
    ConstructPlane_eval(&cp_in, &cp_out);
    printf("  [DEBUG Slat 0] ConstructPlane: x_axis=(%.6f, %.6f, %.6f), y_axis=(%.6f, %.6f, %.6f) -> z_axis=(%.6f, %.6f, %.6f)\n",
           cp_in.x_axes[0][0], cp_in.x_axes[0][1], cp_in.x_axes[0][2],
           cp_in.y_axes[0][0], cp_in.y_axes[0][1], cp_in.y_axes[0][2],
           cp_out.z_axes[0][0], cp_out.z_axes[0][1], cp_out.z_axes[0][2]);

    // 8. List Item to get plane normal toggle (per-slat, but prepare for pn2)
    float pn2_origins[MAX_ANGLES][3];
    for (int i = 0; i < n; ++i) {
        ListItemInput li_in = {
            .list_size = 3,
            .index = 0,
            .wrap = 1
        };
        li_in.list[0] = slat_centroids[i][0];
        li_in.list[1] = slat_centroids[i][1];
        li_in.list[2] = slat_centroids[i][2];
        ListItemOutput li_out;
        ListItem_eval(&li_in, &li_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] ListItem: list[0]=%.6f, list[1]=%.6f, list[2]=%.6f, index=%d -> item=%.6f, valid=%d\n",
                   li_in.list[0], li_in.list[1], li_in.list[2], li_in.index, li_out.item, li_out.valid);
        }
        if (li_out.item != 0.0f) {
            memcpy(pn2_origins[i], slat_centroids[i], sizeof(float) * 3);
        } else {
            int tgt_idx = (i < targets->target_count) ? i : 0;
            memcpy(pn2_origins[i], targets->target_points[tgt_idx], sizeof(float) * 3);
        }
    }

    // 9. Plane Normal for angle calculation (list mode)
    PlaneNormalInput pn2_in;
    memset(&pn2_in, 0, sizeof(PlaneNormalInput));
    pn2_in.plane_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(pn2_in.origins[i], pn2_origins[i], sizeof(float) * 3);
        memcpy(pn2_in.z_axes[i], cp_out.z_axes[i], sizeof(float) * 3);
    }
    PlaneNormalOutput pn2_out;
    PlaneNormal_eval(&pn2_in, &pn2_out);
    printf("  [DEBUG Slat 0] PlaneNormal (pn2): origin=(%.6f, %.6f, %.6f), z_axis=(%.6f, %.6f, %.6f) -> x_axis=(%.6f, %.6f, %.6f)\n",
           pn2_in.origins[0][0], pn2_in.origins[0][1], pn2_in.origins[0][2],
           pn2_in.z_axes[0][0], pn2_in.z_axes[0][1], pn2_in.z_axes[0][2],
           pn2_out.x_axes[0][0], pn2_out.x_axes[0][1], pn2_out.x_axes[0][2]);

    // 10. YZ Plane (list mode)
    YZPlaneInput yz_in;
    memset(&yz_in, 0, sizeof(YZPlaneInput));
    yz_in.plane_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(yz_in.origins[i], slat_centroids[i], sizeof(float) * 3);
    }
    YZPlaneOutput yz_out;
    YZPlane_eval(&yz_in, &yz_out);
    printf("  [DEBUG Slat 0] YZPlane: origin=(%.6f, %.6f, %.6f) -> z_axis=(%.6f, %.6f, %.6f)\n",
           yz_in.origins[0][0], yz_in.origins[0][1], yz_in.origins[0][2],
           yz_out.z_axes[0][0], yz_out.z_axes[0][1], yz_out.z_axes[0][2]);

    // 10. Circle (list mode)
    float circle_radius = 0.1f;
    CircleInput circle_in;
    memset(&circle_in, 0, sizeof(CircleInput));
    circle_in.radius = circle_radius;
    circle_in.circle_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(circle_in.plane_origins[i], yz_out.origins[i], sizeof(float) * 3);
        memcpy(circle_in.plane_x_axes[i], yz_out.x_axes[i], sizeof(float) * 3);
        memcpy(circle_in.plane_y_axes[i], yz_out.y_axes[i], sizeof(float) * 3);
        memcpy(circle_in.plane_z_axes[i], yz_out.z_axes[i], sizeof(float) * 3);
    }
    CircleOutput circle_out;
    Circle_eval(&circle_in, &circle_out);
    printf("  [DEBUG Slat 0] Circle: center=(%.6f, %.6f, %.6f), radius=%.6f\n",
           circle_out.centers[0][0], circle_out.centers[0][1], circle_out.centers[0][2], circle_out.radius);

    // 10. CurveCurve intersection (list mode)
    CurveCurveInput cc_in;
    memset(&cc_in, 0, sizeof(CurveCurveInput));
    cc_in.curve_a_type = 1;  // circle
    cc_in.curve_b_type = 0;  // line
    cc_in.intersection_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(cc_in.circle_a_centers[i], circle_out.centers[i], sizeof(float) * 3);
        cc_in.circle_a_radii[i] = circle_out.radius;
        memcpy(cc_in.circle_a_x_axes[i], yz_out.x_axes[i], sizeof(float) * 3);
        memcpy(cc_in.circle_a_y_axes[i], yz_out.y_axes[i], sizeof(float) * 3);
        memcpy(cc_in.circle_a_z_axes[i], yz_out.z_axes[i], sizeof(float) * 3);
        memcpy(cc_in.line_b_starts[i], line_in_out.starts[i], sizeof(float) * 3);
        memcpy(cc_in.line_b_ends[i],   line_in_out.ends[i],   sizeof(float) * 3);
    }
    CurveCurveOutput cc_out;
    CurveCurve_eval(&cc_in, &cc_out);
    printf("  [DEBUG Slat 0] CurveCurve: circle center=(%.6f, %.6f, %.6f), radius=%.6f, line start=(%.6f, %.6f, %.6f) -> intersection_count=%d\n",
           cc_in.circle_a_centers[0][0], cc_in.circle_a_centers[0][1], cc_in.circle_a_centers[0][2],
           cc_in.circle_a_radii[0],
           cc_in.line_b_starts[0][0], cc_in.line_b_starts[0][1], cc_in.line_b_starts[0][2],
           cc_out.intersection_count);
    if (cc_out.intersection_count > 0) {
        printf("    [DEBUG Slat 0] CurveCurve points: first=(%.6f, %.6f, %.6f)\n",
               cc_out.points_list[0][0], cc_out.points_list[0][1], cc_out.points_list[0][2]);
    }

    // ---------------------------------------------------------------------
    // 11-13. Per-slat final stages: Line from intersection, Angle, Degrees
    //        (These depend on variable CurveCurve results, so kept per-slat)
    // ---------------------------------------------------------------------

    for (int i = 0; i < n; ++i) {
        // 11. Line from intersection points
        if (i < cc_out.intersection_count && 
            (cc_out.points_list[i][0] != 0.0f || cc_out.points_list[i][1] != 0.0f || cc_out.points_list[i][2] != 0.0f)) {
            LineInput line_final_in = {
                .use_two_points = 1
            };
            memcpy(line_final_in.start_point, cc_out.points_list[i], sizeof(float) * 3);
            
            // Compute end point from line direction
            float line_dir[3] = {
                line_in_out.ends[i][0] - line_in_out.starts[i][0],
                line_in_out.ends[i][1] - line_in_out.starts[i][1],
                line_in_out.ends[i][2] - line_in_out.starts[i][2]
            };
            float line_len = sqrtf(line_dir[0]*line_dir[0] + line_dir[1]*line_dir[1] + line_dir[2]*line_dir[2]);
            if (line_len > 0.0001f) {
                float scale = 100.0f / line_len;
                line_final_in.end_point[0] = cc_out.points_list[i][0] + line_dir[0] * scale;
                line_final_in.end_point[1] = cc_out.points_list[i][1] + line_dir[1] * scale;
                line_final_in.end_point[2] = cc_out.points_list[i][2] + line_dir[2] * scale;
            } else {
                line_final_in.end_point[0] = cc_out.points_list[i][0];
                line_final_in.end_point[1] = cc_out.points_list[i][1] + 100.0f;
                line_final_in.end_point[2] = cc_out.points_list[i][2];
            }

            LineOutput line_final_out;
            Line_eval(&line_final_in, &line_final_out);
            if (i == 0) {
                printf("  [DEBUG Slat 0] Line (final): start=(%.6f, %.6f, %.6f), end=(%.6f, %.6f, %.6f)\n",
                       line_final_out.start[0], line_final_out.start[1], line_final_out.start[2],
                       line_final_out.end[0],   line_final_out.end[1],   line_final_out.end[2]);
            }

            // 12-13. Angle and Degrees (list mode)
            float vec_b[3] = {
                line_final_out.end[0] - line_final_out.start[0],
                line_final_out.end[1] - line_final_out.start[1],
                line_final_out.end[2] - line_final_out.start[2]
            };
            float len_b = sqrtf(vec_b[0] * vec_b[0] + vec_b[1] * vec_b[1] + vec_b[2] * vec_b[2]);
            if (len_b > 0.0001f) {
                vec_b[0] /= len_b;
                vec_b[1] /= len_b;
                vec_b[2] /= len_b;
            } else {
                vec_b[0] = 0.0f;
                vec_b[1] = 0.0f;
                vec_b[2] = 1.0f;
            }

            AngleInput angle_in = {
                .use_oriented = 0
            };
            memcpy(angle_in.vector_a, pn2_out.x_axes[i], sizeof(float) * 3);
            memcpy(angle_in.vector_b, vec_b, sizeof(float) * 3);
            memcpy(angle_in.plane_normal, pn2_out.z_axes[i], sizeof(float) * 3);

            AngleOutput angle_out;
            Angle_eval(&angle_in, &angle_out);
            if (i == 0) {
                printf("  [DEBUG Slat 0] Angle: vector_a=(%.6f, %.6f, %.6f), vector_b=(%.6f, %.6f, %.6f) -> angle=%.6f rad\n",
                       angle_in.vector_a[0], angle_in.vector_a[1], angle_in.vector_a[2],
                       angle_in.vector_b[0], angle_in.vector_b[1], angle_in.vector_b[2],
                       angle_out.angle);
            }

            DegreesInput deg_in = { .radians = angle_out.angle };
            DegreesOutput deg_out;
            Degrees_eval(&deg_in, &deg_out);
            if (i == 0) {
                printf("  [DEBUG Slat 0] Degrees: radians=%.6f -> degrees=%.6f\n",
                       deg_in.radians, deg_out.degrees);
            }

            out->slat_angles[i] = deg_out.degrees;
        } else {
            out->slat_angles[i] = 0.0f;
            if (i == 0) {
                printf("  [DEBUG Slat 0] No intersection found (intersection_count=%d, expected >=1)\n", cc_out.intersection_count);
            }
        }
    }

    // For any remaining slats beyond n (if cfg->number_of_slats > n), set angle to 0
    for (int i = n; i < cfg->number_of_slats && i < MAX_ANGLES; ++i) {
        out->slat_angles[i] = 0.0f;
    }
}


