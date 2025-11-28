#ifndef UNITZ_H
#define UNITZ_H

// Derived from evaluate_unit_z in gh_components_stripped.py

typedef struct {
    float factor;
} UnitZInput;

typedef struct {
    float unit_vector[3];
} UnitZOutput;

void UnitZ_eval(const UnitZInput *in, UnitZOutput *out);

#endif // UNITZ_H

