// Derived from evaluate_unit_z in gh_components_stripped.py

#include "UnitZ.h"

void UnitZ_eval(const UnitZInput *in, UnitZOutput *out) {
    if (in->factor_count > 0) {
        // Process array of factors
        int count = in->factor_count;
        if (count > UNITZ_MAX_COUNT) {
            count = UNITZ_MAX_COUNT;
        }
        for (int i = 0; i < count; i++) {
            // GH Unit Z: vector = [0, 0, factor]
            out->unit_vectors[i][0] = 0.0f;
            out->unit_vectors[i][1] = 0.0f;
            out->unit_vectors[i][2] = in->factors[i];
        }
        out->vector_count = count;
        // Also set single vector to first value for backward compatibility
        out->unit_vector[0] = out->unit_vectors[0][0];
        out->unit_vector[1] = out->unit_vectors[0][1];
        out->unit_vector[2] = out->unit_vectors[0][2];
    } else {
        // Single factor mode (backward compatibility)
        // GH Unit Z: vector = [0, 0, factor]
        out->unit_vector[0] = 0.0f;
        out->unit_vector[1] = 0.0f;
        out->unit_vector[2] = in->factor;
        out->vector_count = 0;
    }
}

