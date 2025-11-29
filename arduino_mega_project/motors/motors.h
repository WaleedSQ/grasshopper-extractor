#ifndef MOTORS_H
#define MOTORS_H

#include "../wiring/core_group.h"

// Motor driver interface
// MVP: Prints angles to Serial
// Future: Control servo/stepper motors

void motors_init(int motor_count);
void motors_update(const CoreGroupOutput *core_output);

#endif // MOTORS_H

