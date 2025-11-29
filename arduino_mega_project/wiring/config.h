#ifndef CONFIG_H
#define CONFIG_H

// Configuration structure for Arduino - MUTABLE at runtime
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

    // Sun/time parameters (runtime adjustable)
    int   sun_month;
    int   sun_day;
    float sun_hour;
} ShadeConfig;

// Potentiometer pin definitions
#define POT_HOUR_PIN  A0
#define POT_DAY_PIN   A1
#define POT_MONTH_PIN A2

// Function declarations
void config_init_defaults(ShadeConfig *cfg);
void config_update_from_pots(ShadeConfig *cfg);
float map_pot_to_range(int adc_value, float min_value, float max_value);

#endif // CONFIG_H

