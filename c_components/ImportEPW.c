// Derived from evaluate_import_epw in gh_components_stripped.py
// STUB: returns hardcoded location data

#include "ImportEPW.h"

void ImportEPW_eval(const ImportEPWInput *in, ImportEPWOutput *out) {
    // GH LB Import EPW: STUB - return hardcoded location data
    (void)in;  // Unused in stub
    // Default values from EPW file
    out->latitude = 55.86700f;
    out->longitude = -3.86700f;
    out->elevation = 275.0f;
    out->timezone = 0.0f;  // Timezone offset in hours
}

