// Derived from evaluate_download_weather in gh_components_stripped.py
// STUB: returns hardcoded EPW file path

#include "DownloadWeather.h"
#include <string.h>

void DownloadWeather_eval(const DownloadWeatherInput *in, DownloadWeatherOutput *out) {
    // GH LB Download Weather: STUB - return local EPW file path
    (void)in;  // Unused
    strncpy(out->epw_file, "GBR_SCT_Salsburgh.031520_TMYx.epw", sizeof(out->epw_file) - 1);
    out->epw_file[sizeof(out->epw_file) - 1] = '\0';
}

