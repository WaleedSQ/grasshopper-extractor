#ifndef ARDUINO_COMPAT_H
#define ARDUINO_COMPAT_H

// Arduino compatibility layer for components
// Replaces stdio.h and other POSIX headers

#include <Arduino.h>
#include <math.h>
#include <string.h>

// Redirect printf to Serial for debugging
#define printf(...) Serial.print String(__VA_ARGS__)

// Math constants
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#endif // ARDUINO_COMPAT_H

