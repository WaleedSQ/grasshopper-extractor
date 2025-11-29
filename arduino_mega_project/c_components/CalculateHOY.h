#ifndef CALCULATEHOY_H
#define CALCULATEHOY_H

// Derived from evaluate_calculate_hoy in gh_components_stripped.py

typedef struct {
    int month;   // 1-12
    int day;     // 1-31
    int hour;    // 0-23
    int minute;  // 0-59
} CalculateHOYInput;

typedef struct {
    int hoy;  // Hour of year (0-8759)
} CalculateHOYOutput;

void CalculateHOY_eval(const CalculateHOYInput *in, CalculateHOYOutput *out);

#endif // CALCULATEHOY_H

