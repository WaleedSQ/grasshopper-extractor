#ifndef LINE_H
#define LINE_H

#include <stdbool.h>

// Derived from evaluate_line in gh_components_stripped.py
//
// List mode notes:
// - When use_two_points is true and line_count > 0, Line_eval copies
//   start_points[i], end_points[i] to starts[i], ends[i] and sets
//   line_count in the output (plus start/end from the first item).
// - When line_count == 0, existing single-geometry behavior is used.
//
#define LINE_MAX_ITEMS 100

typedef struct {
    // Single-geometry inputs
    float start_point[3];
    float end_point[3];
    bool use_two_points;  // If false, uses start_point + direction + length
    float direction[3];
    float length;

    // List mode for 2-point lines (used by core_group)
    float start_points[LINE_MAX_ITEMS][3];
    float end_points[LINE_MAX_ITEMS][3];
    int line_count;  // 0 => use single start/end above
} LineInput;

typedef struct {
    // Single-geometry output (backward compatible)
    float start[3];
    float end[3];

    // List mode outputs
    float starts[LINE_MAX_ITEMS][3];
    float ends[LINE_MAX_ITEMS][3];
    int line_count;
} LineOutput;

void Line_eval(const LineInput *in, LineOutput *out);

#endif // LINE_H


