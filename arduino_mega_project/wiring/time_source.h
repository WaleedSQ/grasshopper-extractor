#ifndef TIME_SOURCE_H
#define TIME_SOURCE_H

#include "config.h"

// Time source interface - abstracts time input
// MVP: Reads from potentiometers
// Future: Will integrate GPS/RTC without affecting other code

void time_source_update(ShadeConfig *cfg);

#endif // TIME_SOURCE_H

