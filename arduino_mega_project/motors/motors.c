#include "motors.h"
#include <Arduino.h>

static int g_motor_count = 0;

// Initialize motor system
void motors_init(int motor_count) {
    g_motor_count = motor_count;
    
    // MVP: Just initialize Serial (already done in setup)
    // Future: Initialize servo/stepper driver pins here
    
    Serial.print("Motors initialized: ");
    Serial.print(g_motor_count);
    Serial.println(" slats");
}

// Update motors with new angles
void motors_update(const CoreGroupOutput *core_output) {
    Serial.println("=== Motor Positions ===");
    
    int count = core_output->angle_count;
    if (count > g_motor_count) {
        count = g_motor_count;
    }
    
    for (int i = 0; i < count; i++) {
        Serial.print("Slat ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(core_output->slat_angles[i], 2);
        Serial.println(" degrees");
        
        // Future: Write to servo/stepper here
        // Example: servo[i].write(core_output->slat_angles[i]);
        // Or: stepper[i].moveTo(angle_to_steps(core_output->slat_angles[i]));
    }
    
    Serial.println("=======================");
}

