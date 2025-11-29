#ifndef YZPLANE_H
#define YZPLANE_H

// Derived from evaluate_yz_plane in gh_components_stripped.py

#define YZPLANE_MAX_ITEMS 100

typedef struct {
    // Single plane mode (backward compatible)
    float origin[3];

    // List mode: multiple planes
    float origins[YZPLANE_MAX_ITEMS][3];
    int plane_count;  // 0 => use single origin above
} YZPlaneInput;

typedef struct {
    // Single plane output (backward compatible)
    float origin[3];
    float x_axis[3];
    float y_axis[3];
    float z_axis[3];

    // List mode outputs
    float origins[YZPLANE_MAX_ITEMS][3];
    float x_axes[YZPLANE_MAX_ITEMS][3];
    float y_axes[YZPLANE_MAX_ITEMS][3];
    float z_axes[YZPLANE_MAX_ITEMS][3];
    int plane_count;
} YZPlaneOutput;

void YZPlane_eval(const YZPlaneInput *in, YZPlaneOutput *out);

#endif // YZPLANE_H

