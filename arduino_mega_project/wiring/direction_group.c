#include "direction_group.h"
#include "../c_components/ConstructPoint.h"
#include "../c_components/Box2Pt.h"
#include "../c_components/Rotate.h"
#include "../c_components/Area.h"
#include "../c_components/YZPlane.h"
#include <string.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

void direction_group_eval(const ShadeConfig *cfg, const SlatsGroupOutput *slats, DirectionGroupOutput *out) {
    // 1. Construct Point p1 (first point: 0, -2, 7)
    ConstructPointInput cp1_in = { .x = 0.0f, .y = -2.0f, .z = 7.0f };
    ConstructPointOutput cp1_out;
    ConstructPoint_eval(&cp1_in, &cp1_out);
    
    // 2. Construct Point p1 (second point: 0, 3, -3)
    ConstructPointInput cp2_in = { .x = 0.0f, .y = 3.0f, .z = -3.0f };
    ConstructPointOutput cp2_out;
    ConstructPoint_eval(&cp2_in, &cp2_out);
    
    // 3. Box 2Pt
    Box2PtInput box_in = {
        .plane_origin = {0.0f, 0.0f, 0.0f},
        .plane_x_axis = {1.0f, 0.0f, 0.0f},
        .plane_y_axis = {0.0f, 1.0f, 0.0f},
        .plane_z_axis = {0.0f, 0.0f, 1.0f}
    };
    memcpy(box_in.point_a, cp1_out.point, sizeof(float) * 3);
    memcpy(box_in.point_b, cp2_out.point, sizeof(float) * 3);
    Box2PtOutput box_out;
    Box2Pt_eval(&box_in, &box_out);
    
    // 4. Rotate box
    float orientation_rad = cfg->orientation_deg * M_PI / 180.0f;
    RotateInput rotate_box_in = {
        .geometry_type = 3,
        .angle = orientation_rad,
        .rot_origin = {0.0f, 0.0f, 0.0f},
        .rot_axis = {0.0f, 0.0f, 1.0f}
    };
    memcpy(rotate_box_in.box_corner_a, box_out.corner_a, sizeof(float) * 3);
    memcpy(rotate_box_in.box_corner_b, box_out.corner_b, sizeof(float) * 3);
    RotateOutput rotate_box_out;
    Rotate_eval(&rotate_box_in, &rotate_box_out);
    
    // 5. Area - get centroid
    AreaInput area_in = { .geometry_type = 3 };
    memcpy(area_in.box_corner_a, rotate_box_out.box_corner_a, sizeof(float) * 3);
    memcpy(area_in.box_corner_b, rotate_box_out.box_corner_b, sizeof(float) * 3);
    AreaOutput area_out;
    Area_eval(&area_in, &area_out);
    
    // 6. YZ Plane at centroid
    YZPlaneInput yz_in;
    memcpy(yz_in.origin, area_out.centroid, sizeof(float) * 3);
    YZPlaneOutput yz_out;
    YZPlane_eval(&yz_in, &yz_out);
    
    // 7. Rotate plane
    RotateInput rotate_plane_in = {
        .geometry_type = 4,
        .angle = orientation_rad,
        .rot_origin = {0.0f, 0.0f, 0.0f},
        .rot_axis = {0.0f, 0.0f, 1.0f}
    };
    memcpy(rotate_plane_in.plane_origin, yz_out.origin, sizeof(float) * 3);
    memcpy(rotate_plane_in.plane_x_axis, yz_out.x_axis, sizeof(float) * 3);
    memcpy(rotate_plane_in.plane_y_axis, yz_out.y_axis, sizeof(float) * 3);
    memcpy(rotate_plane_in.plane_z_axis, yz_out.z_axis, sizeof(float) * 3);
    RotateOutput rotate_plane_out;
    Rotate_eval(&rotate_plane_in, &rotate_plane_out);
    
    // Copy output
    memcpy(out->plane_origin, rotate_plane_out.plane_origin, sizeof(float) * 3);
    memcpy(out->plane_x_axis, rotate_plane_out.plane_x_axis, sizeof(float) * 3);
    memcpy(out->plane_y_axis, rotate_plane_out.plane_y_axis, sizeof(float) * 3);
    memcpy(out->plane_z_axis, rotate_plane_out.plane_z_axis, sizeof(float) * 3);
}

