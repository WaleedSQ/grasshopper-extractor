#ifndef UNITY_H
#define UNITY_H

// Derived from evaluate_unit_y in gh_components_stripped.py

typedef struct {
    float factor;
} UnitYInput;

typedef struct {
    float unit_vector[3];
} UnitYOutput;

void UnitY_eval(const UnitYInput *in, UnitYOutput *out);

#endif // UNITY_H

