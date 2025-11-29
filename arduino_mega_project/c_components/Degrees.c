// Derived from evaluate_degrees in gh_components_stripped.py

#include "Degrees.h"
#include <math.h>
#include <string.h>

void Degrees_eval(const DegreesInput *in, DegreesOutput *out) {
    memset(out, 0, sizeof(DegreesOutput));

    // List mode: multiple conversions
    if (in->radians_count > 0) {
        int count = in->radians_count;
        if (count > DEGREES_MAX_ITEMS) count = DEGREES_MAX_ITEMS;

        const float RAD_TO_DEG = 180.0f / 3.14159265358979323846f;
        for (int i = 0; i < count; ++i) {
            out->degrees_list[i] = in->radians_list[i] * RAD_TO_DEG;
        }
        out->degrees_count = count;

        // Backward-compatible single value = first element
        out->degrees = out->degrees_list[0];
        return;
    }

    // Single value mode (backward compatible)
    out->degrees = in->radians * 180.0f / 3.14159265358979323846f;
}

