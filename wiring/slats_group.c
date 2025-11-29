#include "slats_group.h"
#include "../c_components/Rectangle2Pt.h"
#include "../c_components/Move.h"
#include "../c_components/Series.h"
#include "../c_components/UnitY.h"
#include "../c_components/UnitZ.h"
#include "../c_components/Vector2Pt.h"
#include "../c_components/ConstructPoint.h"
#include "../c_components/Box2Pt.h"
#include "../c_components/Negative.h"
#include "../c_components/Division.h"
#include "../c_components/Subtraction.h"
#include "../c_components/Rotate.h"
#include <string.h>
#include <math.h>
#include <stdio.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

void slats_group_eval(const ShadeConfig *cfg, SlatsGroupOutput *out) {
    // Initialize output
    out->slat_count = cfg->number_of_slats;
    
    // 1. Calculate room half-width
    DivisionInput div_room_in = {
        .a = cfg->room_width,
        .b = 2.0f
    };
    DivisionOutput div_room_out;
    Division_eval(&div_room_in, &div_room_out);
    printf("  [DEBUG] Division (room): %.6f / %.6f = %.6f\n", div_room_in.a, div_room_in.b, div_room_out.result);
    
    // 2. Calculate slat half-width
    DivisionInput div_slat_in = {
        .a = cfg->slat_width,
        .b = 2.0f
    };
    DivisionOutput div_slat_out;
    Division_eval(&div_slat_in, &div_slat_out);
    printf("  [DEBUG] Division (slat): %.6f / %.6f = %.6f\n", div_slat_in.a, div_slat_in.b, div_slat_out.result);
    
    // 3. Create negative values for point construction
    NegativeInput neg_x_in = { .value = div_room_out.result };
    NegativeOutput neg_x_out;
    Negative_eval(&neg_x_in, &neg_x_out);
    printf("  [DEBUG] Negative (x): -%.6f = %.6f\n", neg_x_in.value, neg_x_out.result);
    
    NegativeInput neg_y_in = { .value = div_slat_out.result };
    NegativeOutput neg_y_out;
    Negative_eval(&neg_y_in, &neg_y_out);
    printf("  [DEBUG] Negative (y): -%.6f = %.6f\n", neg_y_in.value, neg_y_out.result);
    
    // 4. Construct points for rectangle
    ConstructPointInput cp1_in = {
        .x = neg_x_out.result,
        .y = neg_y_out.result,
        .z = 0.0f
    };
    ConstructPointOutput cp1_out;
    ConstructPoint_eval(&cp1_in, &cp1_out);
    printf("  [DEBUG] ConstructPoint (cp1): (%.6f, %.6f, %.6f) -> (%.6f, %.6f, %.6f)\n",
           cp1_in.x, cp1_in.y, cp1_in.z, cp1_out.point[0], cp1_out.point[1], cp1_out.point[2]);
    
    ConstructPointInput cp2_in = {
        .x = div_room_out.result,
        .y = div_slat_out.result,
        .z = 0.0f
    };
    ConstructPointOutput cp2_out;
    ConstructPoint_eval(&cp2_in, &cp2_out);
    printf("  [DEBUG] ConstructPoint (cp2): (%.6f, %.6f, %.6f) -> (%.6f, %.6f, %.6f)\n",
           cp2_in.x, cp2_in.y, cp2_in.z, cp2_out.point[0], cp2_out.point[1], cp2_out.point[2]);
    
    // 5. Create rectangle
    Rectangle2PtInput rect_in = {
        .plane_origin = {0.0f, 0.0f, 0.0f},
        .plane_x_axis = {1.0f, 0.0f, 0.0f},
        .plane_y_axis = {0.0f, 1.0f, 0.0f},
        .plane_z_axis = {0.0f, 0.0f, 1.0f}
    };
    memcpy(rect_in.point_a, cp1_out.point, sizeof(float) * 3);
    memcpy(rect_in.point_b, cp2_out.point, sizeof(float) * 3);
    Rectangle2PtOutput rect_out;
    Rectangle2Pt_eval(&rect_in, &rect_out);
    printf("  [DEBUG] Rectangle2Pt: corners[0]=(%.6f, %.6f, %.6f), corners[1]=(%.6f, %.6f, %.6f)\n",
           rect_out.corners[0][0], rect_out.corners[0][1], rect_out.corners[0][2],
           rect_out.corners[1][0], rect_out.corners[1][1], rect_out.corners[1][2]);
    
    // 6. Series for slat positioning
    // Calculate step for series
    SubtractionInput sub_height_in = {
        .a = cfg->slats_height_top,
        .b = cfg->slats_height_threshold
    };
    SubtractionOutput sub_height_out;
    Subtraction_eval(&sub_height_in, &sub_height_out);
    printf("  [DEBUG] Subtraction (height): %.6f - %.6f = %.6f\n", sub_height_in.a, sub_height_in.b, sub_height_out.result);
    
    SubtractionInput sub_count_in = {
        .a = (float)cfg->number_of_slats,
        .b = 1.0f
    };
    SubtractionOutput sub_count_out;
    Subtraction_eval(&sub_count_in, &sub_count_out);
    printf("  [DEBUG] Subtraction (count): %.6f - %.6f = %.6f\n", sub_count_in.a, sub_count_in.b, sub_count_out.result);
    
    DivisionInput div_step_in = {
        .a = sub_height_out.result,
        .b = sub_count_out.result
    };
    DivisionOutput div_step_out;
    Division_eval(&div_step_in, &div_step_out);
    printf("  [DEBUG] Division (step): %.6f / %.6f = %.6f\n", div_step_in.a, div_step_in.b, div_step_out.result);
    
    // Series for Y positions
    NegativeInput neg_start_in = { .value = cfg->slats_height_top };
    NegativeOutput neg_start_out;
    Negative_eval(&neg_start_in, &neg_start_out);
    printf("  [DEBUG] Negative (start): -%.6f = %.6f\n", neg_start_in.value, neg_start_out.result);
    
    SeriesInput series_in = {
        .start = neg_start_out.result,
        .step = div_step_out.result,
        .count = cfg->number_of_slats
    };
    SeriesOutput series_out;
    Series_eval(&series_in, &series_out);
    printf("  [DEBUG] Series: start=%.6f, step=%.6f, count=%d -> first=%.6f, last=%.6f\n",
           series_in.start, series_in.step, series_in.count,
           series_out.series[0], series_out.series[series_out.actual_count-1]);
    
    // 7. Unit vectors
    // Negative of horizontal_shift_between_slats
    NegativeInput neg_shift_in = { .value = cfg->horizontal_shift_between_slats };
    NegativeOutput neg_shift_out;
    Negative_eval(&neg_shift_in, &neg_shift_out);
    printf("  [DEBUG] Negative (horizontal_shift): -%.6f = %.6f\n", neg_shift_in.value, neg_shift_out.result);
    
    // Series from negative horizontal_shift
    SeriesInput series_shift_in = {
        .start = cfg->distance_from_window,
        .step = neg_shift_out.result,
        .count = cfg->number_of_slats
    };
    SeriesOutput series_shift_out;
    Series_eval(&series_shift_in, &series_shift_out);
    printf("  [DEBUG] Series (horizontal_shift): start=%.6f, step=%.6f, count=%d -> first=%.6f, last=%.6f\n",
           series_shift_in.start, series_shift_in.step, series_shift_in.count,
           series_shift_out.series[0], series_shift_out.series[series_shift_out.actual_count-1]);
    
    // Negative of series_out (slat positioning series) for UnitZ
    NegativeInput neg_z_factor_in = {
        .value = 0.0f,  // Not used when value_count > 0
        .value_count = series_out.actual_count
    };
    // Copy series values to negative input
    for (int i = 0; i < series_out.actual_count && i < NEGATIVE_MAX_COUNT; i++) {
        neg_z_factor_in.values[i] = series_out.series[i];
    }
    NegativeOutput neg_z_factor_out = {0};  // Initialize to zero
    Negative_eval(&neg_z_factor_in, &neg_z_factor_out);
    printf("  [DEBUG] Negative (z factor from series_out): input_count=%d, result_count=%d\n",
           neg_z_factor_in.value_count, neg_z_factor_out.result_count);
    if (neg_z_factor_out.result_count > 0) {
        printf("    First: %.6f -> %.6f, Last: %.6f -> %.6f\n",
               series_out.series[0], neg_z_factor_out.results[0],
               series_out.series[neg_z_factor_out.result_count-1], 
               neg_z_factor_out.results[neg_z_factor_out.result_count-1]);
    }
    
    // Use negated values for UnitZ factor (pass entire list)
    UnitZInput unitz_in = {
        .factor = 0.0f,  // Not used when factor_count > 0
        .factor_count = neg_z_factor_out.result_count
    };
    // Copy negated values to UnitZ input
    for (int i = 0; i < neg_z_factor_out.result_count && i < UNITZ_MAX_COUNT; i++) {
        unitz_in.factors[i] = neg_z_factor_out.results[i];
    }
    UnitZOutput unitz_out;
    UnitZ_eval(&unitz_in, &unitz_out);
    printf("  [DEBUG] UnitZ: input factor_count=%d, output vector_count=%d\n",
           unitz_in.factor_count, unitz_out.vector_count);
    if (unitz_out.vector_count > 0) {
        printf("    First: factor=%.6f -> vector=(%.6f, %.6f, %.6f)\n",
               unitz_in.factors[0],
               unitz_out.unit_vectors[0][0], unitz_out.unit_vectors[0][1], unitz_out.unit_vectors[0][2]);
        if (unitz_out.vector_count > 1) {
            int last_idx = unitz_out.vector_count - 1;
            printf("    Last: factor=%.6f -> vector=(%.6f, %.6f, %.6f)\n",
                   unitz_in.factors[last_idx],
                   unitz_out.unit_vectors[last_idx][0], unitz_out.unit_vectors[last_idx][1], unitz_out.unit_vectors[last_idx][2]);
        }
    }
    
    // Series for Unit Y (uses distance_from_window as start, same step calculation as slat positioning)
    SeriesInput series_y_in = {
        .start = cfg->distance_from_window,
        .step = neg_shift_out.result,  // Use the same step as the slat positioning series
        .count = cfg->number_of_slats
    };
    SeriesOutput series_y_out;
    Series_eval(&series_y_in, &series_y_out);
    printf("  [DEBUG] Series (y): start=%.6f, step=%.6f, count=%d -> first=%.6f, last=%.6f\n",
           series_y_in.start, series_y_in.step, series_y_in.count,
           series_y_out.series[0], series_y_out.series[series_y_out.actual_count-1]);
    
    // Unit Y uses series output (pass entire list)
    UnitYInput unity_in = {
        .factor = 0.0f,  // Not used when factor_count > 0
        .factor_count = series_y_out.actual_count
    };
    // Copy series values to UnitY input
    for (int i = 0; i < series_y_out.actual_count && i < UNITY_MAX_COUNT; i++) {
        unity_in.factors[i] = series_y_out.series[i];
    }
    UnitYOutput unity_out;
    UnitY_eval(&unity_in, &unity_out);
    printf("  [DEBUG] UnitY: input factor_count=%d, output vector_count=%d\n",
           unity_in.factor_count, unity_out.vector_count);
    if (unity_out.vector_count > 0) {
        printf("    First: factor=%.6f -> vector=(%.6f, %.6f, %.6f)\n",
               unity_in.factors[0],
               unity_out.unit_vectors[0][0], unity_out.unit_vectors[0][1], unity_out.unit_vectors[0][2]);
        if (unity_out.vector_count > 1) {
            int last_idx = unity_out.vector_count - 1;
            printf("    Last: factor=%.6f -> vector=(%.6f, %.6f, %.6f)\n",
                   unity_in.factors[last_idx],
                   unity_out.unit_vectors[last_idx][0], unity_out.unit_vectors[last_idx][1], unity_out.unit_vectors[last_idx][2]);
        }
    }
    
    // 8. Vector 2Pt for motion (pass lists from UnitY and UnitZ)
    // Match the counts - use the minimum of both
    int vec_count = (unity_out.vector_count < unitz_out.vector_count) ? 
                    unity_out.vector_count : unitz_out.vector_count;
    if (vec_count == 0) {
        vec_count = 1;  // Fallback to single mode
    }
    
    Vector2PtInput vec_in = {
        .unitize = 0,
        .point_count = (vec_count > 1) ? vec_count : 0  // Use array mode if count > 1
    };
    
    if (vec_in.point_count > 0) {
        // Copy arrays from UnitY and UnitZ outputs
        for (int i = 0; i < vec_count && i < VECTOR2PT_MAX_COUNT; i++) {
            memcpy(vec_in.points_a[i], unity_out.unit_vectors[i], sizeof(float) * 3);
            memcpy(vec_in.points_b[i], unitz_out.unit_vectors[i], sizeof(float) * 3);
        }
    } else {
        // Single point mode (backward compatibility)
        memcpy(vec_in.point_a, unity_out.unit_vector, sizeof(float) * 3);
        memcpy(vec_in.point_b, unitz_out.unit_vector, sizeof(float) * 3);
    }
    
    Vector2PtOutput vec_out;
    Vector2Pt_eval(&vec_in, &vec_out);
    printf("  [DEBUG] Vector2Pt: input point_count=%d, output vector_count=%d\n",
           vec_in.point_count, vec_out.vector_count);
    if (vec_out.vector_count > 0) {
        printf("    First: point_a=(%.6f, %.6f, %.6f), point_b=(%.6f, %.6f, %.6f) -> vector=(%.6f, %.6f, %.6f)\n",
               vec_in.points_a[0][0], vec_in.points_a[0][1], vec_in.points_a[0][2],
               vec_in.points_b[0][0], vec_in.points_b[0][1], vec_in.points_b[0][2],
               vec_out.vectors[0][0], vec_out.vectors[0][1], vec_out.vectors[0][2]);
        if (vec_out.vector_count > 1) {
            int last_idx = vec_out.vector_count - 1;
            printf("    Last: point_a=(%.6f, %.6f, %.6f), point_b=(%.6f, %.6f, %.6f) -> vector=(%.6f, %.6f, %.6f)\n",
                   vec_in.points_a[last_idx][0], vec_in.points_a[last_idx][1], vec_in.points_a[last_idx][2],
                   vec_in.points_b[last_idx][0], vec_in.points_b[last_idx][1], vec_in.points_b[last_idx][2],
                   vec_out.vectors[last_idx][0], vec_out.vectors[last_idx][1], vec_out.vectors[last_idx][2]);
        }
    } else {
        printf("    Single: point_a=(%.6f, %.6f, %.6f), point_b=(%.6f, %.6f, %.6f) -> vector=(%.6f, %.6f, %.6f)\n",
               vec_in.point_a[0], vec_in.point_a[1], vec_in.point_a[2],
               vec_in.point_b[0], vec_in.point_b[1], vec_in.point_b[2],
               vec_out.vector[0], vec_out.vector[1], vec_out.vector[2]);
    }
    
    // 9. Move rectangle (Slats original) - list mode: move base rectangle by each vector
    int move_count = vec_out.vector_count;
    if (move_count > cfg->number_of_slats) {
        move_count = cfg->number_of_slats;
    }
    if (move_count > MAX_SLATS) {
        move_count = MAX_SLATS;
    }

    MoveInput move_in;
    memset(&move_in, 0, sizeof(MoveInput));
    move_in.geometry_type = 2;  // rectangle
    move_in.rectangle_count = move_count;
    
    // Copy base rectangle to all positions, and corresponding motion vectors
    for (int i = 0; i < move_count; ++i) {
        memcpy(move_in.rectangles[i], rect_out.corners, sizeof(float) * 4 * 3);
        if (i < vec_out.vector_count) {
            memcpy(move_in.motions[i], vec_out.vectors[i], sizeof(float) * 3);
        } else {
            memcpy(move_in.motions[i], vec_out.vector, sizeof(float) * 3);
        }
    }

    MoveOutput move_out;
    Move_eval(&move_in, &move_out);
    printf("  [DEBUG] Move: rectangle_count=%d, first motion=(%.6f, %.6f, %.6f) -> corner[0]=(%.6f, %.6f, %.6f)\n",
           move_out.rectangle_count,
           move_in.motions[0][0], move_in.motions[0][1], move_in.motions[0][2],
           move_out.rectangles[0][0][0], move_out.rectangles[0][0][1], move_out.rectangles[0][0][2]);
    
    // 10. Rotate slats (orientation) - list mode: rotate all moved rectangles
    float orientation_rad = cfg->orientation_deg * M_PI / 180.0f;
    RotateInput rotate_in;
    memset(&rotate_in, 0, sizeof(RotateInput));
    rotate_in.geometry_type = 2;  // rectangle
    rotate_in.angle = orientation_rad;
    rotate_in.rot_origin[0] = 0.0f;
    rotate_in.rot_origin[1] = 0.0f;
    rotate_in.rot_origin[2] = 0.0f;
    rotate_in.rot_axis[0] = 0.0f;
    rotate_in.rot_axis[1] = 0.0f;
    rotate_in.rot_axis[2] = 1.0f;
    rotate_in.rectangle_count = move_out.rectangle_count;
    
    for (int i = 0; i < move_out.rectangle_count; ++i) {
        memcpy(rotate_in.rectangles[i], move_out.rectangles[i], sizeof(float) * 4 * 3);
    }

    RotateOutput rotate_out;
    Rotate_eval(&rotate_in, &rotate_out);
    printf("  [DEBUG] Rotate: rectangle_count=%d, angle=%.6f rad (%.6f deg) -> corner[0]=(%.6f, %.6f, %.6f)\n",
           rotate_out.rectangle_count, rotate_in.angle, cfg->orientation_deg,
           rotate_out.rectangles[0][0][0], rotate_out.rectangles[0][0][1], rotate_out.rectangles[0][0][2]);
    
    // Store output - copy all rotated rectangles
    int store_count = rotate_out.rectangle_count;
    if (store_count > cfg->number_of_slats) {
        store_count = cfg->number_of_slats;
    }
    if (store_count > MAX_SLATS) {
        store_count = MAX_SLATS;
    }
    for (int i = 0; i < store_count; ++i) {
        memcpy(out->slat_rectangles[i], rotate_out.rectangles[i], sizeof(float) * 4 * 3);
    }
    out->slat_count = store_count;
}

