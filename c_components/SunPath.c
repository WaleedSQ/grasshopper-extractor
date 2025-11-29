// Derived from evaluate_sunpath in gh_components_stripped.py

#include "SunPath.h"
#include <math.h>

#define PI 3.14159265358979323846f

static int is_leap_year(int yr) {
    return (yr % 4 == 0 && (yr % 100 != 0 || yr % 400 == 0));
}

static int days_from_010119(int year, int month, int day) {
    const int NUMOFDAYSEACHMONTH[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    const int NUMOFDAYSEACHMONTHLEAP[12] = {31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    
    int days_in_preceding_years = 0;
    if (year == 2017) {
        days_in_preceding_years = 42734;
    } else if (year == 2016) {
        days_in_preceding_years = 42368;
    } else {
        for (int yr = 1900; yr < year; yr++) {
            days_in_preceding_years += is_leap_year(yr) ? 366 : 365;
        }
    }
    
    const int *month_array = is_leap_year(year) ? NUMOFDAYSEACHMONTHLEAP : NUMOFDAYSEACHMONTH;
    int days_in_preceding_months = 0;
    for (int i = 0; i < month - 1; i++) {
        days_in_preceding_months += month_array[i];
    }
    
    return days_in_preceding_years + days_in_preceding_months + day + 1;
}

static void hoy_to_datetime(float hoy, int *month, int *day, int *hour, int *minute) {
    const int NUMOFDAYSEACHMONTH[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    const int NUMOFDAYSEACHMONTHLEAP[12] = {31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    
    int is_leap = 0;  // Default to non-leap year (2017)
    int num_of_hours = 8760;
    hoy = fmodf(hoy, (float)num_of_hours);
    
    const int *month_array = is_leap ? NUMOFDAYSEACHMONTHLEAP : NUMOFDAYSEACHMONTH;
    
    int accumulated_hours = 0;
    *month = 1;
    for (int i = 0; i < 12; i++) {
        int hours_in_month = month_array[i] * 24;
        if (accumulated_hours + hours_in_month > (int)hoy) {
            *month = i + 1;
            float remaining_hours = hoy - accumulated_hours;
            *day = (int)(remaining_hours / 24.0f) + 1;
            *hour = (int)fmodf(remaining_hours, 24.0f);
            *minute = (int)roundf((fmodf(remaining_hours, 1.0f)) * 60.0f);
            return;
        }
        accumulated_hours += hours_in_month;
    }
    
    *month = 12;
    *day = 31;
    *hour = 23;
    *minute = 0;
}

void SunPath_eval(const SunPathInput *in, SunPathOutput *out) {
    // Convert radians for internal use
    float lat_rad = in->latitude * PI / 180.0f;
    float lon_rad = in->longitude * PI / 180.0f;
    
    // Convert HOY to datetime components
    int month, day, hour, minute;
    hoy_to_datetime(in->hoy, &month, &day, &hour, &minute);
    int year = 2017;  // Ladybug default non-leap year
    
    // ========== SOLAR GEOMETRY ==========
    
    // Julian day calculation
    float julian_day = (float)days_from_010119(year, month, day) + 2415018.5f +
                      roundf((minute + hour * 60) / 1440.0f) - (in->timezone / 24.0f);
    
    float julian_century = (julian_day - 2451545.0f) / 36525.0f;
    
    // Geometric mean longitude of sun (degrees)
    float geom_mean_long_sun = fmodf(280.46646f + julian_century *
                                     (36000.76983f + julian_century * 0.0003032f), 360.0f);
    
    // Geometric mean anomaly of sun (degrees)
    float geom_mean_anom_sun = 357.52911f + julian_century * (35999.05029f - 0.0001537f * julian_century);
    
    // Eccentricity of earth orbit
    float eccent_orbit = 0.016708634f - julian_century * (0.000042037f + 0.0000001267f * julian_century);
    
    // Sun equation of center
    float sun_eq_of_ctr = (sinf(geom_mean_anom_sun * PI / 180.0f) *
                          (1.914602f - julian_century * (0.004817f + 0.000014f * julian_century)) +
                          sinf(2.0f * geom_mean_anom_sun * PI / 180.0f) *
                          (0.019993f - 0.000101f * julian_century) +
                          sinf(3.0f * geom_mean_anom_sun * PI / 180.0f) * 0.000289f);
    
    // Sun true longitude (degrees)
    float sun_true_long = geom_mean_long_sun + sun_eq_of_ctr;
    
    // Sun apparent longitude (degrees)
    float sun_app_long = sun_true_long - 0.00569f -
                        0.00478f * sinf((125.04f - 1934.136f * julian_century) * PI / 180.0f);
    
    // Mean obliquity of ecliptic (degrees)
    float mean_obliq_ecliptic = 23.0f + (26.0f + ((21.448f - julian_century *
                                  (46.815f + julian_century * (0.00059f - julian_century * 0.001813f)))) / 60.0f) / 60.0f;
    
    // Obliquity correction (degrees)
    float obliq_corr = mean_obliq_ecliptic +
                     0.00256f * cosf((125.04f - 1934.136f * julian_century) * PI / 180.0f);
    
    // Solar declination (radians)
    float sol_dec = asinf(sinf(obliq_corr * PI / 180.0f) * sinf(sun_app_long * PI / 180.0f));
    
    // Equation of time (minutes)
    float var_y = tanf(obliq_corr * PI / 180.0f / 2.0f);
    var_y = var_y * var_y;
    float eq_of_time = 4.0f * (var_y * sinf(2.0f * geom_mean_long_sun * PI / 180.0f) -
                               2.0f * eccent_orbit * sinf(geom_mean_anom_sun * PI / 180.0f) +
                               4.0f * eccent_orbit * var_y * sinf(geom_mean_anom_sun * PI / 180.0f) *
                               cosf(2.0f * geom_mean_long_sun * PI / 180.0f) -
                               0.5f * var_y * var_y * sinf(4.0f * geom_mean_long_sun * PI / 180.0f) -
                               1.25f * eccent_orbit * eccent_orbit * sinf(2.0f * geom_mean_anom_sun * PI / 180.0f)) * 180.0f / PI;
    
    // ========== SOLAR TIME AND POSITION ==========
    
    // Get float hour from HOY
    float float_hour = fmodf(in->hoy, 24.0f);
    
    // Calculate solar time
    float sol_time = fmodf((float_hour * 60.0f + eq_of_time + 4.0f * in->longitude - 60.0f * in->timezone), 1440.0f) / 60.0f;
    
    // Convert to minutes for hour angle calculation
    float sol_time_minutes = sol_time * 60.0f;
    
    // Hour angle (degrees)
    float hour_angle;
    if (sol_time_minutes < 0.0f) {
        hour_angle = sol_time_minutes / 4.0f + 180.0f;
    } else {
        hour_angle = sol_time_minutes / 4.0f - 180.0f;
    }
    
    // Zenith and altitude
    float zenith = acosf(sinf(lat_rad) * sinf(sol_dec) +
                       cosf(lat_rad) * cosf(sol_dec) *
                       cosf(hour_angle * PI / 180.0f));
    float altitude_deg = 90.0f - zenith * 180.0f / PI;
    
    // ========== ATMOSPHERIC REFRACTION ==========
    float atmos_refraction = 0.0f;
    if (altitude_deg > 85.0f) {
        atmos_refraction = 0.0f;
    } else if (altitude_deg > 5.0f) {
        float tan_alt = tanf(altitude_deg * PI / 180.0f);
        atmos_refraction = (58.1f / tan_alt - 0.07f / (tan_alt * tan_alt * tan_alt) +
                           0.000086f / (tan_alt * tan_alt * tan_alt * tan_alt * tan_alt)) / 3600.0f;
    } else if (altitude_deg > -0.575f) {
        atmos_refraction = (1735.0f + altitude_deg *
                           (-518.2f + altitude_deg *
                           (103.4f + altitude_deg * (-12.79f + altitude_deg * 0.711f)))) / 3600.0f;
    } else {
        atmos_refraction = -20.772f / tanf(altitude_deg * PI / 180.0f) / 3600.0f;
    }
    altitude_deg += atmos_refraction;
    
    // ========== AZIMUTH ==========
    float azimuth_deg;
    float az_init = ((sinf(lat_rad) * cosf(zenith)) - sinf(sol_dec)) /
                    (cosf(lat_rad) * sinf(zenith));
    // Clamp to valid range for acos
    if (az_init > 1.0f) az_init = 1.0f;
    if (az_init < -1.0f) az_init = -1.0f;
    
    if (hour_angle > 0.0f) {
        azimuth_deg = fmodf((acosf(az_init) * 180.0f / PI + 180.0f), 360.0f);
    } else {
        azimuth_deg = fmodf((540.0f - acosf(az_init) * 180.0f / PI), 360.0f);
    }
    
    // ========== SUN VECTOR ==========
    // Start with north vector (0, 1, 0)
    // Rotate around X-axis by altitude
    float altitude_rad = altitude_deg * PI / 180.0f;
    float azimuth_rad = azimuth_deg * PI / 180.0f;
    float north_rad = in->north * PI / 180.0f;
    
    float y_after_x = cosf(altitude_rad);
    float z_after_x = sinf(altitude_rad);
    
    // Rotate around Z-axis by -azimuth
    float angle = -azimuth_rad;
    float x_reversed = 0.0f * cosf(angle) - y_after_x * sinf(angle);
    float y_reversed = 0.0f * sinf(angle) + y_after_x * cosf(angle);
    float z_reversed = z_after_x;
    
    // Apply north angle rotation if needed
    if (in->north != 0.0f) {
        float angle_n = north_rad;
        float x_temp = x_reversed * cosf(angle_n) - y_reversed * sinf(angle_n);
        float y_temp = x_reversed * sinf(angle_n) + y_reversed * cosf(angle_n);
        x_reversed = x_temp;
        y_reversed = y_temp;
    }
    
    // ========== SUN POINT (scaled sun_vector_reversed) ==========
    float base_scale = 100000.0f;
    float effective_scale = in->scale * base_scale;
    
    out->sun_pt[0] = x_reversed * effective_scale;
    out->sun_pt[1] = y_reversed * effective_scale;
    out->sun_pt[2] = z_reversed * effective_scale;
}

