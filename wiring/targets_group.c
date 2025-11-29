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
#include <stdio.h>

void targets_group_eval(const ShadeConfig *cfg, TargetsGroupOutput *out) {
    // Calculate target spacing
    SubtractionInput sub_dist_in = {
        .a = cfg->last_target_from_slats,
        .b = cfg->first_target_from_slats
    };
    SubtractionOutput sub_dist_out;
    Subtraction_eval(&sub_dist_in, &sub_dist_out);
    printf("  [DEBUG] Subtraction (dist): %.6f - %.6f = %.6f\n", sub_dist_in.a, sub_dist_in.b, sub_dist_out.result);
    
    SubtractionInput sub_count_in = {
        .a = (float)cfg->number_of_slats,
        .b = 1.0f
    };
    SubtractionOutput sub_count_out;
    Subtraction_eval(&sub_count_in, &sub_count_out);
    printf("  [DEBUG] Subtraction (count): %.6f - %.6f = %.6f\n", sub_count_in.a, sub_count_in.b, sub_count_out.result);
    
    DivisionInput div_step_in = {
        .a = sub_dist_out.result,
        .b = sub_count_out.result
    };
    DivisionOutput div_step_out;
    Division_eval(&div_step_in, &div_step_out);
    printf("  [DEBUG] Division (step): %.6f / %.6f = %.6f\n", div_step_in.a, div_step_in.b, div_step_out.result);
    
    // Series for target distances
    SeriesInput series_in = {
        .start = 0.0f,
        .step = div_step_out.result,
        .count = cfg->number_of_slats
    };
    SeriesOutput series_out;
    Series_eval(&series_in, &series_out);
    printf("  [DEBUG] Series: start=%.6f, step=%.6f, count=%d -> first=%.6f, last=%.6f\n",
           series_in.start, series_in.step, series_in.count,
           series_out.series[0], series_out.series[series_out.actual_count-1]);
    
    // Negative - negate the entire series (list mode)
    NegativeInput neg_in = {
        .value = 0.0f,  // Not used when value_count > 0
        .value_count = series_out.actual_count
    };
    // Copy series values to negative input
    for (int i = 0; i < series_out.actual_count && i < NEGATIVE_MAX_COUNT; i++) {
        neg_in.values[i] = series_out.series[i];
    }
    NegativeOutput neg_out = {0};  // Initialize to zero
    Negative_eval(&neg_in, &neg_out);
    printf("  [DEBUG] Negative: input_count=%d, result_count=%d\n",
           neg_in.value_count, neg_out.result_count);
    if (neg_out.result_count > 0) {
        printf("    First: %.6f -> %.6f, Last: %.6f -> %.6f\n",
               series_out.series[0], neg_out.results[0],
               series_out.series[neg_out.result_count-1], 
               neg_out.results[neg_out.result_count-1]);
    }
    
    // UnitY - use negated values as factors (list mode)
    UnitYInput unity_in = {
        .factor = 0.0f,  // Not used when factor_count > 0
        .factor_count = neg_out.result_count
    };
    // Copy negated values to UnitY input
    for (int i = 0; i < neg_out.result_count && i < UNITY_MAX_COUNT; i++) {
        unity_in.factors[i] = neg_out.results[i];
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
    
    // Construct Point - create base point at (0, last_target_from_slats, targets_height)
    ConstructPointInput cp_base_in = {
        .x = 0.0f,
        .y = cfg->last_target_from_slats,
        .z = cfg->targets_height
    };
    ConstructPointOutput cp_base_out;
    ConstructPoint_eval(&cp_base_in, &cp_base_out);
    printf("  [DEBUG] ConstructPoint (base): (%.6f, %.6f, %.6f) -> (%.6f, %.6f, %.6f)\n",
           cp_base_in.x, cp_base_in.y, cp_base_in.z,
           cp_base_out.point[0], cp_base_out.point[1], cp_base_out.point[2]);
    
    // Create target points - Move base point by each UnitY vector
    out->target_count = cfg->number_of_slats;
    int move_count = (unity_out.vector_count < cfg->number_of_slats) ? 
                     unity_out.vector_count : cfg->number_of_slats;
    for (int i = 0; i < move_count && i < MAX_TARGETS; i++) {
        // Move - move the base point by the UnitY vector
        MoveInput move_in = {
            .geometry_type = 0,  // point
        };
        memcpy(move_in.point, cp_base_out.point, sizeof(float) * 3);
        memcpy(move_in.motion, unity_out.unit_vectors[i], sizeof(float) * 3);
        MoveOutput move_out;
        Move_eval(&move_in, &move_out);
        
        if (i < 3) {
            printf("  [DEBUG] Move (target %d): point=(%.6f, %.6f, %.6f), motion=(%.6f, %.6f, %.6f) -> (%.6f, %.6f, %.6f)\n",
                   i, move_in.point[0], move_in.point[1], move_in.point[2],
                   move_in.motion[0], move_in.motion[1], move_in.motion[2],
                   move_out.point[0], move_out.point[1], move_out.point[2]);
        }
        
        // Store the moved point
        memcpy(out->target_points[i], move_out.point, sizeof(float) * 3);
    }
}

