#ifndef PLANENORMAL_H
#define PLANENORMAL_H

// Derived from evaluate_plane_normal in gh_components_stripped.py

#define PLANENORMAL_MAX_ITEMS 100

typedef struct {
    // Single plane mode (backward compatible)
    float origin[3];
    float z_axis[3];

    // List mode: multiple planes
    float origins[PLANENORMAL_MAX_ITEMS][3];
    float z_axes[PLANENORMAL_MAX_ITEMS][3];
    int plane_count;  // 0 => use single origin/z_axis above
} PlaneNormalInput;

typedef struct {
    // Single plane output (backward compatible)
    float origin[3];
    float x_axis[3];
    float y_axis[3];
    float z_axis[3];

    // List mode outputs
    float origins[PLANENORMAL_MAX_ITEMS][3];
    float x_axes[PLANENORMAL_MAX_ITEMS][3];
    float y_axes[PLANENORMAL_MAX_ITEMS][3];
    float z_axes[PLANENORMAL_MAX_ITEMS][3];
    int plane_count;
} PlaneNormalOutput;

void PlaneNormal_eval(const PlaneNormalInput *in, PlaneNormalOutput *out);

#endif // PLANENORMAL_H

