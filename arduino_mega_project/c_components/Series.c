// Derived from evaluate_series in gh_components_stripped.py

#include "Series.h"

void Series_eval(const SeriesInput *in, SeriesOutput *out) {
    // GH Series: generate count values starting at start with step
    int count = in->count;
    if (count < 0) count = 0;
    if (count > SERIES_MAX_COUNT) count = SERIES_MAX_COUNT;
    
    out->actual_count = count;
    
    for (int i = 0; i < count; i++) {
        out->series[i] = in->start + i * in->step;
    }
}

