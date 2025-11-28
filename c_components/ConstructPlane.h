#ifndef CONSTRUCTPLANE_H
#define CONSTRUCTPLANE_H

// Derived from evaluate_construct_plane in gh_components_stripped.py

typedef struct {
    float origin[3];
    float x_axis[3];
    float y_axis[3];
} ConstructPlaneInput;

typedef struct {
    float origin[3];
    float x_axis[3];
    float y_axis[3];
    float z_axis[3];
} ConstructPlaneOutput;

void ConstructPlane_eval(const ConstructPlaneInput *in, ConstructPlaneOutput *out);

#endif // CONSTRUCTPLANE_H

