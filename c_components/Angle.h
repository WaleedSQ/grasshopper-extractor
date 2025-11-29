#ifndef ANGLE_H
#define ANGLE_H

#include <stdbool.h>

// Derived from evaluate_angle in gh_components_stripped.py

#define ANGLE_MAX_ITEMS 100

typedef struct {
    // Single angle mode (backward compatible)
    float vector_a[3];
    float vector_b[3];
    float plane_normal[3];  // Optional: if all zeros, oriented angle is not used
    bool use_oriented;

    // List mode: multiple angle calculations
    float vectors_a[ANGLE_MAX_ITEMS][3];
    float vectors_b[ANGLE_MAX_ITEMS][3];
    float plane_normals[ANGLE_MAX_ITEMS][3];
    int angle_count;  // 0 => use single vector_a/vector_b/plane_normal above
} AngleInput;

typedef struct {
    // Single angle output (backward compatible)
    float angle;  // Angle in radians

    // List mode outputs
    float angles[ANGLE_MAX_ITEMS];  // Angles in radians
    int angle_count;
} AngleOutput;

void Angle_eval(const AngleInput *in, AngleOutput *out);

#endif // ANGLE_H

