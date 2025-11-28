// Derived from evaluate_rotate in gh_components_stripped.py

#include "Rotate.h"
#include <math.h>

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

static void rotate_point_around_axis(const float pt[3], const float rot_origin[3],
                                     const float rot_axis_norm[3], float angle,
                                     float out[3]) {
    // Translate to origin
    float px = pt[0] - rot_origin[0];
    float py = pt[1] - rot_origin[1];
    float pz = pt[2] - rot_origin[2];
    
    // Rodrigues' rotation formula
    float ax = rot_axis_norm[0];
    float ay = rot_axis_norm[1];
    float az = rot_axis_norm[2];
    float dot = px*ax + py*ay + pz*az;
    float cross[3] = {
        py*az - pz*ay,
        pz*ax - px*az,
        px*ay - py*ax
    };
    
    float cos_a = cosf(angle);
    float sin_a = sinf(angle);
    
    float rotated[3] = {
        px * cos_a + cross[0] * sin_a + ax * dot * (1.0f - cos_a),
        py * cos_a + cross[1] * sin_a + ay * dot * (1.0f - cos_a),
        pz * cos_a + cross[2] * sin_a + az * dot * (1.0f - cos_a)
    };
    
    // Translate back
    out[0] = rotated[0] + rot_origin[0];
    out[1] = rotated[1] + rot_origin[1];
    out[2] = rotated[2] + rot_origin[2];
}

static void rotate_vec_around_axis(const float vec[3], const float rot_axis_norm[3],
                                   float angle, float out[3]) {
    // Rotate direction vector around rot_axis_norm (no translation)
    float ax = rot_axis_norm[0];
    float ay = rot_axis_norm[1];
    float az = rot_axis_norm[2];
    float vx = vec[0];
    float vy = vec[1];
    float vz = vec[2];
    float dot = vx*ax + vy*ay + vz*az;
    float cross[3] = {
        vy*az - vz*ay,
        vz*ax - vx*az,
        vx*ay - vy*ax
    };
    
    float cos_a = cosf(angle);
    float sin_a = sinf(angle);
    
    out[0] = vx * cos_a + cross[0] * sin_a + ax * dot * (1.0f - cos_a);
    out[1] = vy * cos_a + cross[1] * sin_a + ay * dot * (1.0f - cos_a);
    out[2] = vz * cos_a + cross[2] * sin_a + az * dot * (1.0f - cos_a);
}

void Rotate_eval(const RotateInput *in, RotateOutput *out) {
    // GH Rotate: rotate geometry around plane's Z-axis at plane's origin
    out->geometry_type = in->geometry_type;
    
    float rot_axis_norm[3];
    normalize_vec(in->rot_axis, rot_axis_norm);
    
    if (in->geometry_type == 0) {
        // Point
        rotate_point_around_axis(in->point, in->rot_origin, rot_axis_norm, in->angle, out->point);
    } else if (in->geometry_type == 1) {
        // Line
        rotate_point_around_axis(in->line_start, in->rot_origin, rot_axis_norm, in->angle, out->line_start);
        rotate_point_around_axis(in->line_end, in->rot_origin, rot_axis_norm, in->angle, out->line_end);
    } else if (in->geometry_type == 2) {
        // Rectangle
        for (int i = 0; i < 4; i++) {
            rotate_point_around_axis(in->rectangle_corners[i], in->rot_origin, rot_axis_norm, in->angle, out->rectangle_corners[i]);
        }
    } else if (in->geometry_type == 3) {
        // Box
        rotate_point_around_axis(in->box_corner_a, in->rot_origin, rot_axis_norm, in->angle, out->box_corner_a);
        rotate_point_around_axis(in->box_corner_b, in->rot_origin, rot_axis_norm, in->angle, out->box_corner_b);
    } else if (in->geometry_type == 4) {
        // Plane: rotate origin and axes around rotation plane's Z/normal
        rotate_point_around_axis(in->plane_origin, in->rot_origin, rot_axis_norm, in->angle, out->plane_origin);
        
        float x_rot[3], y_rot[3], z_rot[3];
        rotate_vec_around_axis(in->plane_x_axis, rot_axis_norm, in->angle, x_rot);
        rotate_vec_around_axis(in->plane_y_axis, rot_axis_norm, in->angle, y_rot);
        rotate_vec_around_axis(in->plane_z_axis, rot_axis_norm, in->angle, z_rot);
        
        normalize_vec(x_rot, out->plane_x_axis);
        normalize_vec(y_rot, out->plane_y_axis);
        normalize_vec(z_rot, out->plane_z_axis);
    }
}

