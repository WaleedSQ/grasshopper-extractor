#ifndef SUBTRACTION_H
#define SUBTRACTION_H

// Derived from evaluate_subtraction in gh_components_stripped.py

typedef struct {
    float a;
    float b;
} SubtractionInput;

typedef struct {
    float result;
} SubtractionOutput;

void Subtraction_eval(const SubtractionInput *in, SubtractionOutput *out);

#endif // SUBTRACTION_H

