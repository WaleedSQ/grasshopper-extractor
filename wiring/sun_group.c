#include "sun_group.h"
#include "../c_components/DownloadWeather.h"
#include "../c_components/ImportEPW.h"
#include "../c_components/CalculateHOY.h"
#include "../c_components/SunPath.h"
#include <string.h>
#include <math.h>
#include <stdio.h>

void sun_group_eval(const ShadeConfig *cfg, SunGroupOutput *out) {
    // 1. Download Weather (stub - returns hardcoded path)
    DownloadWeatherInput dw_in = {};
    DownloadWeatherOutput dw_out;
    DownloadWeather_eval(&dw_in, &dw_out);
    printf("  [DEBUG] DownloadWeather: epw_file='%s'\n", dw_out.epw_file);
    
    // 2. Import EPW
    ImportEPWInput epw_in;
    strncpy(epw_in.epw_file, dw_out.epw_file, sizeof(epw_in.epw_file) - 1);
    epw_in.epw_file[sizeof(epw_in.epw_file) - 1] = '\0';
    ImportEPWOutput epw_out;
    ImportEPW_eval(&epw_in, &epw_out);
    printf("  [DEBUG] ImportEPW: lat=%.6f, lon=%.6f, elev=%.6f, tz=%.6f\n",
           epw_out.latitude, epw_out.longitude, epw_out.elevation, epw_out.timezone);
    
    // 3. Calculate HOY (Hour of Year)
    CalculateHOYInput hoy_in = {
        .month = cfg->sun_month,
        .day = cfg->sun_day,
        .hour = (int)cfg->sun_hour,
        .minute = 0
    };
    CalculateHOYOutput hoy_out;
    CalculateHOY_eval(&hoy_in, &hoy_out);
    printf("  [DEBUG] CalculateHOY: input month=%d, day=%d, hour=%d -> hoy=%d\n",
           hoy_in.month, hoy_in.day, hoy_in.hour, hoy_out.hoy);
    
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
    printf("  [DEBUG] SunPath: input lat=%.6f, lon=%.6f, hoy=%.6f -> sun_pt=(%.6f, %.6f, %.6f)\n",
           sp_in.latitude, sp_in.longitude, sp_in.hoy,
           sp_out.sun_pt[0], sp_out.sun_pt[1], sp_out.sun_pt[2]);
    
    // Copy outputs
    memcpy(out->sun_pt, sp_out.sun_pt, sizeof(float) * 3);
    // For sun_vector, we'll compute it from the sun position
    // In a full implementation, this would come from ExplodeTree processing
    // For now, we'll use a normalized vector from origin to sun_pt
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

