# Arduino Mega 2560 - Adaptive Shade Control System

## Overview

This project implements an adaptive window shade control system for Arduino Mega 2560. It integrates a Grasshopper-derived evaluation engine to compute optimal slat angles based on sun position, room geometry, and target illumination points.

## Hardware Requirements

### Minimum (MVP)
- **Arduino Mega 2560** (ATmega2560, 16 MHz, 8 KB SRAM)
- **3x 10kΩ Potentiometers** connected to analog pins:
  - A0: Hour control (0-24 hours)
  - A1: Day control (1-31 days)
  - A2: Month control (1-12 months)
- **USB cable** for programming and Serial output

### Future Expansion
- **RTC Module** (DS3231 or similar) for automatic timekeeping
- **GPS Module** for automatic location and time
- **Servo Motors** (e.g., 10x SG90) or **Stepper Motors** for slat control
- **External Motor Driver** (e.g., PCA9685) for controlling multiple servos

## Project Structure

```
arduino_mega_project/
├── arduino_mega_project.ino    # Main Arduino sketch
├── c_components/               # Grasshopper component implementations
│   ├── Angle.c/.h             # Angle calculation
│   ├── Area.c/.h              # Area and centroid calculation
│   ├── Circle.c/.h            # Circle geometry
│   ├── CurveCurve.c/.h        # Curve intersection
│   ├── ImportEPW.c/.h         # EPW weather file import
│   ├── SunPath.c/.h           # Solar position calculation
│   └── ... (40+ component files)
├── wiring/                     # Evaluation pipeline
│   ├── config.c/.h            # Runtime configuration
│   ├── time_source.c/.h       # Time input abstraction
│   ├── sun_group.c/.h         # Sun position evaluation
│   ├── slats_group.c/.h       # Slat geometry generation
│   ├── direction_group.c/.h   # Direction plane computation
│   ├── targets_group.c/.h     # Target point generation
│   └── core_group.c/.h        # Core angle computation
├── motors/                     # Motor control layer
│   ├── motors.c/.h            # Motor driver interface
└── utils/                      # Utility headers
    ├── types.h                # Basic type definitions
    └── arduino_compat.h       # Arduino compatibility layer
```

## System Architecture

### Evaluation Pipeline

The system evaluates slat angles through a sequential pipeline:

1. **Time Source** → Reads current time from potentiometers (or RTC/GPS in future)
2. **Sun Group** → Calculates sun position based on time and location
3. **Slats Group** → Generates slat geometries based on room parameters
4. **Direction Group** → Computes direction plane for projection
5. **Targets Group** → Generates target illumination points
6. **Core Group** → Computes optimal slat angles using ray tracing
7. **Motors** → Outputs commands to control physical slats

### Memory Management

The system is designed for the Arduino Mega's 8 KB SRAM:
- **No dynamic allocation** - all structures are statically allocated
- **Efficient float usage** - floats only where necessary
- **Limited array sizes** - MAX_SLATS = 100 (configurable)
- **Stripped debug output** - minimal Serial prints in production

## Configuration

### Default Parameters

Edit `wiring/config.c` to change default values:

```c
// Slat and room parameters
cfg->room_width = 5.0f;                // Room width (meters)
cfg->slat_width = 0.08f;               // Slat width (meters)
cfg->distance_from_window = -0.07f;    // Distance from window
cfg->number_of_slats = 10;             // Number of slats to control
cfg->orientation_deg = 0.0f;           // Building orientation (degrees)

// Target parameters
cfg->targets_height = 4.0f;            // Target height (meters)
cfg->last_target_from_slats = 4.5f;    // Last target distance
cfg->first_target_from_slats = 1.0f;   // First target distance
```

### Runtime Parameters

Time parameters are controlled by potentiometers:
- **Hour**: Maps 0-1023 ADC → 0.0-23.99 hours
- **Day**: Maps 0-1023 ADC → 1-31 days
- **Month**: Maps 0-1023 ADC → 1-12 months

## Installation

### Arduino IDE

1. **Copy the entire `arduino_mega_project` folder** to your Arduino sketchbook
2. **Open `arduino_mega_project.ino`** in Arduino IDE
3. **Select Board**: Tools → Board → Arduino Mega or Mega 2560
4. **Select Port**: Tools → Port → (your COM port)
5. **Upload**: Click Upload button

### Compilation

The project compiles as a standard Arduino sketch. The Arduino IDE automatically:
- Compiles all `.c` and `.cpp` files in the sketch folder
- Includes all subdirectories (`c_components/`, `wiring/`, `motors/`, `utils/`)
- Links everything into a single firmware binary

