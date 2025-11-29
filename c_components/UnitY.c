// Derived from evaluate_unit_y in gh_components_stripped.py

#include "UnitY.h"

void UnitY_eval(const UnitYInput *in, UnitYOutput *out) {
    if (in->factor_count > 0) {
        // Process array of factors
        int count = in->factor_count;
        if (count > UNITY_MAX_COUNT) {
            count = UNITY_MAX_COUNT;
        }
        for (int i = 0; i < count; i++) {
            // GH Unit Y: vector = [0, factor, 0]
            out->unit_vectors[i][0] = 0.0f;
            out->unit_vectors[i][1] = in->factors[i];
            out->unit_vectors[i][2] = 0.0f;
        }
        out->vector_count = count;
        // Also set single vector to first value for backward compatibility
        out->unit_vector[0] = out->unit_vectors[0][0];
        out->unit_vector[1] = out->unit_vectors[0][1];
        out->unit_vector[2] = out->unit_vectors[0][2];
    } else {
        // Single factor mode (backward compatibility)
        // GH Unit Y: vector = [0, factor, 0]
        out->unit_vector[0] = 0.0f;
        out->unit_vector[1] = in->factor;
        out->unit_vector[2] = 0.0f;
        out->vector_count = 0;
    }
}

