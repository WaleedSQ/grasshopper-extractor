// Derived from evaluate_division in gh_components_stripped.py

#include "Division.h"
#include <math.h>

void Division_eval(const DivisionInput *in, DivisionOutput *out) {
    // GH Division: A / B
    if (in->b == 0.0f) {
        // Division by zero: return infinity with sign of numerator
        out->result = (in->a >= 0.0f) ? INFINITY : -INFINITY;
    } else {
        out->result = in->a / in->b;
    }
}

