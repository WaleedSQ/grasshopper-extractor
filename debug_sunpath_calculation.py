"""Debug sunpath calculation to find discrepancy"""

import math

# Expected output
expected = [33219.837229, -61164.521016, 71800.722722]
expected_mag = (expected[0]**2 + expected[1]**2 + expected[2]**2)**0.5
print(f"Expected: {expected}")
print(f"Expected magnitude: {expected_mag:.2f}")
print()

# Convert to unit vector
expected_unit = [x / expected_mag for x in expected]
print(f"Expected unit vector: {expected_unit}")
print()

# Calculate altitude and azimuth from expected
# In Grasshopper: X=East, Y=North, Z=Up
# x = cos(alt) * sin(az)
# y = cos(alt) * cos(az)
# z = sin(alt)

z_unit = expected_unit[2]
altitude_expected = math.asin(z_unit)
print(f"Expected altitude: {math.degrees(altitude_expected):.6f} degrees")

# Azimuth from unit vector
x_unit = expected_unit[0]
y_unit = expected_unit[1]
azimuth_expected = math.atan2(x_unit, y_unit)  # atan2(x, y) gives azimuth from +Y
if azimuth_expected < 0:
    azimuth_expected += 2 * math.pi
print(f"Expected azimuth: {math.degrees(azimuth_expected):.6f} degrees")
print()

# Actual output
actual = [20819.409336705885, -63652.02014794362, 74262.86101381]
actual_mag = (actual[0]**2 + actual[1]**2 + actual[2]**2)**0.5
print(f"Actual: {actual}")
print(f"Actual magnitude: {actual_mag:.2f}")
print()

actual_unit = [x / actual_mag for x in actual]
print(f"Actual unit vector: {actual_unit}")
print()

z_unit_act = actual_unit[2]
altitude_actual = math.asin(z_unit_act)
print(f"Actual altitude: {math.degrees(altitude_actual):.6f} degrees")

x_unit_act = actual_unit[0]
y_unit_act = actual_unit[1]
azimuth_actual = math.atan2(x_unit_act, y_unit_act)
if azimuth_actual < 0:
    azimuth_actual += 2 * math.pi
print(f"Actual azimuth: {math.degrees(azimuth_actual):.6f} degrees")
print()

# Differences
alt_diff = math.degrees(altitude_expected - altitude_actual)
az_diff = math.degrees(azimuth_expected - azimuth_actual)
if az_diff > 180:
    az_diff -= 360
elif az_diff < -180:
    az_diff += 360

print("=" * 80)
print("DIFFERENCES")
print("=" * 80)
print(f"Altitude difference: {alt_diff:.6f} degrees")
print(f"Azimuth difference: {az_diff:.6f} degrees")
print()

# Check if it's a coordinate system issue
# Maybe the azimuth calculation or north rotation is wrong
print("Possible issues:")
print("  1. Azimuth calculation formula")
print("  2. North rotation application")
print("  3. Coordinate system conversion (X=East, Y=North, Z=Up)")
print("  4. Solar position algorithm constants")
print()

