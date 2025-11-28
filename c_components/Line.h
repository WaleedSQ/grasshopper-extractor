#ifndef LINE_H
#define LINE_H

// Derived from evaluate_line in gh_components_stripped.py

typedef struct {
    float start_point[3];
    float end_point[3];
    bool use_two_points;  // If false, uses start_point + direction + length
    float direction[3];
    float length;
} LineInput;

typedef struct {
    float start[3];
    float end[3];
} LineOutput;

void Line_eval(const LineInput *in, LineOutput *out);

#endif // LINE_H

