// Derived from evaluate_subtraction in gh_components_stripped.py

#include "Subtraction.h"

void Subtraction_eval(const SubtractionInput *in, SubtractionOutput *out) {
    // GH Subtraction: A - B
    out->result = in->a - in->b;
}

