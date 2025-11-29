#include "config.h"
#include <Arduino.h>

// Initialize configuration with default values
void config_init_defaults(ShadeConfig *cfg) {
    // Slat and room parameters
    cfg->room_width = 5.0f;
    cfg->slat_width = 0.08f;
    cfg->distance_from_window = -0.07f;
    cfg->horizontal_shift_between_slats = 0.0f;
    cfg->slats_height_top = 3.8f;
    cfg->slats_height_threshold = 3.1f;
    cfg->number_of_slats = 10;
    cfg->orientation_deg = 0.0f;

    // Target parameters
    cfg->targets_height = 4.0f;
    cfg->last_target_from_slats = 4.5f;
    cfg->first_target_from_slats = 1.0f;

    // Sun/time parameters (will be updated by potentiometers)
    cfg->sun_month = 8;
    cfg->sun_day = 13;
    cfg->sun_hour = 11.0f;
}

// Map ADC value (0-1023) to a range
float map_pot_to_range(int adc_value, float min_value, float max_value) {
    // Constrain ADC value
    if (adc_value < 0) adc_value = 0;
    if (adc_value > 1023) adc_value = 1023;
    
    // Map to range
    return min_value + (adc_value / 1023.0f) * (max_value - min_value);
}

// Update configuration from potentiometers
void config_update_from_pots(ShadeConfig *cfg) {
    // Read ADC values
    int hour_adc = analogRead(POT_HOUR_PIN);
    int day_adc = analogRead(POT_DAY_PIN);
    int month_adc = analogRead(POT_MONTH_PIN);
    
    // Map to appropriate ranges
    cfg->sun_hour = map_pot_to_range(hour_adc, 0.0f, 23.99f);
    cfg->sun_day = (int)map_pot_to_range(day_adc, 1.0f, 31.0f);
    cfg->sun_month = (int)map_pot_to_range(month_adc, 1.0f, 12.0f);
}

