// Derived from evaluate_negative in gh_components_stripped.py

#include "Negative.h"

void Negative_eval(const NegativeInput *in, NegativeOutput *out) {
    if (in->value_count > 0) {
        // Process array of values
        int count = in->value_count;
        if (count > NEGATIVE_MAX_COUNT) {
            count = NEGATIVE_MAX_COUNT;
        }
        for (int i = 0; i < count; i++) {
            out->results[i] = -in->values[i];
        }
        out->result_count = count;
        // Also set single result to first value for backward compatibility
        out->result = out->results[0];
    } else {
        // Single value mode (backward compatibility)
        out->result = -in->value;
        out->result_count = 0;
    }
}

