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

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

void core_group_eval(
    const ShadeConfig *cfg,
    const SunGroupOutput *sun,
    const SlatsGroupOutput *slats,
    const DirectionGroupOutput *dir,
    const TargetsGroupOutput *targets,
    CoreGroupOutput *out
) {
    int max_slats = cfg->number_of_slats;
    if (max_slats > MAX_ANGLES) max_slats = MAX_ANGLES;
    out->angle_count = cfg->number_of_slats;

    if (max_slats <= 0) return;

    // STEP 1: Area - get slat centroids
    AreaInput area_in;
    memset(&area_in, 0, sizeof(AreaInput));
    area_in.geometry_type = 2;

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

    // STEP 2: Move "New Sun"
    MoveInput move_sun_in;
    memset(&move_sun_in, 0, sizeof(MoveInput));
    move_sun_in.geometry_type = 0;
    move_sun_in.motion[0] = sun->sun_pt[0];
    move_sun_in.motion[1] = sun->sun_pt[1];
    move_sun_in.motion[2] = sun->sun_pt[2];
    move_sun_in.point_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(move_sun_in.points[i], slat_centroids[i], sizeof(float) * 3);
    }

    MoveOutput move_sun_out;
    Move_eval(&move_sun_in, &move_sun_out);

    // STEP 3: Line "Out Ray"
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

    // STEP 4: Rotate Targets
    float orientation_rad = cfg->orientation_deg * (float)M_PI / 180.0f;

    RotateInput rot_tgt_in;
    memset(&rot_tgt_in, 0, sizeof(RotateInput));
    rot_tgt_in.geometry_type = 0;
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

    // STEP 5: Line "In Ray"
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

    // STEP 6: Project
    ProjectInput proj_in;
    memset(&proj_in, 0, sizeof(ProjectInput));
    proj_in.curve_type = 1;
    proj_in.brep_type = 1;
    memcpy(proj_in.plane_origin, dir->plane_origin, sizeof(float) * 3);
    memcpy(proj_in.plane_z_axis, dir->plane_z_axis, sizeof(float) * 3);

    proj_in.line_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(proj_in.line_starts[i], line_out_out.starts[i], sizeof(float) * 3);
        memcpy(proj_in.line_ends[i], line_out_out.ends[i], sizeof(float) * 3);
    }

    ProjectOutput proj_out;
    Project_eval(&proj_in, &proj_out);

    // STEP 7: YZ Plane
    YZPlaneInput yz_in;
    memset(&yz_in, 0, sizeof(YZPlaneInput));
    yz_in.plane_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(yz_in.origins[i], slat_centroids[i], sizeof(float) * 3);
    }

    YZPlaneOutput yz_out;
    YZPlane_eval(&yz_in, &yz_out);

    // STEP 8: Circle
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

    // STEP 9: Curve|Curve #1 (Circle ∩ In Ray)
    CurveCurveInput cc_in_in;
    memset(&cc_in_in, 0, sizeof(CurveCurveInput));
    cc_in_in.curve_a_type = 1;
    cc_in_in.curve_b_type = 0;
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

    // STEP 10: Curve|Curve #2 (Circle ∩ Projected)
    CurveCurveInput cc_proj_in;
    memset(&cc_proj_in, 0, sizeof(CurveCurveInput));
    cc_proj_in.curve_a_type = 1;
    cc_proj_in.curve_b_type = 0;
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

    // STEP 11: Line Final (CCX1 → CCX2)
    LineInput line_final_in;
    memset(&line_final_in, 0, sizeof(LineInput));
    line_final_in.use_two_points = 1;
    line_final_in.line_count = n;
    for (int i = 0; i < n; ++i) {
        if (i < cc_in_out.intersection_count) {
            memcpy(line_final_in.start_points[i], cc_in_out.points_list[i], sizeof(float) * 3);
        } else {
            memset(line_final_in.start_points[i], 0, sizeof(float) * 3);
        }
        
        if (i < cc_proj_out.intersection_count) {
            memcpy(line_final_in.end_points[i], cc_proj_out.points_list[i], sizeof(float) * 3);
        } else {
            memset(line_final_in.end_points[i], 0, sizeof(float) * 3);
        }
    }

    LineOutput line_final_out;
    Line_eval(&line_final_in, &line_final_out);

    // STEP 12-13: PolyLines (compute directions)
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

    // STEP 14: Plane Normal #1
    PlaneNormalInput pn1_in;
    memset(&pn1_in, 0, sizeof(PlaneNormalInput));
    pn1_in.plane_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(pn1_in.origins[i], slat_centroids[i], sizeof(float) * 3);
        memcpy(pn1_in.z_axes[i], targets_dir, sizeof(float) * 3);
    }

    PlaneNormalOutput pn1_out;
    PlaneNormal_eval(&pn1_in, &pn1_out);

    // STEP 15: Construct Plane
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

    // STEP 16: List Item (last centroid)
    float last_centroid[3];
    memcpy(last_centroid, slat_centroids[n-1], sizeof(float) * 3);

    // STEP 17: List Item (first plane normal)
    float first_plane_normal[3];
    memcpy(first_plane_normal, pn1_out.z_axes[0], sizeof(float) * 3);

    // STEP 18: Plane Normal #2
    PlaneNormalInput pn2_in;
    memset(&pn2_in, 0, sizeof(PlaneNormalInput));
    pn2_in.plane_count = n;
    for (int i = 0; i < n; ++i) {
        memcpy(pn2_in.origins[i], last_centroid, sizeof(float) * 3);
        memcpy(pn2_in.z_axes[i], cp_out.z_axes[i], sizeof(float) * 3);
    }

    PlaneNormalOutput pn2_out;
    PlaneNormal_eval(&pn2_in, &pn2_out);

    // STEP 19: Angle
    AngleInput angle_in;
    memset(&angle_in, 0, sizeof(AngleInput));
    angle_in.use_oriented = 1;
    angle_in.angle_count = n;
    
    for (int i = 0; i < n; ++i) {
        memcpy(angle_in.vectors_a[i], first_plane_normal, sizeof(float) * 3);
        
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
        memcpy(angle_in.plane_normals[i], pn2_out.z_axes[i], sizeof(float) * 3);
    }

    AngleOutput angle_out;
    Angle_eval(&angle_in, &angle_out);

    // STEP 20: Degrees
    DegreesInput deg_in;
    memset(&deg_in, 0, sizeof(DegreesInput));
    deg_in.radians_count = n;
    for (int i = 0; i < n; ++i) {
        deg_in.radians_list[i] = angle_out.angles[i];
    }

    DegreesOutput deg_out;
    Degrees_eval(&deg_in, &deg_out);

    // Copy results to output
    for (int i = 0; i < n; ++i) {
        out->slat_angles[i] = deg_out.degrees_list[i];
    }

    // Zero out any remaining slots
    for (int i = n; i < cfg->number_of_slats && i < MAX_ANGLES; ++i) {
        out->slat_angles[i] = 0.0f;
    }
}

