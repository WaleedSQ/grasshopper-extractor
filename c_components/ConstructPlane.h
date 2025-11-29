#ifndef CONSTRUCTPLANE_H
#define CONSTRUCTPLANE_H

// Derived from evaluate_construct_plane in gh_components_stripped.py

#define CONSTRUCTPLANE_MAX_ITEMS 100

typedef struct {
    // Single plane mode (backward compatible)
    float origin[3];
    float x_axis[3];
    float y_axis[3];

    // List mode: multiple planes
    float origins[CONSTRUCTPLANE_MAX_ITEMS][3];
    float x_axes[CONSTRUCTPLANE_MAX_ITEMS][3];
    float y_axes[CONSTRUCTPLANE_MAX_ITEMS][3];
    int plane_count;  // 0 => use single origin/x_axis/y_axis above
} ConstructPlaneInput;

typedef struct {
    // Single plane output (backward compatible)
    float origin[3];
    float x_axis[3];
    float y_axis[3];
    float z_axis[3];

    // List mode outputs
    float origins[CONSTRUCTPLANE_MAX_ITEMS][3];
    float x_axes[CONSTRUCTPLANE_MAX_ITEMS][3];
    float y_axes[CONSTRUCTPLANE_MAX_ITEMS][3];
    float z_axes[CONSTRUCTPLANE_MAX_ITEMS][3];
    int plane_count;
} ConstructPlaneOutput;

void ConstructPlane_eval(const ConstructPlaneInput *in, ConstructPlaneOutput *out);

#endif // CONSTRUCTPLANE_H

