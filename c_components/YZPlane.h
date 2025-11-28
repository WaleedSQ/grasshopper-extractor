#ifndef YZPLANE_H
#define YZPLANE_H

// Derived from evaluate_yz_plane in gh_components_stripped.py

typedef struct {
    float origin[3];
} YZPlaneInput;

typedef struct {
    float origin[3];
    float x_axis[3];
    float y_axis[3];
    float z_axis[3];
} YZPlaneOutput;

void YZPlane_eval(const YZPlaneInput *in, YZPlaneOutput *out);

#endif // YZPLANE_H

