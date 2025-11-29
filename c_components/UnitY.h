#ifndef UNITY_H
#define UNITY_H

// Derived from evaluate_unit_y in gh_components_stripped.py

#define UNITY_MAX_COUNT 1000

typedef struct {
    float factor;  // Single factor (for backward compatibility)
    float factors[UNITY_MAX_COUNT];  // Array of factors
    int factor_count;  // Number of factors in array (0 means use single factor)
} UnitYInput;

typedef struct {
    float unit_vector[3];  // Single vector (for backward compatibility)
    float unit_vectors[UNITY_MAX_COUNT][3];  // Array of vectors
    int vector_count;  // Number of vectors
} UnitYOutput;

void UnitY_eval(const UnitYInput *in, UnitYOutput *out);

#endif // UNITY_H

