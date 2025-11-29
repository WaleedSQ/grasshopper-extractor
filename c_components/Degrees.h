#ifndef DEGREES_H
#define DEGREES_H

// Derived from evaluate_degrees in gh_components_stripped.py

#define DEGREES_MAX_ITEMS 100

typedef struct {
    // Single value mode (backward compatible)
    float radians;

    // List mode: multiple conversions
    float radians_list[DEGREES_MAX_ITEMS];
    int radians_count;  // 0 => use single radians above
} DegreesInput;

typedef struct {
    // Single value output (backward compatible)
    float degrees;

    // List mode outputs
    float degrees_list[DEGREES_MAX_ITEMS];
    int degrees_count;
} DegreesOutput;

void Degrees_eval(const DegreesInput *in, DegreesOutput *out);

#endif // DEGREES_H

