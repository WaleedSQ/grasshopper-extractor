#ifndef UNITZ_H
#define UNITZ_H

// Derived from evaluate_unit_z in gh_components_stripped.py

#define UNITZ_MAX_COUNT 1000

typedef struct {
    float factor;  // Single factor (for backward compatibility)
    float factors[UNITZ_MAX_COUNT];  // Array of factors
    int factor_count;  // Number of factors in array (0 means use single factor)
} UnitZInput;

typedef struct {
    float unit_vector[3];  // Single vector (for backward compatibility)
    float unit_vectors[UNITZ_MAX_COUNT][3];  // Array of vectors
    int vector_count;  // Number of vectors
} UnitZOutput;

void UnitZ_eval(const UnitZInput *in, UnitZOutput *out);

#endif // UNITZ_H

