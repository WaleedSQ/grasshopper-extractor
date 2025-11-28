// Derived from evaluate_unit_z in gh_components_stripped.py

#include "UnitZ.h"

void UnitZ_eval(const UnitZInput *in, UnitZOutput *out) {
    // GH Unit Z: vector = [0, 0, factor]
    out->unit_vector[0] = 0.0f;
    out->unit_vector[1] = 0.0f;
    out->unit_vector[2] = in->factor;
}

