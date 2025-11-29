#ifndef VECTOR2PT_H
#define VECTOR2PT_H

#include <stdbool.h>

// Derived from evaluate_vector2pt in gh_components_stripped.py

#define VECTOR2PT_MAX_COUNT 1000

typedef struct {
    float point_a[3];  // Single point A (for backward compatibility)
    float point_b[3];  // Single point B (for backward compatibility)
    float points_a[VECTOR2PT_MAX_COUNT][3];  // Array of points A
    float points_b[VECTOR2PT_MAX_COUNT][3];  // Array of points B
    int point_count;  // Number of point pairs (0 means use single points)
    bool unitize;
} Vector2PtInput;

typedef struct {
    float vector[3];  // Single vector (for backward compatibility)
    float vectors[VECTOR2PT_MAX_COUNT][3];  // Array of vectors
    int vector_count;  // Number of vectors
} Vector2PtOutput;

void Vector2Pt_eval(const Vector2PtInput *in, Vector2PtOutput *out);

#endif // VECTOR2PT_H

