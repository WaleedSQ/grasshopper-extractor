#ifndef NEGATIVE_H
#define NEGATIVE_H

// Derived from evaluate_negative in gh_components_stripped.py

#define NEGATIVE_MAX_COUNT 1000

typedef struct {
    float value;  // Single value (for backward compatibility)
    float values[NEGATIVE_MAX_COUNT];  // Array of values
    int value_count;  // Number of values in array (0 means use single value)
} NegativeInput;

typedef struct {
    float result;  // Single result (for backward compatibility)
    float results[NEGATIVE_MAX_COUNT];  // Array of results
    int result_count;  // Number of results
} NegativeOutput;

void Negative_eval(const NegativeInput *in, NegativeOutput *out);

#endif // NEGATIVE_H

