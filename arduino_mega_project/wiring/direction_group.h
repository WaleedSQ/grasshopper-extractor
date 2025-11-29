#ifndef DIRECTION_GROUP_H
#define DIRECTION_GROUP_H

#include "config.h"
#include "slats_group.h"

// Output structure for direction group
typedef struct {
    float plane_origin[3];
    float plane_x_axis[3];
    float plane_y_axis[3];
    float plane_z_axis[3];
} DirectionGroupOutput;

void direction_group_eval(const ShadeConfig *cfg, const SlatsGroupOutput *slats, DirectionGroupOutput *out);

#endif // DIRECTION_GROUP_H

