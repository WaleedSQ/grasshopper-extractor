#ifndef NEGATIVE_H
#define NEGATIVE_H

// Derived from evaluate_negative in gh_components_stripped.py

typedef struct {
    float value;
} NegativeInput;

typedef struct {
    float result;
} NegativeOutput;

void Negative_eval(const NegativeInput *in, NegativeOutput *out);

#endif // NEGATIVE_H

