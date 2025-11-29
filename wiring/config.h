#ifndef CONFIG_H
#define CONFIG_H

// Configuration structure containing all slider values from Grasshopper
typedef struct {
    // Slat and room parameters
    float room_width;
    float slat_width;
    float distance_from_window;
    float horizontal_shift_between_slats;
    float slats_height_top;
    float slats_height_threshold;
    int   number_of_slats;
    float orientation_deg;

    // Target parameters
    float targets_height;
    float last_target_from_slats;
    float first_target_from_slats;

    // Sun/time parameters
    int   sun_month;
    int   sun_day;
    float sun_hour;
} ShadeConfig;

extern const ShadeConfig DEFAULT_CONFIG;

#endif // CONFIG_H

