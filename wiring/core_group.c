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
    out->angle_count = cfg->number_of_slats;
    
    // For each slat, calculate the angle
    for (int i = 0; i < cfg->number_of_slats && i < MAX_ANGLES; i++) {
        // Debug output for first slat only
        if (i == 0) {
            printf("  [DEBUG Slat 0] Starting angle calculation...\n");
        }
        
        // 1. Move sun point (New Sun)
        MoveInput move_sun_in = {
            .geometry_type = 0,  // point
            .motion = {0.0f, 0.0f, 10.0f}  // Default from persistent data
        };
        memcpy(move_sun_in.point, sun->sun_pt, sizeof(float) * 3);
        // Use sun vector as motion (from ExplodeTree branch 0)
        memcpy(move_sun_in.motion, sun->sun_vector, sizeof(float) * 3);
        MoveOutput move_sun_out;
        Move_eval(&move_sun_in, &move_sun_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] Move (sun): point=(%.6f, %.6f, %.6f), motion=(%.6f, %.6f, %.6f) -> (%.6f, %.6f, %.6f)\n",
                   move_sun_in.point[0], move_sun_in.point[1], move_sun_in.point[2],
                   move_sun_in.motion[0], move_sun_in.motion[1], move_sun_in.motion[2],
                   move_sun_out.point[0], move_sun_out.point[1], move_sun_out.point[2]);
        }
        
        // 2. Line from sun to moved sun (Out Ray)
        LineInput line_out_in = {
            .use_two_points = 1,
        };
        memcpy(line_out_in.start_point, sun->sun_pt, sizeof(float) * 3);
        memcpy(line_out_in.end_point, move_sun_out.point, sizeof(float) * 3);
        LineOutput line_out_out;
        Line_eval(&line_out_in, &line_out_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] Line (out ray): start=(%.6f, %.6f, %.6f), end=(%.6f, %.6f, %.6f)\n",
                   line_out_out.start[0], line_out_out.start[1], line_out_out.start[2],
                   line_out_out.end[0], line_out_out.end[1], line_out_out.end[2]);
        }
        
        // 3. Line from sun to target (In Ray)
        LineInput line_in_in = {
            .use_two_points = 1,
        };
        memcpy(line_in_in.start_point, sun->sun_pt, sizeof(float) * 3);
        if (i < targets->target_count) {
            memcpy(line_in_in.end_point, targets->target_points[i], sizeof(float) * 3);
        } else {
            memcpy(line_in_in.end_point, targets->target_points[0], sizeof(float) * 3);
        }
        LineOutput line_in_out;
        Line_eval(&line_in_in, &line_in_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] Line (in ray): start=(%.6f, %.6f, %.6f), end=(%.6f, %.6f, %.6f)\n",
                   line_in_out.start[0], line_in_out.start[1], line_in_out.start[2],
                   line_in_out.end[0], line_in_out.end[1], line_in_out.end[2]);
        }
        
        // 4. Project curve onto box (Project Curve)
        ProjectInput proj_in = {
            .curve_type = 1,  // line
            .brep_type = 1,  // box
            .direction = {0.0f, 0.0f, 1.0f}  // Default
        };
        memcpy(proj_in.line_start, line_out_out.start, sizeof(float) * 3);
        memcpy(proj_in.line_end, line_out_out.end, sizeof(float) * 3);
        // Box from direction group (simplified - use plane as box)
        memcpy(proj_in.plane_origin, dir->plane_origin, sizeof(float) * 3);
        memcpy(proj_in.plane_z_axis, dir->plane_z_axis, sizeof(float) * 3);
        ProjectOutput proj_out;
        Project_eval(&proj_in, &proj_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] Project: line_start=(%.6f, %.6f, %.6f), plane_origin=(%.6f, %.6f, %.6f) -> line_start=(%.6f, %.6f, %.6f)\n",
                   proj_in.line_start[0], proj_in.line_start[1], proj_in.line_start[2],
                   proj_in.plane_origin[0], proj_in.plane_origin[1], proj_in.plane_origin[2],
                   proj_out.line_start[0], proj_out.line_start[1], proj_out.line_start[2]);
        }
        
        // 5. PolyLine from projected points
        PolyLineInput poly_in = {
            .vertex_count = 2,
            .closed = 0
        };
        memcpy(poly_in.vertices[0], proj_out.line_start, sizeof(float) * 3);
        memcpy(poly_in.vertices[1], proj_out.line_end, sizeof(float) * 3);
        PolyLineOutput poly_out;
        PolyLine_eval(&poly_in, &poly_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] PolyLine: vertex[0]=(%.6f, %.6f, %.6f), vertex[1]=(%.6f, %.6f, %.6f)\n",
                   poly_out.vertices[0][0], poly_out.vertices[0][1], poly_out.vertices[0][2],
                   poly_out.vertices[1][0], poly_out.vertices[1][1], poly_out.vertices[1][2]);
        }
        
        // 6. Plane Normal from polyline
        PlaneNormalInput pn_in;
        memcpy(pn_in.origin, sun->sun_pt, sizeof(float) * 3);
        memcpy(pn_in.z_axis, poly_out.vertices[0], sizeof(float) * 3);
        PlaneNormalOutput pn_out;
        PlaneNormal_eval(&pn_in, &pn_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] PlaneNormal (pn): origin=(%.6f, %.6f, %.6f), z_axis=(%.6f, %.6f, %.6f) -> x_axis=(%.6f, %.6f, %.6f)\n",
                   pn_in.origin[0], pn_in.origin[1], pn_in.origin[2],
                   pn_in.z_axis[0], pn_in.z_axis[1], pn_in.z_axis[2],
                   pn_out.x_axis[0], pn_out.x_axis[1], pn_out.x_axis[2]);
        }
        
        // 7. Construct Plane
        ConstructPlaneInput cp_in;
        memcpy(cp_in.origin, sun->sun_pt, sizeof(float) * 3);
        memcpy(cp_in.x_axis, poly_out.vertices[0], sizeof(float) * 3);
        // Y-axis from another polyline (reversed)
        PolyLineInput poly_rev_in = {
            .vertex_count = 2,
            .closed = 0
        };
        memcpy(poly_rev_in.vertices[0], proj_out.line_end, sizeof(float) * 3);
        memcpy(poly_rev_in.vertices[1], proj_out.line_start, sizeof(float) * 3);
        PolyLineOutput poly_rev_out;
        PolyLine_eval(&poly_rev_in, &poly_rev_out);
        memcpy(cp_in.y_axis, poly_rev_out.vertices[0], sizeof(float) * 3);
        ConstructPlaneOutput cp_out;
        ConstructPlane_eval(&cp_in, &cp_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] ConstructPlane: x_axis=(%.6f, %.6f, %.6f), y_axis=(%.6f, %.6f, %.6f) -> z_axis=(%.6f, %.6f, %.6f)\n",
                   cp_in.x_axis[0], cp_in.x_axis[1], cp_in.x_axis[2],
                   cp_in.y_axis[0], cp_in.y_axis[1], cp_in.y_axis[2],
                   cp_out.z_axis[0], cp_out.z_axis[1], cp_out.z_axis[2]);
        }
        
        // 8. List Item to get plane normal
        ListItemInput li_in = {
            .list_size = 3,
            .index = 0,
            .wrap = 1
        };
        li_in.list[0] = cp_out.x_axis[0];
        li_in.list[1] = cp_out.y_axis[0];
        li_in.list[2] = cp_out.z_axis[0];
        ListItemOutput li_out;
        ListItem_eval(&li_in, &li_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] ListItem: list[0]=%.6f, list[1]=%.6f, list[2]=%.6f, index=%d -> item=%.6f, valid=%d\n",
                   li_in.list[0], li_in.list[1], li_in.list[2], li_in.index, li_out.item, li_out.valid);
        }
        
        // 9. Plane Normal for angle calculation
        PlaneNormalInput pn2_in;
        memcpy(pn2_in.origin, li_out.item ? sun->sun_pt : targets->target_points[i], sizeof(float) * 3);
        memcpy(pn2_in.z_axis, cp_out.z_axis, sizeof(float) * 3);
        PlaneNormalOutput pn2_out;
        PlaneNormal_eval(&pn2_in, &pn2_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] PlaneNormal (pn2): origin=(%.6f, %.6f, %.6f), z_axis=(%.6f, %.6f, %.6f) -> x_axis=(%.6f, %.6f, %.6f)\n",
                   pn2_in.origin[0], pn2_in.origin[1], pn2_in.origin[2],
                   pn2_in.z_axis[0], pn2_in.z_axis[1], pn2_in.z_axis[2],
                   pn2_out.x_axis[0], pn2_out.x_axis[1], pn2_out.x_axis[2]);
        }
        
        // 10. Circle and Curve|Curve intersection
        YZPlaneInput yz_in;
        memcpy(yz_in.origin, sun->sun_pt, sizeof(float) * 3);
        YZPlaneOutput yz_out;
        YZPlane_eval(&yz_in, &yz_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] YZPlane: origin=(%.6f, %.6f, %.6f) -> z_axis=(%.6f, %.6f, %.6f)\n",
                   yz_in.origin[0], yz_in.origin[1], yz_in.origin[2],
                   yz_out.z_axis[0], yz_out.z_axis[1], yz_out.z_axis[2]);
        }
        
        // Circle radius - use fixed small value like Python (0.1)
        // The circle is used for intersection, not for scaling
        float circle_radius = 0.1f;
        
        CircleInput circle_in = {
            .radius = circle_radius
        };
        memcpy(circle_in.plane_origin, yz_out.origin, sizeof(float) * 3);
        memcpy(circle_in.plane_x_axis, yz_out.x_axis, sizeof(float) * 3);
        memcpy(circle_in.plane_y_axis, yz_out.y_axis, sizeof(float) * 3);
        memcpy(circle_in.plane_z_axis, yz_out.z_axis, sizeof(float) * 3);
        CircleOutput circle_out;
        Circle_eval(&circle_in, &circle_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] Circle: center=(%.6f, %.6f, %.6f), radius=%.6f\n",
                   circle_out.center[0], circle_out.center[1], circle_out.center[2], circle_out.radius);
        }
        
        // Curve|Curve intersection
        CurveCurveInput cc_in = {
            .curve_a_type = 1,  // circle
            .curve_b_type = 0   // line
        };
        memcpy(cc_in.circle_a_center, circle_out.center, sizeof(float) * 3);
        cc_in.circle_a_radius = circle_out.radius;
        memcpy(cc_in.circle_a_x_axis, yz_out.x_axis, sizeof(float) * 3);
        memcpy(cc_in.circle_a_y_axis, yz_out.y_axis, sizeof(float) * 3);
        memcpy(cc_in.circle_a_z_axis, yz_out.z_axis, sizeof(float) * 3);
        memcpy(cc_in.line_b_start, line_in_out.start, sizeof(float) * 3);
        memcpy(cc_in.line_b_end, line_in_out.end, sizeof(float) * 3);
        CurveCurveOutput cc_out;
        CurveCurve_eval(&cc_in, &cc_out);
        if (i == 0) {
            printf("  [DEBUG Slat 0] CurveCurve: circle center=(%.6f, %.6f, %.6f), radius=%.6f, line start=(%.6f, %.6f, %.6f) -> %d points\n",
                   cc_in.circle_a_center[0], cc_in.circle_a_center[1], cc_in.circle_a_center[2],
                   cc_in.circle_a_radius,
                   cc_in.line_b_start[0], cc_in.line_b_start[1], cc_in.line_b_start[2],
                   cc_out.point_count);
        }
        
        
        // 11. Line from intersection points
        // For line-circle intersection, we typically get 1 point (exit point)
        // We need to create a line from the intersection point
        if (cc_out.point_count >= 1) {
            // If we have 2 points, use them; otherwise use the single point and create a short line
            LineInput line_final_in = {
                .use_two_points = 1
            };
            if (cc_out.point_count >= 2) {
                memcpy(line_final_in.start_point, cc_out.points[0], sizeof(float) * 3);
                memcpy(line_final_in.end_point, cc_out.points[1], sizeof(float) * 3);
            } else {
                // Single point - create a short line in the direction of the line
                memcpy(line_final_in.start_point, cc_out.points[0], sizeof(float) * 3);
                // Create end point by extending along the line direction
                float line_dir[3] = {
                    line_in_out.end[0] - line_in_out.start[0],
                    line_in_out.end[1] - line_in_out.start[1],
                    line_in_out.end[2] - line_in_out.start[2]
                };
                float line_len = sqrtf(line_dir[0]*line_dir[0] + line_dir[1]*line_dir[1] + line_dir[2]*line_dir[2]);
                if (line_len > 0.0001f) {
                    float scale = 100.0f / line_len;  // 100 unit extension
                    line_final_in.end_point[0] = cc_out.points[0][0] + line_dir[0] * scale;
                    line_final_in.end_point[1] = cc_out.points[0][1] + line_dir[1] * scale;
                    line_final_in.end_point[2] = cc_out.points[0][2] + line_dir[2] * scale;
                } else {
                    // Fallback: extend in Y direction
                    line_final_in.end_point[0] = cc_out.points[0][0];
                    line_final_in.end_point[1] = cc_out.points[0][1] + 100.0f;
                    line_final_in.end_point[2] = cc_out.points[0][2];
                }
            }
            LineOutput line_final_out;
            Line_eval(&line_final_in, &line_final_out);
            if (i == 0) {
                printf("  [DEBUG Slat 0] Line (final): start=(%.6f, %.6f, %.6f), end=(%.6f, %.6f, %.6f)\n",
                       line_final_out.start[0], line_final_out.start[1], line_final_out.start[2],
                       line_final_out.end[0], line_final_out.end[1], line_final_out.end[2]);
            }
            
            // 12. Angle calculation
            AngleInput angle_in = {
                .use_oriented = 0
            };
            // Vector A from List Item
            memcpy(angle_in.vector_a, pn2_out.x_axis, sizeof(float) * 3);
            // Vector B from final line
            float vec_b[3] = {
                line_final_out.end[0] - line_final_out.start[0],
                line_final_out.end[1] - line_final_out.start[1],
                line_final_out.end[2] - line_final_out.start[2]
            };
            float len_b = sqrtf(vec_b[0] * vec_b[0] + vec_b[1] * vec_b[1] + vec_b[2] * vec_b[2]);
            if (len_b > 0.0001f) {
                angle_in.vector_b[0] = vec_b[0] / len_b;
                angle_in.vector_b[1] = vec_b[1] / len_b;
                angle_in.vector_b[2] = vec_b[2] / len_b;
            } else {
                angle_in.vector_b[0] = 0.0f;
                angle_in.vector_b[1] = 0.0f;
                angle_in.vector_b[2] = 1.0f;
            }
            memcpy(angle_in.plane_normal, pn2_out.z_axis, sizeof(float) * 3);
            AngleOutput angle_out;
            Angle_eval(&angle_in, &angle_out);
            if (i == 0) {
                printf("  [DEBUG Slat 0] Angle: vector_a=(%.6f, %.6f, %.6f), vector_b=(%.6f, %.6f, %.6f) -> angle=%.6f rad\n",
                       angle_in.vector_a[0], angle_in.vector_a[1], angle_in.vector_a[2],
                       angle_in.vector_b[0], angle_in.vector_b[1], angle_in.vector_b[2],
                       angle_out.angle);
            }
            
            // 13. Convert to degrees
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
            // Debug output for first slat
            if (i == 0) {
                printf("  [DEBUG Slat 0] No intersection found (point_count=%d, expected >=1)\n", cc_out.point_count);
            }
        }
    }
}

