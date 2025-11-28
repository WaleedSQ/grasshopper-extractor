#ifndef VECTOR2PT_H
#define VECTOR2PT_H

// Derived from evaluate_vector_2pt in gh_components_stripped.py

typedef struct {
    float point_a[3];
    float point_b[3];
    bool unitize;
} Vector2PtInput;

typedef struct {
    float vector[3];
} Vector2PtOutput;

void Vector2Pt_eval(const Vector2PtInput *in, Vector2PtOutput *out);

#endif // VECTOR2PT_H

