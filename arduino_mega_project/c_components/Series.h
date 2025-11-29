#ifndef SERIES_H
#define SERIES_H

// Derived from evaluate_series in gh_components_stripped.py

#define SERIES_MAX_COUNT 1000

typedef struct {
    float start;
    float step;
    int count;
} SeriesInput;

typedef struct {
    float series[SERIES_MAX_COUNT];
    int actual_count;
} SeriesOutput;

void Series_eval(const SeriesInput *in, SeriesOutput *out);

#endif // SERIES_H

