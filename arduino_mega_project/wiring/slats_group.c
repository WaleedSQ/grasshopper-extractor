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

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

void slats_group_eval(const ShadeConfig *cfg, SlatsGroupOutput *out) {
    out->slat_count = cfg->number_of_slats;
    
    // 1. Calculate room half-width
    DivisionInput div_room_in = { .a = cfg->room_width, .b = 2.0f };
    DivisionOutput div_room_out;
    Division_eval(&div_room_in, &div_room_out);
    
    // 2. Calculate slat half-width
    DivisionInput div_slat_in = { .a = cfg->slat_width, .b = 2.0f };
    DivisionOutput div_slat_out;
    Division_eval(&div_slat_in, &div_slat_out);
    
    // 3. Create negative values
    NegativeInput neg_x_in = { .value = div_room_out.result };
    NegativeOutput neg_x_out;
    Negative_eval(&neg_x_in, &neg_x_out);
    
    NegativeInput neg_y_in = { .value = div_slat_out.result };
    NegativeOutput neg_y_out;
    Negative_eval(&neg_y_in, &neg_y_out);
    
    // 4. Construct points for rectangle
    ConstructPointInput cp1_in = {
        .x = neg_x_out.result, .y = neg_y_out.result, .z = 0.0f
    };
    ConstructPointOutput cp1_out;
    ConstructPoint_eval(&cp1_in, &cp1_out);
    
    ConstructPointInput cp2_in = {
        .x = div_room_out.result, .y = div_slat_out.result, .z = 0.0f
    };
    ConstructPointOutput cp2_out;
    ConstructPoint_eval(&cp2_in, &cp2_out);
    
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
    
    // 6. Series for slat positioning
    SubtractionInput sub_height_in = {
        .a = cfg->slats_height_top, .b = cfg->slats_height_threshold
    };
    SubtractionOutput sub_height_out;
    Subtraction_eval(&sub_height_in, &sub_height_out);
    
    SubtractionInput sub_count_in = {
        .a = (float)cfg->number_of_slats, .b = 1.0f
    };
    SubtractionOutput sub_count_out;
    Subtraction_eval(&sub_count_in, &sub_count_out);
    
    DivisionInput div_step_in = {
        .a = sub_height_out.result, .b = sub_count_out.result
    };
    DivisionOutput div_step_out;
    Division_eval(&div_step_in, &div_step_out);
    
    NegativeInput neg_start_in = { .value = cfg->slats_height_top };
    NegativeOutput neg_start_out;
    Negative_eval(&neg_start_in, &neg_start_out);
    
    SeriesInput series_in = {
        .start = neg_start_out.result,
        .step = div_step_out.result,
        .count = cfg->number_of_slats
    };
    SeriesOutput series_out;
    Series_eval(&series_in, &series_out);
    
    // 7. Unit vectors
    NegativeInput neg_shift_in = { .value = cfg->horizontal_shift_between_slats };
    NegativeOutput neg_shift_out;
    Negative_eval(&neg_shift_in, &neg_shift_out);
    
    SeriesInput series_shift_in = {
        .start = cfg->distance_from_window,
        .step = neg_shift_out.result,
        .count = cfg->number_of_slats
    };
    SeriesOutput series_shift_out;
    Series_eval(&series_shift_in, &series_shift_out);
    
    // Negative of series_out for UnitZ
    NegativeInput neg_z_factor_in = {
        .value = 0.0f,
        .value_count = series_out.actual_count
    };
    for (int i = 0; i < series_out.actual_count && i < NEGATIVE_MAX_COUNT; i++) {
        neg_z_factor_in.values[i] = series_out.series[i];
    }
    NegativeOutput neg_z_factor_out = {0};
    Negative_eval(&neg_z_factor_in, &neg_z_factor_out);
    
    // UnitZ
    UnitZInput unitz_in = {
        .factor = 0.0f,
        .factor_count = neg_z_factor_out.result_count
    };
    for (int i = 0; i < neg_z_factor_out.result_count && i < UNITZ_MAX_COUNT; i++) {
        unitz_in.factors[i] = neg_z_factor_out.results[i];
    }
    UnitZOutput unitz_out;
    UnitZ_eval(&unitz_in, &unitz_out);
    
    // Series for Unit Y
    SeriesInput series_y_in = {
        .start = cfg->distance_from_window,
        .step = neg_shift_out.result,
        .count = cfg->number_of_slats
    };
    SeriesOutput series_y_out;
    Series_eval(&series_y_in, &series_y_out);
    
    // UnitY
    UnitYInput unity_in = {
        .factor = 0.0f,
        .factor_count = series_y_out.actual_count
    };
    for (int i = 0; i < series_y_out.actual_count && i < UNITY_MAX_COUNT; i++) {
        unity_in.factors[i] = series_y_out.series[i];
    }
    UnitYOutput unity_out;
    UnitY_eval(&unity_in, &unity_out);
    
    // 8. Vector 2Pt for motion
    int vec_count = (unity_out.vector_count < unitz_out.vector_count) ? 
                    unity_out.vector_count : unitz_out.vector_count;
    if (vec_count == 0) vec_count = 1;
    
    Vector2PtInput vec_in = {
        .unitize = 0,
        .point_count = (vec_count > 1) ? vec_count : 0
    };
    
    if (vec_in.point_count > 0) {
        for (int i = 0; i < vec_count && i < VECTOR2PT_MAX_COUNT; i++) {
            memcpy(vec_in.points_a[i], unity_out.unit_vectors[i], sizeof(float) * 3);
            memcpy(vec_in.points_b[i], unitz_out.unit_vectors[i], sizeof(float) * 3);
        }
    } else {
        memcpy(vec_in.point_a, unity_out.unit_vector, sizeof(float) * 3);
        memcpy(vec_in.point_b, unitz_out.unit_vector, sizeof(float) * 3);
    }
    
    Vector2PtOutput vec_out;
    Vector2Pt_eval(&vec_in, &vec_out);
    
    // 9. Move rectangle
    int move_count = vec_out.vector_count;
    if (move_count > cfg->number_of_slats) move_count = cfg->number_of_slats;
    if (move_count > MAX_SLATS) move_count = MAX_SLATS;

    MoveInput move_in;
    memset(&move_in, 0, sizeof(MoveInput));
    move_in.geometry_type = 2;
    move_in.rectangle_count = move_count;
    
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
    
    // 10. Rotate slats
    float orientation_rad = cfg->orientation_deg * M_PI / 180.0f;
    RotateInput rotate_in;
    memset(&rotate_in, 0, sizeof(RotateInput));
    rotate_in.geometry_type = 2;
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
    
    // Store output
    int store_count = rotate_out.rectangle_count;
    if (store_count > cfg->number_of_slats) store_count = cfg->number_of_slats;
    if (store_count > MAX_SLATS) store_count = MAX_SLATS;
    for (int i = 0; i < store_count; ++i) {
        memcpy(out->slat_rectangles[i], rotate_out.rectangles[i], sizeof(float) * 4 * 3);
    }
    out->slat_count = store_count;
}

