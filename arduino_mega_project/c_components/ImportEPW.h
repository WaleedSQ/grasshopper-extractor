#ifndef IMPORTEPW_H
#define IMPORTEPW_H

// Derived from evaluate_import_epw in gh_components_stripped.py
// STUB: returns hardcoded location data

typedef struct {
    char epw_file[256];  // Path to EPW file (unused in stub)
} ImportEPWInput;

typedef struct {
    float latitude;
    float longitude;
    float elevation;
    float timezone;
} ImportEPWOutput;

void ImportEPW_eval(const ImportEPWInput *in, ImportEPWOutput *out);

#endif // IMPORTEPW_H

