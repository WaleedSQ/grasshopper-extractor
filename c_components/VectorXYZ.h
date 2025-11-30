#ifndef VECTORXYZ_H
#define VECTORXYZ_H

// Derived from evaluate_vector_xyz in gh_components_rotatingslats.py

#include <math.h>

#define VECTORXYZ_MAX_COUNT 1000

typedef struct {
    // Single values (for backward compatibility)
    float x_component;
    float y_component;
    float z_component;
    
    // Array mode
    float x_components[VECTORXYZ_MAX_COUNT];
    float y_components[VECTORXYZ_MAX_COUNT];
    float z_components[VECTORXYZ_MAX_COUNT];
    int component_count;  // Number of components in arrays (0 means use single values)
} VectorXYZInput;

typedef struct {
    // Single outputs (for backward compatibility)
    float vector[3];  // Vector [x, y, z]
    float length;     // Magnitude of vector
    
    // Array mode
    float vectors[VECTORXYZ_MAX_COUNT][3];  // Array of vectors
    float lengths[VECTORXYZ_MAX_COUNT];     // Array of lengths
    int vector_count;  // Number of vectors
} VectorXYZOutput;

void VectorXYZ_eval(const VectorXYZInput *in, VectorXYZOutput *out);

#endif // VECTORXYZ_H

