#ifndef CONSTRUCTPOINT_H
#define CONSTRUCTPOINT_H

// Derived from evaluate_construct_point in gh_components_stripped.py

typedef struct {
    float x;
    float y;
    float z;
} ConstructPointInput;

typedef struct {
    float point[3];
} ConstructPointOutput;

void ConstructPoint_eval(const ConstructPointInput *in, ConstructPointOutput *out);

#endif // CONSTRUCTPOINT_H

