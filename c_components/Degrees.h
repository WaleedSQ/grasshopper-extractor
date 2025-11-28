#ifndef DEGREES_H
#define DEGREES_H

// Derived from evaluate_degrees in gh_components_stripped.py

typedef struct {
    float radians;
} DegreesInput;

typedef struct {
    float degrees;
} DegreesOutput;

void Degrees_eval(const DegreesInput *in, DegreesOutput *out);

#endif // DEGREES_H