## Usage

### MVP Mode (Current)

1. **Connect potentiometers** to A0, A1, A2
2. **Upload firmware** to Arduino Mega
3. **Open Serial Monitor** at 115200 baud
4. **Adjust potentiometers** to change time
5. **Observe slat angles** printed to Serial every second

### Production Mode (Future)

To change evaluation frequency from 1 second to 1 hour:

```cpp
// In arduino_mega_project.ino, line 26:
const unsigned long EVAL_INTERVAL = 3600000;  // 1 hour in milliseconds
```

### Adding RTC/GPS

Replace the time source without affecting other code:

1. **Edit `wiring/time_source.c`**:

```c
void time_source_update(ShadeConfig *cfg) {
    // Replace potentiometer code with RTC/GPS code
    DateTime now = rtc.now();  // Example for DS3231
    cfg->sun_hour = now.hour() + (now.minute() / 60.0f);
    cfg->sun_day = now.day();
    cfg->sun_month = now.month();
}
```

2. **No other files need modification** - the modular architecture isolates time input

### Adding Motor Control

Replace the motor stub with actual hardware control:

1. **Edit `motors/motors.c`** `motors_init()`:

```c
void motors_init(int motor_count) {
    g_motor_count = motor_count;
    
    // Initialize servo library
    for (int i = 0; i < motor_count; i++) {
        servos[i].attach(servo_pins[i]);  // Attach to PWM pins
    }
}
```

2. **Edit `motors/motors.c`** `motors_update()`:

```c
void motors_update(const CoreGroupOutput *core_output) {
    for (int i = 0; i < g_motor_count; i++) {
        float angle = core_output->slat_angles[i];
        servos[i].write(angle);  // Write angle to servo
    }
}
```

## Performance

### Timing

On Arduino Mega 2560 @ 16 MHz:
- **Evaluation time**: ~200-500ms per cycle (depending on slat count)
- **Update frequency**: Once per hour (negligible CPU load)
- **Free RAM**: ~4-5 KB available after initialization

### Optimization Notes

- Floats are software-emulated on AVR (slow but acceptable for hourly updates)
- Trigonometric functions (sin, cos, atan2) are the most expensive operations
- Consider reducing `MAX_SLATS` if memory is tight

## Serial Output

Example output:

```
========================================
Arduino Mega - Adaptive Shade System
========================================

Configuration initialized:
  Room width: 5.00
  Slat width: 0.08
  Number of slats: 10

Motors initialized: 10 slats

========================================
Evaluation at T=12s
========================================
Current time: 8/13 @ 11.50h

Evaluating sun position...
  Sun point: (33219.45, -61164.32, 71800.12)

Evaluating slats geometry...
  Generated 10 slat geometries

Computing slat angles...
  Computed 10 slat angles

=== Motor Positions ===
Slat 0: 45.23 degrees
Slat 1: 43.87 degrees
...
Slat 9: 38.12 degrees
=======================

Free RAM: 4832 bytes
```

## Troubleshooting

### Compilation Errors

- **"not enough memory"**: Reduce `MAX_SLATS` in header files
- **"undefined reference"**: Ensure all `.c` files are in the sketch folder
- **"multiple definitions"**: Check for duplicate `.cpp` files

### Runtime Issues

- **Low free RAM (<1000 bytes)**: Reduce `MAX_SLATS` or strip more debug code
- **Incorrect angles**: Verify potentiometer connections and EPW file data
- **System hangs**: Check for stack overflow (reduce local array sizes)

## Data Files

### EPW Weather File

The system requires an EPW (EnergyPlus Weather) file for location data:
- Default: `GBR_SCT_Salsburgh.031520_TMYx.epw`
- Copy to SD card or embed data in firmware
- Contains: latitude, longitude, elevation, timezone

### Future: SD Card Support

To add SD card support for EPW files:

1. Connect SD card module to SPI pins
2. Modify `ImportEPW.c` to read from SD card instead of embedded data

## License

This project integrates code derived from Grasshopper components. 
Ensure compliance with relevant licenses for commercial use.

## Credits

- **Grasshopper Evaluation Engine**: Ported from visual programming workflow
- **Arduino Mega Platform**: ATmega2560 microcontroller
- **Solar Position Algorithm**: Based on NOAA solar calculator

## Support

For issues, improvements, or questions, refer to the project documentation or contact the development team.

---

**Version**: 1.0.0 (MVP)  
**Target**: Arduino Mega 2560  
**Date**: November 2025

