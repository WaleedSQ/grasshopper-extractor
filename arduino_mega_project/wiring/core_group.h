#ifndef CORE_GROUP_H
#define CORE_GROUP_H

#include "config.h"
#include "sun_group.h"
#include "slats_group.h"
#include "direction_group.h"
#include "targets_group.h"

#define MAX_ANGLES 100

// Output structure for core group - final results
typedef struct {
    float slat_angles[MAX_ANGLES];  // Angles in degrees
    int angle_count;
} CoreGroupOutput;

void core_group_eval(
    const ShadeConfig *cfg,
    const SunGroupOutput *sun,
    const SlatsGroupOutput *slats,
    const DirectionGroupOutput *dir,
    const TargetsGroupOutput *targets,
    CoreGroupOutput *out
);

#endif // CORE_GROUP_H

