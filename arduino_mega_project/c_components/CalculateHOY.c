// Derived from evaluate_calculate_hoy in gh_components_stripped.py

#include "CalculateHOY.h"

void CalculateHOY_eval(const CalculateHOYInput *in, CalculateHOYOutput *out) {
    // GH LB Calculate HOY: calculate hour of year from month/day/hour
    // Days per month (non-leap year)
    const int days_per_month[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    
    // Clamp values
    int month = in->month;
    if (month < 1) month = 1;
    if (month > 12) month = 12;
    
    int day = in->day;
    if (day < 1) day = 1;
    if (day > 31) day = 31;
    
    int hour = in->hour;
    if (hour < 0) hour = 0;
    if (hour > 23) hour = 23;
    
    // Calculate day of year
    int doy = 0;
    for (int i = 0; i < month - 1; i++) {
        doy += days_per_month[i];
    }
    doy += day;
    
    // Calculate hour of year
    out->hoy = (doy - 1) * 24 + hour;
}

