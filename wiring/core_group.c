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

/*
 * CORE GROUP EVALUATION
 * 
 * This implements the exact GH wiring for the coreGroup as documented in components.json
 * 
 * Evaluation Order (by GUID):
 * 1. 3bd2c1d3 - Area (slats centroids)
 * 2. 0f529988 - Move "New Sun" (centroids + sun_pt)
 * 3. 9a33273a - Line "Out Ray"
 * 4. 464c66b3 - Rotate (targets)
 * 5. c7dba531 - Line "In Ray"
 * 6. 9cd053c9 - Project (Out Ray onto direction plane)
 * 7. d52b786d - YZ Plane (at centroids)
 * 8. 2c8beafc - Circle
 * 9. bdde1ec6 - Curve|Curve #1 (Circle ∩ In Ray)
 * 10. 0974a3a7 - Curve|Curve #2 (Circle ∩ Projected)
 * 11. ff77f5b8 - Line (CCX1 → CCX2)
 * 12. ef803855 - PolyLine (targets - ALL vertices as ONE polyline)
 * 13. 910c335c - PolyLine (reversed centroids - ALL vertices as ONE polyline)
 * 14. 326da981 - Plane Normal #1
 * 15. 30f76ec5 - Construct Plane
 * 16. 9ff79870 - List Item (centroid[9] - LAST centroid)
 * 17. 157c48b5 - List Item (plane[0] - FIRST plane)
 * 18. 011398ea - Plane Normal #2
 * 19. 0d695e6b - Angle
 * 20. fa0ba5a6 - Degrees
 */

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

    // =========================================================================
    // STEP 1: Area (GUID: 3bd2c1d3-149d-49fb-952c-8db272035f9e)
    // Input: Rotated slat rectangles from slatsGroup
    // Output: Centroids of each slat (10 points)
    // =========================================================================

    AreaInput area_in;
    memset(&area_in, 0, sizeof(AreaInput));
    area_in.geometry_type = 2; // rectangle

    int rect_count = slats->slat_count;
    if (rect_count > max_slats) rect_count = max_slats;
    if (rect_count <= 0) {
        for (int i = 0; i < max_slats; ++i) out->slat_angles[i] = 0.0f;
        return;
    }

    area_in.rectangle_count = rect_count;
    for (int i = 0; i < rect_count; ++i) {
        memcpy(area_in.rectangles[i], slats->slat_rectangles[i], sizeof(float) * 4 * 3);
    }

    AreaOutput area_out;
    Area_eval(&area_in, &area_out);

    float slat_centroids[MAX_ANGLES][3];
    int n = area_out.centroid_count;
    if (n > rect_count) n = rect_count;
    if (n > max_slats) n = max_slats;
    
    for (int i = 0; i < n; ++i) {
        slat_centroids[i][0] = area_out.centroids[i][0];
        slat_centroids[i][1] = area_out.centroids[i][1];
        slat_centroids[i][2] = area_out.centroids[i][2];
    }

    printf("  [DEBUG Slat 0] Area (slats): rect_idx=0, centroid_count=%d, first=(%.6f, %.6f, %.6f)\n",
           n, slat_centroids[0][0], slat_centroids[0][1], slat_centroids[0][2]);
    if (n > 1) {
        printf("    [DEBUG Slat 0] Area list: second=(%.6f, %.6f, %.6f)\n",
               slat_centroids[1][0], slat_centroids[1][1], slat_centroids[1][2]);
    }
    if (n > 2) {
        printf("    [DEBUG Slat 0] Area list: last=(%.6f, %.6f, %.6f)\n",
               slat_centroids[n-1][0], slat_centroids[n-1][1], slat_centroids[n-1][2]);
    }

    // =========================================================================
    // STEP 2: Move "New Sun" (GUID: 0f529988-b68b-4d48-9a48-cf099af69050)
    // Input Geometry: Area Centroids (10 points)
    // Input Motion: sun->sun_pt (sun point at ~100km distance, NOT sun_vector!)
    // Output: Moved points (centroids + sun_pt)
    // =========================================================================

    MoveInput move_sun_in;
    memset(&move_sun_in, 0, sizeof(MoveInput));
    move_sun_in.geometry_type = 0; // point
    
    // CRITICAL FIX: Use sun_pt as motion, NOT sun_vector!
    // GH wiring: ExplodeTree Branch 0 → sun_pt (e.g., 33219, -61164, 71800)
    move_sun_in.motion[0] = sun->sun_pt[0];
    move_sun_in.motion[1] = sun->sun_pt[1];
    move_sun_in.motion[2] = sun->sun_pt[2];
    
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

    // =========================================================================
    // STEP 3: Line "Out Ray" (GUID: 9a33273a-910e-439d-98d5-d225e29faebf)
    // Start: Area Centroids
    // End: Move "New Sun" output
    // Output: 10 lines (out rays from centroid toward sun)
    // =========================================================================

    LineInput line_out_in;
    memset(&line_out_in, 0, sizeof(LineInput));
    line_out_in.use_two_points = 1;
    line_out_in.line_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(line_out_in.start_points[i], slat_centroids[i], sizeof(float) * 3);
        memcpy(line_out_in.end_points[i], move_sun_out.points[i], sizeof(float) * 3);
    }

    LineOutput line_out_out;
    Line_eval(&line_out_in, &line_out_out);

    printf("  [DEBUG Slat 0] Line (out ray): start=(%.6f, %.6f, %.6f), end=(%.6f, %.6f, %.6f)\n",
           line_out_out.starts[0][0], line_out_out.starts[0][1], line_out_out.starts[0][2],
           line_out_out.ends[0][0], line_out_out.ends[0][1], line_out_out.ends[0][2]);

    // =========================================================================
    // STEP 4: Rotate Targets (GUID: 464c66b3-4ac6-4cc0-b283-407f8fe787a3)
    // Input: targets->target_points (from targetsGroup)
    // Angle: cfg->orientation_deg converted to radians
    // Output: 10 rotated target points
    // =========================================================================

    float orientation_rad = cfg->orientation_deg * (float)M_PI / 180.0f;

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
    
    int target_count = targets->target_count;
    if (target_count > n) target_count = n;
    rot_tgt_in.point_count = target_count;
    
    for (int i = 0; i < target_count; ++i) {
        memcpy(rot_tgt_in.points[i], targets->target_points[i], sizeof(float) * 3);
    }

    RotateOutput rot_tgt_out;
    Rotate_eval(&rot_tgt_in, &rot_tgt_out);

    float rotated_targets[MAX_ANGLES][3];
    for (int i = 0; i < n; ++i) {
        if (i < rot_tgt_out.point_count) {
            memcpy(rotated_targets[i], rot_tgt_out.points[i], sizeof(float) * 3);
        } else {
            memcpy(rotated_targets[i], rot_tgt_out.points[rot_tgt_out.point_count - 1], sizeof(float) * 3);
        }
    }

    printf("  [DEBUG Slat 0] Rotate (target): raw=(%.6f, %.6f, %.6f) -> rotated=(%.6f, %.6f, %.6f)\n",
           rot_tgt_in.points[0][0], rot_tgt_in.points[0][1], rot_tgt_in.points[0][2],
           rotated_targets[0][0], rotated_targets[0][1], rotated_targets[0][2]);

    // =========================================================================
    // STEP 5: Line "In Ray" (GUID: c7dba531-36f1-4a2d-8e0e-ed94b3873bba)
    // Start: Area Centroids (with GRAFT in GH, but diagonal pairing result)
    // End: Rotated Targets
    // Output: 10 lines (in rays from centroid toward target)
    // =========================================================================

    LineInput line_in_in;
    memset(&line_in_in, 0, sizeof(LineInput));
    line_in_in.use_two_points = 1;
    line_in_in.line_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(line_in_in.start_points[i], slat_centroids[i], sizeof(float) * 3);
        memcpy(line_in_in.end_points[i], rotated_targets[i], sizeof(float) * 3);
    }

    LineOutput line_in_out;
    Line_eval(&line_in_in, &line_in_out);

    printf("  [DEBUG Slat 0] Line (in ray): start=(%.6f, %.6f, %.6f), end=(%.6f, %.6f, %.6f)\n",
           line_in_out.starts[0][0], line_in_out.starts[0][1], line_in_out.starts[0][2],
           line_in_out.ends[0][0], line_in_out.ends[0][1], line_in_out.ends[0][2]);

    // =========================================================================
    // STEP 6: Project (GUID: 9cd053c9-3dd2-432b-aa46-a29a4b05c339)
    // Curve: Out Ray lines (with FLATTEN in GH)
    // Brep: Direction group's rotated box
    // Direction: Direction group's rotated plane normal
    // Output: 10 projected curves
    // =========================================================================

    ProjectInput proj_in;
    memset(&proj_in, 0, sizeof(ProjectInput));
    proj_in.curve_type = 1;  // line
    proj_in.brep_type = 1;   // box
    memcpy(proj_in.plane_origin, dir->plane_origin, sizeof(float) * 3);
    memcpy(proj_in.plane_z_axis, dir->plane_z_axis, sizeof(float) * 3);

    proj_in.line_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(proj_in.line_starts[i], line_out_out.starts[i], sizeof(float) * 3);
        memcpy(proj_in.line_ends[i], line_out_out.ends[i], sizeof(float) * 3);
    }

    ProjectOutput proj_out;
    Project_eval(&proj_in, &proj_out);

    printf("  [DEBUG Slat 0] Project: line_start=(%.6f, %.6f, %.6f), plane_origin=(%.6f, %.6f, %.6f) -> projected_start=(%.6f, %.6f, %.6f)\n",
           proj_in.line_starts[0][0], proj_in.line_starts[0][1], proj_in.line_starts[0][2],
           proj_in.plane_origin[0], proj_in.plane_origin[1], proj_in.plane_origin[2],
           proj_out.line_starts[0][0], proj_out.line_starts[0][1], proj_out.line_starts[0][2]);

    // =========================================================================
    // STEP 7: YZ Plane (GUID: d52b786d-9ccd-411a-824c-3ae52ddc5438)
    // Origin: Area Centroids
    // Output: 10 YZ planes at centroid locations
    // =========================================================================

    YZPlaneInput yz_in;
    memset(&yz_in, 0, sizeof(YZPlaneInput));
    yz_in.plane_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(yz_in.origins[i], slat_centroids[i], sizeof(float) * 3);
    }

    YZPlaneOutput yz_out;
    YZPlane_eval(&yz_in, &yz_out);

    printf("  [DEBUG Slat 0] YZPlane: origin=(%.6f, %.6f, %.6f) -> x_axis=(%.6f, %.6f, %.6f), z_axis=(%.6f, %.6f, %.6f)\n",
           yz_out.origins[0][0], yz_out.origins[0][1], yz_out.origins[0][2],
           yz_out.x_axes[0][0], yz_out.x_axes[0][1], yz_out.x_axes[0][2],
           yz_out.z_axes[0][0], yz_out.z_axes[0][1], yz_out.z_axes[0][2]);

    // =========================================================================
    // STEP 8: Circle (GUID: 2c8beafc-c3a7-425a-905e-4830f637c094)
    // Plane: YZ Plane output
    // Radius: 0.1 (persistent data)
    // Output: 10 circles
    // =========================================================================

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
           circle_out.centers[0][0], circle_out.centers[0][1], circle_out.centers[0][2], 
           circle_out.radius);

    // =========================================================================
    // STEP 9: Curve|Curve #1 (GUID: bdde1ec6-2004-476b-b670-3de72b6fb0b0)
    // Curve A: Circle
    // Curve B: In Ray Line
    // Output: Intersection points (ccx_in_pts)
    // =========================================================================

    CurveCurveInput cc_in_in;
    memset(&cc_in_in, 0, sizeof(CurveCurveInput));
    cc_in_in.curve_a_type = 1;  // circle
    cc_in_in.curve_b_type = 0;  // line
    cc_in_in.intersection_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(cc_in_in.circle_a_centers[i], circle_out.centers[i], sizeof(float) * 3);
        cc_in_in.circle_a_radii[i] = circle_out.radius;
        memcpy(cc_in_in.circle_a_x_axes[i], yz_out.x_axes[i], sizeof(float) * 3);
        memcpy(cc_in_in.circle_a_y_axes[i], yz_out.y_axes[i], sizeof(float) * 3);
        memcpy(cc_in_in.circle_a_z_axes[i], yz_out.z_axes[i], sizeof(float) * 3);
        memcpy(cc_in_in.line_b_starts[i], line_in_out.starts[i], sizeof(float) * 3);
        memcpy(cc_in_in.line_b_ends[i], line_in_out.ends[i], sizeof(float) * 3);
    }

    CurveCurveOutput cc_in_out;
    CurveCurve_eval(&cc_in_in, &cc_in_out);

    printf("  [DEBUG Slat 0] CurveCurve (In Ray): intersection_count=%d, first=(%.6f, %.6f, %.6f)\n",
           cc_in_out.intersection_count,
           cc_in_out.points_list[0][0], cc_in_out.points_list[0][1], cc_in_out.points_list[0][2]);

    // =========================================================================
    // STEP 10: Curve|Curve #2 (GUID: 0974a3a7-c1f6-4451-89e4-ad726846f035)
    // Curve A: Circle
    // Curve B: Projected Curve (from Project output)
    // Output: Intersection points (ccx_proj_pts)
    // =========================================================================

    CurveCurveInput cc_proj_in;
    memset(&cc_proj_in, 0, sizeof(CurveCurveInput));
    cc_proj_in.curve_a_type = 1;  // circle
    cc_proj_in.curve_b_type = 0;  // line (projected curves are still lines)
    cc_proj_in.intersection_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(cc_proj_in.circle_a_centers[i], circle_out.centers[i], sizeof(float) * 3);
        cc_proj_in.circle_a_radii[i] = circle_out.radius;
        memcpy(cc_proj_in.circle_a_x_axes[i], yz_out.x_axes[i], sizeof(float) * 3);
        memcpy(cc_proj_in.circle_a_y_axes[i], yz_out.y_axes[i], sizeof(float) * 3);
        memcpy(cc_proj_in.circle_a_z_axes[i], yz_out.z_axes[i], sizeof(float) * 3);
        memcpy(cc_proj_in.line_b_starts[i], proj_out.line_starts[i], sizeof(float) * 3);
        memcpy(cc_proj_in.line_b_ends[i], proj_out.line_ends[i], sizeof(float) * 3);
    }

    CurveCurveOutput cc_proj_out;
    CurveCurve_eval(&cc_proj_in, &cc_proj_out);

    printf("  [DEBUG Slat 0] CurveCurve (Projected): intersection_count=%d, first=(%.6f, %.6f, %.6f)\n",
           cc_proj_out.intersection_count,
           cc_proj_out.points_list[0][0], cc_proj_out.points_list[0][1], cc_proj_out.points_list[0][2]);

    // =========================================================================
    // STEP 11: Line Final (GUID: ff77f5b8-1125-4565-bdf6-0922a443efcf)
    // Start: CCX #1 Points (Circle ∩ In Ray)
    // End: CCX #2 Points (Circle ∩ Projected)
    // Output: 10 lines connecting the two intersection points
    // =========================================================================

    LineInput line_final_in;
    memset(&line_final_in, 0, sizeof(LineInput));
    line_final_in.use_two_points = 1;
    line_final_in.line_count = n;
    for (int i = 0; i < n; ++i) {
        // Start from CCX #1 (Circle ∩ In Ray)
        if (i < cc_in_out.intersection_count) {
            memcpy(line_final_in.start_points[i], cc_in_out.points_list[i], sizeof(float) * 3);
        } else {
            memset(line_final_in.start_points[i], 0, sizeof(float) * 3);
        }
        
        // End at CCX #2 (Circle ∩ Projected)
        if (i < cc_proj_out.intersection_count) {
            memcpy(line_final_in.end_points[i], cc_proj_out.points_list[i], sizeof(float) * 3);
        } else {
            memset(line_final_in.end_points[i], 0, sizeof(float) * 3);
        }
    }

    LineOutput line_final_out;
    Line_eval(&line_final_in, &line_final_out);

    printf("  [DEBUG Slat 0] Line (final): start=(%.6f, %.6f, %.6f), end=(%.6f, %.6f, %.6f)\n",
           line_final_out.starts[0][0], line_final_out.starts[0][1], line_final_out.starts[0][2],
           line_final_out.ends[0][0], line_final_out.ends[0][1], line_final_out.ends[0][2]);

    // =========================================================================
    // STEP 12-13: PolyLines (GUIDs: ef803855, 910c335c)
    // These create SINGLE polylines from ALL vertices (not per-slat)
    // Used for Plane Normal Z-axis computation
    // 
    // ef803855: Rotated targets → ONE polyline with 10 vertices
    // 910c335c: Reversed centroids → ONE polyline with 10 vertices
    // =========================================================================

    // For Plane Normal computation, we need the direction from polyline
    // GH uses the polyline's first segment direction as Z-axis
    // Targets polyline direction: from target[0] to target[1]
    float targets_dir[3] = {
        rotated_targets[1][0] - rotated_targets[0][0],
        rotated_targets[1][1] - rotated_targets[0][1],
        rotated_targets[1][2] - rotated_targets[0][2]
    };
    float targets_len = sqrtf(targets_dir[0]*targets_dir[0] + targets_dir[1]*targets_dir[1] + targets_dir[2]*targets_dir[2]);
    if (targets_len > 0.0001f) {
        targets_dir[0] /= targets_len;
        targets_dir[1] /= targets_len;
        targets_dir[2] /= targets_len;
    }

    // Reversed centroids: from centroid[n-1] to centroid[n-2]
    // Since all centroids have same X and Y, direction is purely in Z
    float centroids_rev_dir[3] = {
        slat_centroids[n-2][0] - slat_centroids[n-1][0],
        slat_centroids[n-2][1] - slat_centroids[n-1][1],
        slat_centroids[n-2][2] - slat_centroids[n-1][2]
    };
    float centroids_len = sqrtf(centroids_rev_dir[0]*centroids_rev_dir[0] + 
                                 centroids_rev_dir[1]*centroids_rev_dir[1] + 
                                 centroids_rev_dir[2]*centroids_rev_dir[2]);
    if (centroids_len > 0.0001f) {
        centroids_rev_dir[0] /= centroids_len;
        centroids_rev_dir[1] /= centroids_len;
        centroids_rev_dir[2] /= centroids_len;
    }

    printf("  [DEBUG] PolyLine directions: targets_dir=(%.6f, %.6f, %.6f), centroids_rev_dir=(%.6f, %.6f, %.6f)\n",
           targets_dir[0], targets_dir[1], targets_dir[2],
           centroids_rev_dir[0], centroids_rev_dir[1], centroids_rev_dir[2]);

    // =========================================================================
    // STEP 14: Plane Normal #1 (GUID: 326da981-351e-4794-9d60-77e8e87bd778)
    // Origin: Area Centroids
    // Z-Axis: PolyLine (targets) - GH converts polyline to direction vector
    // Output: 10 planes
    // 
    // GH uses polyline as Z-axis by taking its direction, not the curve itself
    // The direction from first to second target is approximately (0, -0.389, 0) normalized to (0, -1, 0)
    // =========================================================================

    PlaneNormalInput pn1_in;
    memset(&pn1_in, 0, sizeof(PlaneNormalInput));
    pn1_in.plane_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(pn1_in.origins[i], slat_centroids[i], sizeof(float) * 3);
        // Use targets direction as Z-axis (GH behavior: polyline → direction)
        memcpy(pn1_in.z_axes[i], targets_dir, sizeof(float) * 3);
    }

    PlaneNormalOutput pn1_out;
    PlaneNormal_eval(&pn1_in, &pn1_out);

    printf("  [DEBUG Slat 0] PlaneNormal #1: origin=(%.6f, %.6f, %.6f), z_axis=(%.6f, %.6f, %.6f) -> x_axis=(%.6f, %.6f, %.6f)\n",
           pn1_in.origins[0][0], pn1_in.origins[0][1], pn1_in.origins[0][2],
           pn1_in.z_axes[0][0], pn1_in.z_axes[0][1], pn1_in.z_axes[0][2],
           pn1_out.x_axes[0][0], pn1_out.x_axes[0][1], pn1_out.x_axes[0][2]);

    // =========================================================================
    // STEP 15: Construct Plane (GUID: 30f76ec5-d532-4903-aa18-cd18b27442f9)
    // Origin: Area Centroids
    // X-Axis: PolyLine (targets) direction
    // Y-Axis: PolyLine (reversed centroids) direction
    // Output: 10 planes
    // =========================================================================

    ConstructPlaneInput cp_in;
    memset(&cp_in, 0, sizeof(ConstructPlaneInput));
    cp_in.plane_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(cp_in.origins[i], slat_centroids[i], sizeof(float) * 3);
        memcpy(cp_in.x_axes[i], targets_dir, sizeof(float) * 3);
        memcpy(cp_in.y_axes[i], centroids_rev_dir, sizeof(float) * 3);
    }

    ConstructPlaneOutput cp_out;
    ConstructPlane_eval(&cp_in, &cp_out);

    printf("  [DEBUG Slat 0] ConstructPlane: x_axis=(%.6f, %.6f, %.6f), y_axis=(%.6f, %.6f, %.6f) -> z_axis=(%.6f, %.6f, %.6f)\n",
           cp_in.x_axes[0][0], cp_in.x_axes[0][1], cp_in.x_axes[0][2],
           cp_in.y_axes[0][0], cp_in.y_axes[0][1], cp_in.y_axes[0][2],
           cp_out.z_axes[0][0], cp_out.z_axes[0][1], cp_out.z_axes[0][2]);

    // =========================================================================
    // STEP 16: List Item (GUID: 9ff79870-05d0-483d-87be-b3641d71c6fc)
    // List: Area Centroids
    // Index: number_of_slats - 1 = 9 (expression "x-1")
    // Output: Last centroid = centroid[9]
    // =========================================================================

    // GH extracts the LAST centroid (index = n-1)
    float last_centroid[3];
    memcpy(last_centroid, slat_centroids[n-1], sizeof(float) * 3);

    printf("  [DEBUG] ListItem (centroid[%d]): (%.6f, %.6f, %.6f)\n",
           n-1, last_centroid[0], last_centroid[1], last_centroid[2]);

    // =========================================================================
    // STEP 17: List Item (GUID: 157c48b5-0aed-49e5-a808-d4c64666062d)
    // List: Plane Normal #1 output (10 planes)
    // Index: 0 (default)
    // Output: First plane = plane[0]
    // 
    // CRITICAL: When GH converts a Plane to a Vector (for Angle's Vector A input),
    // it uses the plane's Z-AXIS (normal), NOT the X-axis!
    // =========================================================================

    // GH extracts the FIRST plane (index = 0)
    // The Z-AXIS (normal) of this plane becomes Vector A for Angle
    float first_plane_normal[3];
    memcpy(first_plane_normal, pn1_out.z_axes[0], sizeof(float) * 3);

    printf("  [DEBUG] ListItem (plane[0].z_axis as Vector A): (%.6f, %.6f, %.6f)\n",
           first_plane_normal[0], first_plane_normal[1], first_plane_normal[2]);

    // =========================================================================
    // STEP 18: Plane Normal #2 (GUID: 011398ea-ce1d-412a-afeb-fe91e8fac96c)
    // Origin: ListItem output = last_centroid (SINGLE point, replicated 10 times)
    // Z-Axis: ConstructPlane output (each plane converted to its z_axis)
    // Output: 10 planes (all with same origin at last_centroid)
    // =========================================================================

    PlaneNormalInput pn2_in;
    memset(&pn2_in, 0, sizeof(PlaneNormalInput));
    pn2_in.plane_count = n;
    for (int i = 0; i < n; ++i) {
        // Origin is ALWAYS the last centroid (from ListItem)
        memcpy(pn2_in.origins[i], last_centroid, sizeof(float) * 3);
        // Z-axis from ConstructPlane output for each slat
        memcpy(pn2_in.z_axes[i], cp_out.z_axes[i], sizeof(float) * 3);
    }

    PlaneNormalOutput pn2_out;
    PlaneNormal_eval(&pn2_in, &pn2_out);

    printf("  [DEBUG Slat 0] PlaneNormal #2: origin=(%.6f, %.6f, %.6f), z_axis=(%.6f, %.6f, %.6f) -> x_axis=(%.6f, %.6f, %.6f)\n",
           pn2_in.origins[0][0], pn2_in.origins[0][1], pn2_in.origins[0][2],
           pn2_in.z_axes[0][0], pn2_in.z_axes[0][1], pn2_in.z_axes[0][2],
           pn2_out.x_axes[0][0], pn2_out.x_axes[0][1], pn2_out.x_axes[0][2]);

    // =========================================================================
    // STEP 19: Angle (GUID: 0d695e6b-3696-4337-bc80-d14104f8a59e)
    // Vector A: ListItem 157c48b5 output (plane[0].x_axis) - SINGLE vector
    // Vector B: Line ff77f5b8 output converted to direction vectors - 10 vectors
    // Plane: PlaneNormal #2 output - 10 planes
    // Output: 10 angles in radians
    // =========================================================================

    AngleInput angle_in;
    memset(&angle_in, 0, sizeof(AngleInput));
    angle_in.use_oriented = 1;  // Use oriented angle with plane
    angle_in.angle_count = n;
    
    for (int i = 0; i < n; ++i) {
        // Vector A: SAME for all slats (from ListItem - first plane's Z-axis/normal)
        // GH converts Plane → Z-axis when used as Vector input
        memcpy(angle_in.vectors_a[i], first_plane_normal, sizeof(float) * 3);
        
        // Vector B: Direction of line_final for each slat
        float line_dir[3] = {
            line_final_out.ends[i][0] - line_final_out.starts[i][0],
            line_final_out.ends[i][1] - line_final_out.starts[i][1],
            line_final_out.ends[i][2] - line_final_out.starts[i][2]
        };
        float line_len = sqrtf(line_dir[0]*line_dir[0] + line_dir[1]*line_dir[1] + line_dir[2]*line_dir[2]);
        if (line_len > 0.0001f) {
            line_dir[0] /= line_len;
            line_dir[1] /= line_len;
            line_dir[2] /= line_len;
        } else {
            line_dir[0] = 0.0f;
            line_dir[1] = 1.0f;
            line_dir[2] = 0.0f;
        }
        memcpy(angle_in.vectors_b[i], line_dir, sizeof(float) * 3);
        
        // Plane normal from PlaneNormal #2
        memcpy(angle_in.plane_normals[i], pn2_out.z_axes[i], sizeof(float) * 3);
    }

    AngleOutput angle_out;
    Angle_eval(&angle_in, &angle_out);

    printf("  [DEBUG Slat 0] Angle: vector_a=(%.6f, %.6f, %.6f), vector_b=(%.6f, %.6f, %.6f) -> angle=%.6f rad\n",
           angle_in.vectors_a[0][0], angle_in.vectors_a[0][1], angle_in.vectors_a[0][2],
           angle_in.vectors_b[0][0], angle_in.vectors_b[0][1], angle_in.vectors_b[0][2],
           angle_out.angles[0]);

    // =========================================================================
    // STEP 20: Degrees (GUID: fa0ba5a6-7dd9-43f4-a82a-cf02841d0f58)
    // Input: Angle output in radians
    // Output: Angles in degrees
    // =========================================================================

    DegreesInput deg_in;
    memset(&deg_in, 0, sizeof(DegreesInput));
    deg_in.radians_count = n;
    for (int i = 0; i < n; ++i) {
        deg_in.radians_list[i] = angle_out.angles[i];
    }

    DegreesOutput deg_out;
    Degrees_eval(&deg_in, &deg_out);

    printf("  [DEBUG Slat 0] Degrees: radians=%.6f -> degrees=%.6f\n",
           deg_in.radians_list[0], deg_out.degrees_list[0]);

    // =========================================================================
    // Copy results to output
    // =========================================================================

    printf("  Calculated %d slat angles:\n", n);
    for (int i = 0; i < n; ++i) {
        out->slat_angles[i] = deg_out.degrees_list[i];
        printf("    Slat %d: %.6f degrees\n", i, out->slat_angles[i]);
    }

    // Zero out any remaining slots
    for (int i = n; i < cfg->number_of_slats && i < MAX_ANGLES; ++i) {
        out->slat_angles[i] = 0.0f;
    }
}
