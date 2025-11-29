#ifndef SUNPATH_H
#define SUNPATH_H

// Derived from evaluate_sunpath in gh_components_stripped.py

typedef struct {
    float latitude;
    float longitude;
    float elevation;
    float timezone;
    float hoy;      // Hour of year
    float north;     // North direction in degrees, CCW from +Y (default 0)
    float scale;     // Scale factor (default 1)
} SunPathInput;

typedef struct {
    float sun_pt[3];  // Sun position point (3D coordinates)
} SunPathOutput;

void SunPath_eval(const SunPathInput *in, SunPathOutput *out);

#endif // SUNPATH_H

