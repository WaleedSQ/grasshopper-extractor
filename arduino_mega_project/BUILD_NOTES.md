# Build Notes - Arduino Mega Project

## Important: Arduino Compatibility Adjustments

### Component Files Compatibility

The component files in `c_components/` were copied from the original project. Some may contain `printf()` and `#include <stdio.h>` statements that need handling:

#### Option 1: Keep Debug Output (Recommended for Development)
No changes needed. Arduino IDE will:
- Replace `printf()` with Serial.print() macros (if you add the macro)
- Ignore `<stdio.h>` (Arduino provides its own I/O)

#### Option 2: Strip Debug Output (Recommended for Production)
Remove all `printf()` statements from component `.c` files to save memory and improve performance.

**Quick PowerShell script to remove printf lines:**

```powershell
# Run from arduino_mega_project directory
Get-ChildItem -Path c_components\*.c | ForEach-Object {
    (Get-Content $_.FullName) | Where-Object { $_ -notmatch 'printf' } | Set-Content $_.FullName
}
```

**Or manually** comment out printf lines in components that show warnings.

### Include Path Adjustments

Some component files may have include statements that need updating:

**Change from:**
```c
#include "ComponentName.h"
```

**Change to:**
```c
#include "ComponentName.h"  // Already correct for Arduino
```

Arduino IDE automatically searches subdirectories, so relative paths work correctly.

### stdio.h Removal

If you encounter compilation errors about `stdio.h`:

1. Open the problematic `.c` file
2. Remove or comment out: `#include <stdio.h>`
3. Save and recompile

Most components don't actually use stdio.h functions except printf.

## Memory Optimization Tips

### Reduce SRAM Usage

If you run low on RAM (Free RAM < 1000 bytes):

1. **Reduce MAX_SLATS** in header files:
   ```c
   // In slats_group.h, targets_group.h, core_group.h
   #define MAX_SLATS 50  // Instead of 100
   #define MAX_TARGETS 50
   #define MAX_ANGLES 50
   ```

2. **Remove unused components** from `c_components/` that aren't used by the wiring groups

3. **Strip all printf statements** from component files

### Reduce Flash Usage

If you hit the 256 KB flash limit:

1. **Remove unused components** completely
2. **Use PROGMEM** for constant data (weather data, lookup tables)
3. **Optimize floating-point operations** (use integer math where possible)

## Compilation Process

### Arduino IDE

The Arduino IDE will automatically:

1. Find `arduino_mega_project.ino` (main entry point)
2. Compile all `.c` and `.cpp` files in the project directory
3. Recursively include subdirectories (`c_components/`, `wiring/`, `motors/`, `utils/`)
4. Link everything together
5. Generate firmware binary

### Expected Output

```
Sketch uses 89234 bytes (34%) of program storage space. Maximum is 253952 bytes.
Global variables use 4123 bytes (50%) of dynamic memory, leaving 4069 bytes for local variables.
```

If these numbers are too high, apply optimizations above.

## Testing Checklist

### Before Upload

- [ ] Potentiometers connected to A0, A1, A2
- [ ] Arduino Mega selected in Tools → Board
- [ ] Correct COM port selected in Tools → Port
- [ ] Serial Monitor set to 115200 baud

### After Upload

- [ ] Serial output appears
- [ ] System initialization completes
- [ ] Potentiometer changes affect time values
- [ ] Slat angles are computed and displayed
- [ ] Free RAM is > 1000 bytes

### Common Upload Issues

**Error: "avrdude: stk500v2_ReceiveMessage(): timeout"**
- Solution: Press reset button on Arduino, then immediately click Upload

**Error: "not in sync"**
- Solution: Check COM port, try different USB cable, restart Arduino IDE

**Error: "programmer is not responding"**
- Solution: Disconnect other USB devices, check bootloader

## Performance Benchmarks

### Expected Performance (10 slats)

- **Initialization**: ~100ms
- **Sun evaluation**: ~50ms
- **Slats evaluation**: ~100ms
- **Core evaluation**: ~200ms
- **Total per cycle**: ~400ms
- **Free RAM after init**: ~4500 bytes

### Performance by Slat Count

| Slats | Eval Time | RAM Usage |
|-------|-----------|-----------|
| 5     | ~250ms    | ~3200 bytes |
| 10    | ~400ms    | ~4500 bytes |
| 20    | ~800ms    | ~6800 bytes |
| 50    | ~2000ms   | OUT OF RAM |

## Future Improvements

### Phase 1 (MVP) ✓
- [x] Potentiometer time input
- [x] Serial output of angles
- [x] Core evaluation working

### Phase 2 (Next Steps)
- [ ] RTC module integration
- [ ] SD card for EPW files
- [ ] Servo motor control
- [ ] LCD display for status
- [ ] Button interface for manual control

### Phase 3 (Advanced)
- [ ] GPS module for auto-location
- [ ] WiFi module for remote monitoring
- [ ] Multiple room support
- [ ] Seasonal profile storage
- [ ] Power optimization (sleep modes)

## Troubleshooting Compile Errors

### "undefined reference to `sqrtf`"
**Solution**: Make sure math.h is included and `-lm` flag is set (Arduino IDE handles this automatically)

### "multiple definition of `main`"
**Solution**: Remove any extra `.cpp` files with main() function. Only the .ino file should have setup() and loop()

### "too many errors emitted"
**Solution**: Fix the first error shown, then recompile. Often one error causes many cascading errors

### Component-specific errors

If a specific component fails to compile:
1. Check the component's `.c` file for Arduino-incompatible code
2. Remove `<stdio.h>` and `printf()` statements
3. Ensure all #include paths use relative paths

## Contact & Support

For issues specific to:
- **Arduino compatibility**: Check Arduino forums
- **Component errors**: Review original Grasshopper implementation
- **Memory issues**: Apply optimization techniques above
- **Motor control**: Refer to servo/stepper library documentation

---

**Last Updated**: November 2025  
**Tested On**: Arduino Mega 2560 Rev3  
**IDE Version**: Arduino IDE 1.8.19 / 2.x

