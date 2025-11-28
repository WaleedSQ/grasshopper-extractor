#ifndef MOVE_H
#define MOVE_H

// Derived from evaluate_move in gh_components_stripped.py

typedef struct {
    int geometry_type;  // 0=point, 1=line, 2=rectangle, 3=box
    float point[3];
    float line_start[3];
    float line_end[3];
    float rectangle_corners[4][3];
    float box_corner_a[3];
    float box_corner_b[3];
    float motion[3];
} MoveInput;

typedef struct {
    int geometry_type;
    float point[3];
    float line_start[3];
    float line_end[3];
    float rectangle_corners[4][3];
    float box_corner_a[3];
    float box_corner_b[3];
} MoveOutput;

void Move_eval(const MoveInput *in, MoveOutput *out);

#endif // MOVE_H

