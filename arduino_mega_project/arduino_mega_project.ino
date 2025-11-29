/*
 * Arduino Mega 2560 - Adaptive Shade Control System
 * 
 * This project integrates the Grasshopper-derived evaluation engine
 * to control adaptive window shades based on sun position and time.
 * 
 * Hardware Requirements:
 * - Arduino Mega 2560
 * - 3x Potentiometers connected to A0, A1, A2 (for hour, day, month input)
 * - Optional: Future RTC/GPS module for automatic time
 * - Optional: Servo/stepper motors for slat control
 * 
 * System Architecture:
 * - config: Runtime-adjustable configuration
 * - time_source: Abstract time input (MVP: pots, Future: GPS/RTC)
 * - evaluation groups: Sun, slats, direction, targets, core computation
 * - motors: Output layer (MVP: Serial, Future: Servo/Stepper)
 */

// Core system includes
#include "wiring/config.h"
#include "wiring/time_source.h"
#include "wiring/sun_group.h"
#include "wiring/slats_group.h"
#include "wiring/direction_group.h"
#include "wiring/targets_group.h"
#include "wiring/core_group.h"
#include "motors/motors.h"

// Global configuration and output structures
ShadeConfig g_config;
SunGroupOutput g_sun_output;
SlatsGroupOutput g_slats_output;
DirectionGroupOutput g_direction_output;
TargetsGroupOutput g_targets_output;
CoreGroupOutput g_core_output;

// Timing control
unsigned long g_last_eval_time = 0;
const unsigned long EVAL_INTERVAL = 1000;  // Evaluate every second (MVP)
                                            // In production: 3600000 (1 hour)

void setup() {
    // Initialize Serial communication
    Serial.begin(115200);
    while (!Serial && millis() < 3000);  // Wait up to 3 seconds for Serial
    
    Serial.println("========================================");
    Serial.println("Arduino Mega - Adaptive Shade System");
    Serial.println("========================================");
    Serial.println();
    
    // Initialize configuration with defaults
    config_init_defaults(&g_config);
    
    Serial.println("Configuration initialized:");
    Serial.print("  Room width: "); Serial.println(g_config.room_width);
    Serial.print("  Slat width: "); Serial.println(g_config.slat_width);
    Serial.print("  Number of slats: "); Serial.println(g_config.number_of_slats);
    Serial.println();
    
    // Initialize motor system
    motors_init(g_config.number_of_slats);
    Serial.println();
    
    Serial.println("System ready!");
    Serial.println("Adjust potentiometers to change time:");
    Serial.println("  A0: Hour (0-24)");
    Serial.println("  A1: Day (1-31)");
    Serial.println("  A2: Month (1-12)");
    Serial.println();
}

void loop() {
    unsigned long current_time = millis();
    
    // Check if it's time to evaluate
    if (current_time - g_last_eval_time >= EVAL_INTERVAL) {
        g_last_eval_time = current_time;
        
        // Print separator
        Serial.println("========================================");
        Serial.print("Evaluation at T=");
        Serial.print(current_time / 1000);
        Serial.println("s");
        Serial.println("========================================");
        
        // STEP 1: Update time from potentiometers
        time_source_update(&g_config);
        
        Serial.print("Current time: ");
        Serial.print(g_config.sun_month);
        Serial.print("/");
        Serial.print(g_config.sun_day);
        Serial.print(" @ ");
        Serial.print(g_config.sun_hour, 2);
        Serial.println("h");
        Serial.println();
        
        // STEP 2: Evaluate sun position
        Serial.println("Evaluating sun position...");
        sun_group_eval(&g_config, &g_sun_output);
        Serial.print("  Sun point: (");
        Serial.print(g_sun_output.sun_pt[0], 2);
        Serial.print(", ");
        Serial.print(g_sun_output.sun_pt[1], 2);
        Serial.print(", ");
        Serial.print(g_sun_output.sun_pt[2], 2);
        Serial.println(")");
        Serial.println();
        
        // STEP 3: Evaluate slats geometry
        Serial.println("Evaluating slats geometry...");
        slats_group_eval(&g_config, &g_slats_output);
        Serial.print("  Generated ");
        Serial.print(g_slats_output.slat_count);
        Serial.println(" slat geometries");
        Serial.println();
        
        // STEP 4: Evaluate direction plane
        Serial.println("Evaluating direction plane...");
        direction_group_eval(&g_config, &g_slats_output, &g_direction_output);
        Serial.println("  Direction plane computed");
        Serial.println();
        
        // STEP 5: Evaluate target points
        Serial.println("Evaluating target points...");
        targets_group_eval(&g_config, &g_targets_output);
        Serial.print("  Generated ");
        Serial.print(g_targets_output.target_count);
        Serial.println(" target points");
        Serial.println();
        
        // STEP 6: Compute final slat angles
        Serial.println("Computing slat angles...");
        core_group_eval(&g_config, &g_sun_output, &g_slats_output, 
                       &g_direction_output, &g_targets_output, &g_core_output);
        Serial.print("  Computed ");
        Serial.print(g_core_output.angle_count);
        Serial.println(" slat angles");
        Serial.println();
        
        // STEP 7: Update motors
        motors_update(&g_core_output);
        Serial.println();
        
        // Show memory usage (helpful for debugging)
        Serial.print("Free RAM: ");
        Serial.print(freeRam());
        Serial.println(" bytes");
        Serial.println();
    }
    
    // Small delay to prevent excessive loop iterations
    delay(10);
}

// Utility function to check free RAM
int freeRam() {
    extern int __heap_start, *__brkval;
    int v;
    return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
}

