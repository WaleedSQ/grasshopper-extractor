#ifndef DOWNLOADWEATHER_H
#define DOWNLOADWEATHER_H

// Derived from evaluate_download_weather in gh_components_stripped.py
// STUB: returns hardcoded EPW file path

typedef struct {
    // No inputs used (stub component)
} DownloadWeatherInput;

typedef struct {
    char epw_file[256];  // Path to EPW file
} DownloadWeatherOutput;

void DownloadWeather_eval(const DownloadWeatherInput *in, DownloadWeatherOutput *out);

#endif // DOWNLOADWEATHER_H

