#ifndef MOVE_H
#define MOVE_H

// Derived from evaluate_move in gh_components_stripped.py
//
// List mode notes:
// - When point_count > 0, Move_eval processes points[0..point_count-1]
//   using the single motion vector, and fills points/point_count in
//   the output (as well as point = points[0] for backward compatibility).
// - When point_count == 0, existing single-geometry fields/behavior
//   are used unchanged.
//
#define MOVE_MAX_ITEMS 100

typedef struct {
    int geometry_type;  // 0=point, 1=line, 2=rectangle, 3=box

    // Single-geometry fields (backward compatible)
    float point[3];
    float line_start[3];
    float line_end[3];
    float rectangle_corners[4][3];
    float box_corner_a[3];
    float box_corner_b[3];
    float motion[3];

    // List mode for points
    float points[MOVE_MAX_ITEMS][3];
    int point_count;  // 0 => use single point field above

    // List mode for rectangles (each rectangle moved by corresponding motion)
    float rectangles[MOVE_MAX_ITEMS][4][3];
    float motions[MOVE_MAX_ITEMS][3];  // One motion per rectangle
    int rectangle_count;  // 0 => use single rectangle_corners + motion above
} MoveInput;

typedef struct {
    int geometry_type;

    // Single-geometry outputs (backward compatible)
    float point[3];
    float line_start[3];
    float line_end[3];
    float rectangle_corners[4][3];
    float box_corner_a[3];
    float box_corner_b[3];

    // List mode outputs for points
    float points[MOVE_MAX_ITEMS][3];
    int point_count;

    // List mode outputs for rectangles
    float rectangles[MOVE_MAX_ITEMS][4][3];
    int rectangle_count;
} MoveOutput;

void Move_eval(const MoveInput *in, MoveOutput *out);

#endif // MOVE_H


