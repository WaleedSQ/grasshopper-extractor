#include "time_source.h"
#include "config.h"

// MVP Implementation: Read time from potentiometers
// Future: Replace this function to use GPS/RTC without affecting other code
void time_source_update(ShadeConfig *cfg) {
    // Currently delegates to config_update_from_pots
    // In the future, this will read from GPS/RTC module
    config_update_from_pots(cfg);
}

