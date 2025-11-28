// Derived from evaluate_negative in gh_components_stripped.py

#include "Negative.h"

void Negative_eval(const NegativeInput *in, NegativeOutput *out) {
    // GH Negative: -value
    out->result = -in->value;
}

