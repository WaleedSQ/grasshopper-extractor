#ifndef SUN_GROUP_H
#define SUN_GROUP_H

#include "config.h"

// Output structure for sun group - contains data needed by other groups
typedef struct {
    float sun_pt[3];  // Sun position point from SunPath
    float sun_vector[3];  // Sun vector (from ExplodeTree output)
} SunGroupOutput;

void sun_group_eval(const ShadeConfig *cfg, SunGroupOutput *out);

#endif // SUN_GROUP_H

