// Derived from evaluate_unit_y in gh_components_stripped.py

#include "UnitY.h"

void UnitY_eval(const UnitYInput *in, UnitYOutput *out) {
    // GH Unit Y: vector = [0, factor, 0]
    out->unit_vector[0] = 0.0f;
    out->unit_vector[1] = in->factor;
    out->unit_vector[2] = 0.0f;
}

