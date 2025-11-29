#include "sun_group.h"
#include "../c_components/DownloadWeather.h"
#include "../c_components/ImportEPW.h"
#include "../c_components/CalculateHOY.h"
#include "../c_components/SunPath.h"
#include <string.h>
#include <math.h>

void sun_group_eval(const ShadeConfig *cfg, SunGroupOutput *out) {
    // 1. Download Weather (stub - returns hardcoded path)
    DownloadWeatherInput dw_in = {};
    DownloadWeatherOutput dw_out;
    DownloadWeather_eval(&dw_in, &dw_out);
    
    // 2. Import EPW
    ImportEPWInput epw_in;
    strncpy(epw_in.epw_file, dw_out.epw_file, sizeof(epw_in.epw_file) - 1);
    epw_in.epw_file[sizeof(epw_in.epw_file) - 1] = '\0';
    ImportEPWOutput epw_out;
    ImportEPW_eval(&epw_in, &epw_out);
    
    // 3. Calculate HOY (Hour of Year)
    CalculateHOYInput hoy_in = {
        .month = cfg->sun_month,
        .day = cfg->sun_day,
        .hour = (int)cfg->sun_hour,
        .minute = 0
    };
    CalculateHOYOutput hoy_out;
    CalculateHOY_eval(&hoy_in, &hoy_out);
    
    // 4. SunPath
    SunPathInput sp_in = {
        .latitude = epw_out.latitude,
        .longitude = epw_out.longitude,
        .elevation = epw_out.elevation,
        .timezone = epw_out.timezone,
        .hoy = (float)hoy_out.hoy,
        .north = 0.0f,
        .scale = 1.0f
    };
    SunPathOutput sp_out;
    SunPath_eval(&sp_in, &sp_out);
    
    // Copy outputs
    memcpy(out->sun_pt, sp_out.sun_pt, sizeof(float) * 3);
    
    // Compute sun_vector from sun position
    float length = sqrtf(sp_out.sun_pt[0] * sp_out.sun_pt[0] + 
                         sp_out.sun_pt[1] * sp_out.sun_pt[1] + 
                         sp_out.sun_pt[2] * sp_out.sun_pt[2]);
    if (length > 0.0001f) {
        out->sun_vector[0] = sp_out.sun_pt[0] / length;
        out->sun_vector[1] = sp_out.sun_pt[1] / length;
        out->sun_vector[2] = sp_out.sun_pt[2] / length;
    } else {
        out->sun_vector[0] = 0.0f;
        out->sun_vector[1] = 0.0f;
        out->sun_vector[2] = 1.0f;
    }
}

