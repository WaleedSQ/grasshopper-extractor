#include "targets_group.h"
#include "../c_components/ConstructPoint.h"
#include "../c_components/Series.h"
#include "../c_components/Negative.h"
#include "../c_components/UnitY.h"
#include "../c_components/Move.h"
#include "../c_components/Subtraction.h"
#include "../c_components/Division.h"
#include <string.h>
#include <math.h>

void targets_group_eval(const ShadeConfig *cfg, TargetsGroupOutput *out) {
    // Calculate target spacing
    SubtractionInput sub_dist_in = {
        .a = cfg->last_target_from_slats,
        .b = cfg->first_target_from_slats
    };
    SubtractionOutput sub_dist_out;
    Subtraction_eval(&sub_dist_in, &sub_dist_out);
    
    SubtractionInput sub_count_in = {
        .a = (float)cfg->number_of_slats,
        .b = 1.0f
    };
    SubtractionOutput sub_count_out;
    Subtraction_eval(&sub_count_in, &sub_count_out);
    
    DivisionInput div_step_in = {
        .a = sub_dist_out.result,
        .b = sub_count_out.result
    };
    DivisionOutput div_step_out;
    Division_eval(&div_step_in, &div_step_out);
    
    // Series for target distances
    SeriesInput series_in = {
        .start = 0.0f,
        .step = div_step_out.result,
        .count = cfg->number_of_slats
    };
    SeriesOutput series_out;
    Series_eval(&series_in, &series_out);
    
    // Negative - negate the entire series
    NegativeInput neg_in = {
        .value = 0.0f,
        .value_count = series_out.actual_count
    };
    for (int i = 0; i < series_out.actual_count && i < NEGATIVE_MAX_COUNT; i++) {
        neg_in.values[i] = series_out.series[i];
    }
    NegativeOutput neg_out = {0};
    Negative_eval(&neg_in, &neg_out);
    
    // UnitY - use negated values as factors
    UnitYInput unity_in = {
        .factor = 0.0f,
        .factor_count = neg_out.result_count
    };
    for (int i = 0; i < neg_out.result_count && i < UNITY_MAX_COUNT; i++) {
        unity_in.factors[i] = neg_out.results[i];
    }
    UnitYOutput unity_out;
    UnitY_eval(&unity_in, &unity_out);
    
    // Construct Point - create base point
    ConstructPointInput cp_base_in = {
        .x = 0.0f,
        .y = cfg->last_target_from_slats,
        .z = cfg->targets_height
    };
    ConstructPointOutput cp_base_out;
    ConstructPoint_eval(&cp_base_in, &cp_base_out);
    
    // Create target points - Move base point by each UnitY vector
    out->target_count = cfg->number_of_slats;
    int move_count = (unity_out.vector_count < cfg->number_of_slats) ? 
                     unity_out.vector_count : cfg->number_of_slats;
    for (int i = 0; i < move_count && i < MAX_TARGETS; i++) {
        MoveInput move_in = { .geometry_type = 0 };
        memcpy(move_in.point, cp_base_out.point, sizeof(float) * 3);
        memcpy(move_in.motion, unity_out.unit_vectors[i], sizeof(float) * 3);
        MoveOutput move_out;
        Move_eval(&move_in, &move_out);
        memcpy(out->target_points[i], move_out.point, sizeof(float) * 3);
    }
}

