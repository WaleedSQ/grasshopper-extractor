#ifndef DIVISION_H
#define DIVISION_H

// Derived from evaluate_division in gh_components_stripped.py

typedef struct {
    float a;
    float b;
} DivisionInput;

typedef struct {
    float result;
} DivisionOutput;

void Division_eval(const DivisionInput *in, DivisionOutput *out);

#endif // DIVISION_H

