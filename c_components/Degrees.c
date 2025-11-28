// Derived from evaluate_degrees in gh_components_stripped.py

#include "Degrees.h"
#include <math.h>

void Degrees_eval(const DegreesInput *in, DegreesOutput *out) {
    // GH Degrees: degrees = radians * 180 / π
    out->degrees = in->radians * 180.0f / 3.14159265358979323846f;
}

