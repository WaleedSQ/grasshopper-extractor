#ifndef ANGLE_H
#define ANGLE_H

#include <stdbool.h>

// Derived from evaluate_angle in gh_components_stripped.py

typedef struct {
    float vector_a[3];
    float vector_b[3];
    float plane_normal[3];  // Optional: if all zeros, oriented angle is not used
    bool use_oriented;
} AngleInput;

typedef struct {
    float angle;  // Angle in radians
} AngleOutput;

void Angle_eval(const AngleInput *in, AngleOutput *out);

#endif // ANGLE_H

