#!/usr/bin/env python3
"""
Final attempt to fix the follower arm - trying different approaches
"""
import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus, OperatingMode

PORT = "/dev/tty.usbmodem5A7A0562271"  # Follower arm

print("=" * 70)
print("FINAL FIX ATTEMPTS FOR FOLLOWER ARM")
print("=" * 70)

bus = FeetechMotorsBus(
    port=PORT,
    motors={"shoulder_pan": Motor(1, "sts3215", MotorNormMode.DEGREES)},
)

bus.connect()
print("✓ Connected!")

# Check firmware version
print("\n" + "=" * 70)
print("CHECKING FIRMWARE VERSION")
print("=" * 70)
try:
    major = bus.read("Firmware_Major_Version", "shoulder_pan", normalize=False)
    minor = bus.read("Firmware_Minor_Version", "shoulder_pan", normalize=False)
    print(f"Firmware: {major}.{minor}")
except:
    print("Could not read firmware version")

# METHOD 1: Try unlocking AFTER enabling torque
print("\n" + "=" * 70)
print("METHOD 1: Unlock AFTER torque enable")
print("=" * 70)

bus.disable_torque("shoulder_pan")
bus.write("Operating_Mode", "shoulder_pan", OperatingMode.POSITION.value, normalize=False)
bus.enable_torque("shoulder_pan")
print(f"Lock before unlock attempt: {bus.read('Lock', 'shoulder_pan', normalize=False)}")

# Try to unlock with torque ON (some servos require this)
print("Attempting to unlock with torque ON...")
bus.write("Lock", "shoulder_pan", 0, normalize=False)
time.sleep(0.2)
lock_status = bus.read("Lock", "shoulder_pan", normalize=False)
print(f"Lock after unlock attempt: {lock_status}")

if lock_status == 0:
    print("✓ Unlocked successfully!")
    # Test movement
    pos = bus.read("Present_Position", "shoulder_pan", normalize=False)
    bus.write("Goal_Position", "shoulder_pan", pos + 100, normalize=False)
    time.sleep(1.0)
    new_pos = bus.read("Present_Position", "shoulder_pan", normalize=False)
    if abs(new_pos - pos) > 50:
        print(f"✓ MOTOR MOVED! {pos} -> {new_pos}")
    else:
        print(f"✗ Still not moving: {pos} -> {new_pos}")
else:
    print("✗ Still locked")

# METHOD 2: Try different operating modes
print("\n" + "=" * 70)
print("METHOD 2: Try VELOCITY mode instead")
print("=" * 70)

bus.disable_torque("shoulder_pan")
bus.write("Operating_Mode", "shoulder_pan", 1, normalize=False)  # VELOCITY mode
bus.write("Lock", "shoulder_pan", 0, normalize=False)
bus.enable_torque("shoulder_pan")

print(f"Operating_Mode: {bus.read('Operating_Mode', 'shoulder_pan', normalize=False)}")
print(f"Lock: {bus.read('Lock', 'shoulder_pan', normalize=False)}")

# In velocity mode, set a velocity
print("Setting velocity to 100...")
bus.write("Goal_Velocity", "shoulder_pan", 100, normalize=False)
time.sleep(0.5)
vel = bus.read("Present_Velocity", "shoulder_pan", normalize=False)
print(f"Present_Velocity: {vel}")

# Stop velocity
bus.write("Goal_Velocity", "shoulder_pan", 0, normalize=False)

# METHOD 3: Check protection settings
print("\n" + "=" * 70)
print("METHOD 3: Check/disable protection settings")
print("=" * 70)

bus.disable_torque("shoulder_pan")

protection_params = [
    ("Unloading_Condition", 0),
    ("LED_Alarm_Condition", 0),
    ("Protective_Torque", 0),
    ("Protection_Time", 0),
    ("Overload_Torque", 0),
    ("Over_Current_Protection_Time", 0),
]

for param, value in protection_params:
    try:
        current = bus.read(param, "shoulder_pan", normalize=False)
        print(f"{param}: {current}", end="")
        if current != value:
            bus.write(param, "shoulder_pan", value, normalize=False)
            print(f" -> {value}")
        else:
            print()
    except:
        print(f"{param}: Could not read/write")

# Try position mode again
bus.write("Operating_Mode", "shoulder_pan", 0, normalize=False)
bus.write("Lock", "shoulder_pan", 0, normalize=False)
bus.enable_torque("shoulder_pan")

print(f"\nFinal Lock status: {bus.read('Lock', 'shoulder_pan', normalize=False)}")

# Test movement
pos = bus.read("Present_Position", "shoulder_pan", normalize=False)
bus.write("Goal_Position", "shoulder_pan", pos + 100, normalize=False)
time.sleep(1.0)
new_pos = bus.read("Present_Position", "shoulder_pan", normalize=False)
current = bus.read("Present_Current", "shoulder_pan", normalize=False)

print(f"Movement test: {pos} -> {new_pos} (current: {current})")

if abs(new_pos - pos) > 50:
    print("\n✓✓✓ SUCCESS! Found the fix!")
else:
    print("\n" + "=" * 70)
    print("FINAL RECOMMENDATIONS")
    print("=" * 70)
    print("1. The motors might need the official Feetech configuration tool")
    print("   to properly unlock them (FD Debug or SCServo_Debug)")
    print("2. Try power cycling the arm completely (unplug power for 30s)")
    print("3. The motors might be in a locked state from factory")
    print("4. Try using the full robot class with proper initialization:")
    print("")
    print("   from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig")
    print("   config = SO101FollowerConfig(port=PORT)")
    print("   robot = SO101Follower(config)")
    print("   robot.connect(calibrate=True)  # Force recalibration")
    print("")
    print("5. Contact TheRobotStudio support - this Lock=1 issue is unusual")

bus.disconnect()
print("\n✓ Disconnected")



