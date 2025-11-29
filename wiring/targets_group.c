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
        .start = cfg->first_target_from_slats,
        .step = div_step_out.result,
        .count = cfg->number_of_slats
    };
    SeriesOutput series_out;
    Series_eval(&series_in, &series_out);
    printf("  [DEBUG] Series: start=%.6f, step=%.6f, count=%d -> first=%.6f, last=%.6f\n",
           series_in.start, series_in.step, series_in.count,
           series_out.series[0], series_out.series[series_out.actual_count-1]);
    
    // Create target points
    out->target_count = cfg->number_of_slats;
    for (int i = 0; i < cfg->number_of_slats && i < MAX_TARGETS; i++) {
        // Construct point at (0, series_out.series[i], targets_height)
        ConstructPointInput cp_in = {
            .x = 0.0f,
            .y = series_out.series[i],
            .z = cfg->targets_height
        };
        ConstructPointOutput cp_out;
        ConstructPoint_eval(&cp_in, &cp_out);
        
        if (i < 3) {
            printf("  [DEBUG] ConstructPoint (target %d): (%.6f, %.6f, %.6f) -> (%.6f, %.6f, %.6f)\n",
                   i, cp_in.x, cp_in.y, cp_in.z, cp_out.point[0], cp_out.point[1], cp_out.point[2]);
        }
        
        // Copy directly - no need for Move
        memcpy(out->target_points[i], cp_out.point, sizeof(float) * 3);
    }
}

