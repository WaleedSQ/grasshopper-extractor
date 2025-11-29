#ifndef SLATS_GROUP_H
#define SLATS_GROUP_H

#include "config.h"

#define MAX_SLATS 100

// Output structure for slats group
typedef struct {
    // Transformed slat geometries (one per slat)
    float slat_rectangles[MAX_SLATS][4][3];  // 4 corners per rectangle
    int slat_count;
} SlatsGroupOutput;

void slats_group_eval(const ShadeConfig *cfg, SlatsGroupOutput *out);

#endif // SLATS_GROUP_H

