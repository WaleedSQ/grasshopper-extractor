// Derived from evaluate_sunpath in gh_components_stripped.py

#include "SunPath.h"
#include <math.h>

#define PI 3.14159265358979323846

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

static void hoy_to_datetime(double hoy, int *month, int *day, int *hour, int *minute) {
    const int NUMOFDAYSEACHMONTH[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    const int NUMOFDAYSEACHMONTHLEAP[12] = {31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    
    int is_leap = 0;  // Default to non-leap year (2017)
    int num_of_hours = 8760;
    hoy = fmod(hoy, (double)num_of_hours);
    
    const int *month_array = is_leap ? NUMOFDAYSEACHMONTHLEAP : NUMOFDAYSEACHMONTH;
    
    int accumulated_hours = 0;
    *month = 1;
    for (int i = 0; i < 12; i++) {
        int hours_in_month = month_array[i] * 24;
        if (accumulated_hours + hours_in_month > hoy) {
            *month = i + 1;
            double remaining_hours = hoy - accumulated_hours;
            *day = (int)(remaining_hours / 24.0) + 1;
            *hour = (int)fmod(remaining_hours, 24.0);
            *minute = (int)round(fmod(remaining_hours, 1.0) * 60.0);
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
    // Use double precision for all intermediate calculations (matching Python)
    double lat = (double)in->latitude;
    double lon = (double)in->longitude;
    double tz = (double)in->timezone;
    double hoy_val = (double)in->hoy;
    double north_val = (double)in->north;
    double scale_val = (double)in->scale;
    
    // Convert radians for internal use
    double lat_rad = lat * PI / 180.0;
    
    // Convert HOY to datetime components
    int month, day, hour, minute;
    hoy_to_datetime(hoy_val, &month, &day, &hour, &minute);
    int year = 2017;  // Ladybug default non-leap year
    
    // ========== SOLAR GEOMETRY ==========
    
    // Julian day calculation (matching Python: round to 2 decimal places)
    double julian_day = (double)days_from_010119(year, month, day) + 2415018.5 +
                       round((minute + hour * 60) / 1440.0 * 100.0) / 100.0 - (tz / 24.0);
    
    double julian_century = (julian_day - 2451545.0) / 36525.0;
    
    // Geometric mean longitude of sun (degrees)
    double geom_mean_long_sun = fmod(280.46646 + julian_century *
                                     (36000.76983 + julian_century * 0.0003032), 360.0);
    
    // Geometric mean anomaly of sun (degrees)
    double geom_mean_anom_sun = 357.52911 + julian_century * (35999.05029 - 0.0001537 * julian_century);
    
    // Eccentricity of earth orbit
    double eccent_orbit = 0.016708634 - julian_century * (0.000042037 + 0.0000001267 * julian_century);
    
    // Sun equation of center
    double sun_eq_of_ctr = (sin(geom_mean_anom_sun * PI / 180.0) *
                          (1.914602 - julian_century * (0.004817 + 0.000014 * julian_century)) +
                          sin(2.0 * geom_mean_anom_sun * PI / 180.0) *
                          (0.019993 - 0.000101 * julian_century) +
                          sin(3.0 * geom_mean_anom_sun * PI / 180.0) * 0.000289);
    
    // Sun true longitude (degrees)
    double sun_true_long = geom_mean_long_sun + sun_eq_of_ctr;
    
    // Sun apparent longitude (degrees)
    double sun_app_long = sun_true_long - 0.00569 -
                        0.00478 * sin((125.04 - 1934.136 * julian_century) * PI / 180.0);
    
    // Mean obliquity of ecliptic (degrees)
    double mean_obliq_ecliptic = 23.0 + (26.0 + ((21.448 - julian_century *
                                  (46.815 + julian_century * (0.00059 - julian_century * 0.001813)))) / 60.0) / 60.0;
    
    // Obliquity correction (degrees)
    double obliq_corr = mean_obliq_ecliptic +
                     0.00256 * cos((125.04 - 1934.136 * julian_century) * PI / 180.0);
    
    // Solar declination (radians)
    double sol_dec = asin(sin(obliq_corr * PI / 180.0) * sin(sun_app_long * PI / 180.0));
    
    // Equation of time (minutes)
    double var_y = tan(obliq_corr * PI / 180.0 / 2.0);
    var_y = var_y * var_y;
    double eq_of_time = 4.0 * (var_y * sin(2.0 * geom_mean_long_sun * PI / 180.0) -
                               2.0 * eccent_orbit * sin(geom_mean_anom_sun * PI / 180.0) +
                               4.0 * eccent_orbit * var_y * sin(geom_mean_anom_sun * PI / 180.0) *
                               cos(2.0 * geom_mean_long_sun * PI / 180.0) -
                               0.5 * var_y * var_y * sin(4.0 * geom_mean_long_sun * PI / 180.0) -
                               1.25 * eccent_orbit * eccent_orbit * sin(2.0 * geom_mean_anom_sun * PI / 180.0)) * 180.0 / PI;
    
    // ========== SOLAR TIME AND POSITION ==========
    
    // Get float hour from HOY
    double float_hour = fmod(hoy_val, 24.0);
    
    // Calculate solar time
    double sol_time = fmod((float_hour * 60.0 + eq_of_time + 4.0 * lon - 60.0 * tz), 1440.0) / 60.0;
    
    // Convert to minutes for hour angle calculation
    double sol_time_minutes = sol_time * 60.0;
    
    // Hour angle (degrees)
    double hour_angle;
    if (sol_time_minutes < 0.0) {
        hour_angle = sol_time_minutes / 4.0 + 180.0;
    } else {
        hour_angle = sol_time_minutes / 4.0 - 180.0;
    }
    
    // Zenith and altitude
    double zenith = acos(sin(lat_rad) * sin(sol_dec) +
                       cos(lat_rad) * cos(sol_dec) *
                       cos(hour_angle * PI / 180.0));
    double altitude_deg = 90.0 - zenith * 180.0 / PI;
    
    // ========== ATMOSPHERIC REFRACTION ==========
    double atmos_refraction = 0.0;
    if (altitude_deg > 85.0) {
        atmos_refraction = 0.0;
    } else if (altitude_deg > 5.0) {
        double tan_alt = tan(altitude_deg * PI / 180.0);
        atmos_refraction = (58.1 / tan_alt - 0.07 / (tan_alt * tan_alt * tan_alt) +
                           0.000086 / (tan_alt * tan_alt * tan_alt * tan_alt * tan_alt)) / 3600.0;
    } else if (altitude_deg > -0.575) {
        atmos_refraction = (1735.0 + altitude_deg *
                           (-518.2 + altitude_deg *
                           (103.4 + altitude_deg * (-12.79 + altitude_deg * 0.711)))) / 3600.0;
    } else {
        atmos_refraction = -20.772 / tan(altitude_deg * PI / 180.0) / 3600.0;
    }
    altitude_deg += atmos_refraction;
    
    // ========== AZIMUTH ==========
    double azimuth_deg;
    double az_init = ((sin(lat_rad) * cos(zenith)) - sin(sol_dec)) /
                    (cos(lat_rad) * sin(zenith));
    // Clamp to valid range for acos
    if (az_init > 1.0) az_init = 1.0;
    if (az_init < -1.0) az_init = -1.0;
    
    if (hour_angle > 0.0) {
        azimuth_deg = fmod((acos(az_init) * 180.0 / PI + 180.0), 360.0);
    } else {
        azimuth_deg = fmod((540.0 - acos(az_init) * 180.0 / PI), 360.0);
    }
    
    // ========== SUN VECTOR ==========
    // Start with north vector (0, 1, 0)
    // Rotate around X-axis by altitude
    double altitude_rad = altitude_deg * PI / 180.0;
    double azimuth_rad = azimuth_deg * PI / 180.0;
    double north_rad = north_val * PI / 180.0;
    
    double y_after_x = cos(altitude_rad);
    double z_after_x = sin(altitude_rad);
    
    // Rotate around Z-axis by -azimuth
    double angle = -azimuth_rad;
    double x_reversed = 0.0 * cos(angle) - y_after_x * sin(angle);
    double y_reversed = 0.0 * sin(angle) + y_after_x * cos(angle);
    double z_reversed = z_after_x;
    
    // Apply north angle rotation if needed
    if (north_val != 0.0) {
        double angle_n = north_rad;
        double x_temp = x_reversed * cos(angle_n) - y_reversed * sin(angle_n);
        double y_temp = x_reversed * sin(angle_n) + y_reversed * cos(angle_n);
        x_reversed = x_temp;
        y_reversed = y_temp;
    }
    
    // ========== SUN POINT (scaled sun_vector_reversed) ==========
    double base_scale = 100000.0;
    double effective_scale = scale_val * base_scale;
    
    out->sun_pt[0] = (float)(x_reversed * effective_scale);
    out->sun_pt[1] = (float)(y_reversed * effective_scale);
    out->sun_pt[2] = (float)(z_reversed * effective_scale);
}
