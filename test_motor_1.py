#!/usr/bin/env python3
"""
Test motor ID 1 (shoulder_pan) instead of motor 6 (gripper)
"""
import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus, OperatingMode

PORT = "/dev/tty.usbmodem5A7A0562271"  # Follower arm

print("=" * 70)
print("TESTING MOTOR ID 1 (SHOULDER PAN)")
print("=" * 70)

bus = FeetechMotorsBus(
    port=PORT,
    motors={"shoulder_pan": Motor(1, "sts3215", MotorNormMode.DEGREES)},
)

bus.connect()
print("✓ Connected!")

# Check current settings
print("\n" + "=" * 70)
print("MOTOR 1 SETTINGS")
print("=" * 70)

params = [
    ("Operating_Mode", False),
    ("Torque_Enable", False),
    ("Lock", False),
    ("Max_Torque_Limit", False),
    ("Torque_Limit", False),
    ("Present_Position", False),
    ("Goal_Position", False),
]

for param, norm in params:
    value = bus.read(param, "shoulder_pan", normalize=norm)
    print(f"{param:25s}: {value}")

# Configure motor
print("\n" + "=" * 70)
print("CONFIGURING MOTOR")
print("=" * 70)

bus.disable_torque("shoulder_pan")

print("Setting Max_Torque_Limit to 1000...")
bus.write("Max_Torque_Limit", "shoulder_pan", 1000, normalize=False)

print("Setting Torque_Limit to 1000...")
bus.write("Torque_Limit", "shoulder_pan", 1000, normalize=False)

print("Setting Operating_Mode to POSITION...")
bus.write("Operating_Mode", "shoulder_pan", OperatingMode.POSITION.value, normalize=False)

print("Setting Lock to 0...")
bus.write("Lock", "shoulder_pan", 0, normalize=False)

print("Setting position limits...")
bus.write("Min_Position_Limit", "shoulder_pan", 0, normalize=False)
bus.write("Max_Position_Limit", "shoulder_pan", 4095, normalize=False)

bus.enable_torque("shoulder_pan")
print("Torque enabled!")
time.sleep(0.5)

# Check lock status after enabling torque
lock_after = bus.read("Lock", "shoulder_pan", normalize=False)
print(f"\nLock status after enabling torque: {lock_after}")

# Test movement
print("\n" + "=" * 70)
print("MOVEMENT TEST")
print("=" * 70)

initial_pos = bus.read("Present_Position", "shoulder_pan", normalize=False)
print(f"Initial position: {initial_pos}")

print("\n⚠️  WARNING: Shoulder will move! Make sure arm is safe to move!")
print("Sending movement command (+200 steps in 3 seconds)...")
input("Press ENTER to continue or Ctrl+C to abort...")

target = initial_pos + 200
bus.write("Goal_Position", "shoulder_pan", target, normalize=False)
print(f"Goal: {target}")

# Monitor
print("\nMonitoring:")
for i in range(6):
    time.sleep(0.5)
    pos = bus.read("Present_Position", "shoulder_pan", normalize=False)
    moving = bus.read("Moving", "shoulder_pan", normalize=False)
    load = bus.read("Present_Load", "shoulder_pan", normalize=False)
    current = bus.read("Present_Current", "shoulder_pan", normalize=False)
    print(f"  {i*0.5:.1f}s: Pos={pos}, Moving={moving}, Load={load}, Current={current}")

final_pos = bus.read("Present_Position", "shoulder_pan", normalize=False)
moved = abs(final_pos - initial_pos)

print(f"\nFinal position: {final_pos}")
print(f"Total movement: {moved} steps")

if moved > 50:
    print("\n✓ SUCCESS! Motor 1 is moving!")
    print("This means motor 6 (gripper) might have a specific issue.")
    
    print("\nReturning to initial position...")
    bus.write("Goal_Position", "shoulder_pan", initial_pos, normalize=False)
    time.sleep(2.0)
else:
    print("\n✗ Motor 1 also not moving")
    print("This suggests a system-wide configuration issue.")
    print("\nPossible causes:")
    print("1. The Lock parameter might be enforced in firmware")
    print("2. There might be a safety feature preventing movement")
    print("3. The motors might be in a different mode than expected")

bus.disconnect()
print("\n✓ Disconnected")


