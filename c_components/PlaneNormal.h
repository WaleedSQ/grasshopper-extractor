#ifndef PLANENORMAL_H
#define PLANENORMAL_H

// Derived from evaluate_plane_normal in gh_components_stripped.py

typedef struct {
    float origin[3];
    float z_axis[3];
} PlaneNormalInput;

typedef struct {
    float origin[3];
    float x_axis[3];
    float y_axis[3];
    float z_axis[3];
} PlaneNormalOutput;

void PlaneNormal_eval(const PlaneNormalInput *in, PlaneNormalOutput *out);

#endif // PLANENORMAL_H

