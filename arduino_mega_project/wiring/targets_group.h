#ifndef TARGETS_GROUP_H
#define TARGETS_GROUP_H

#include "config.h"

#define MAX_TARGETS 100

// Output structure for targets group
typedef struct {
    float target_points[MAX_TARGETS][3];
    int target_count;
} TargetsGroupOutput;

void targets_group_eval(const ShadeConfig *cfg, TargetsGroupOutput *out);

#endif // TARGETS_GROUP_H

