#!/usr/bin/env python3
"""
Fix the Lock issue and test movement
"""
import time
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

PORT = "/dev/tty.usbmodem5A7A0574331"  # Leader arm

print("=" * 70)
print("FIX LOCK ISSUE AND TEST MOVEMENT")
print("=" * 70)

# Create and connect robot
config = SO101FollowerConfig(port=PORT, use_degrees=True)
robot = SO101Follower(config)

print("\nConnecting to robot...")
robot.connect(calibrate=False)
print("✓ Connected!")

print("\n" + "=" * 70)
print("FIXING THE LOCK ISSUE")
print("=" * 70)

# The bug is in enable_torque() which sets Lock=1
# We need to override this after torque is enabled

print("\n1. Current Lock status:")
for motor in robot.bus.motors.keys():
    lock = robot.bus.read("Lock", motor, normalize=False)
    torque = robot.bus.read("Torque_Enable", motor, normalize=False)
    print(f"  {motor:15s}: Lock={lock}, Torque={torque}")

print("\n2. FIXING: Setting Lock=0 with torque enabled...")
# This is the workaround - set Lock=0 AFTER torque is enabled
for motor in robot.bus.motors.keys():
    # Keep torque enabled but unlock
    robot.bus.write("Lock", motor, 0, normalize=False)

print("\n3. New Lock status:")
for motor in robot.bus.motors.keys():
    lock = robot.bus.read("Lock", motor, normalize=False)
    torque = robot.bus.read("Torque_Enable", motor, normalize=False)
    print(f"  {motor:15s}: Lock={lock}, Torque={torque}")

print("\n" + "=" * 70)
print("TESTING MOVEMENT WITH LOCK=0")
print("=" * 70)

# Test gripper
print("\nTesting gripper movement...")
initial = robot.bus.read("Present_Position", "gripper")
print(f"Initial position: {initial:.1f}°")

print("\nMoving gripper to 80%...")
robot.bus.write("Goal_Position", "gripper", 80.0)

# Monitor movement
print("Monitoring position (5 seconds):")
moved = False
for i in range(10):
    time.sleep(0.5)
    pos = robot.bus.read("Present_Position", "gripper")
    current = robot.bus.read("Present_Current", "gripper", normalize=False)
    lock = robot.bus.read("Lock", "gripper", normalize=False)
    diff = abs(pos - initial)
    print(f"  {i*0.5:.1f}s: Position={pos:.1f}°, Current={current}, Lock={lock}, Moved={diff:.1f}°")
    if diff > 5:
        moved = True
        print("  ✓✓✓ MOTOR IS MOVING!")
        break

if not moved:
    print("\n✗ Still not moving even with Lock=0")
    print("\nThis might be a hardware issue:")
    print("1. The Waveshare board might have its own protection")
    print("2. The motors might be damaged")
    print("3. Power might not be reaching the motors")
else:
    print("\n" + "=" * 70)
    print("✓✓✓ SUCCESS! ROBOT IS FINALLY MOVING!")
    print("=" * 70)
    print("\nThe issue was the Lock parameter being set to 1 by enable_torque()")
    print("This is a bug in the lerobot Feetech implementation")
    
    # Return to initial
    print(f"\nReturning to initial position ({initial:.1f}°)...")
    robot.bus.write("Goal_Position", "gripper", initial)
    time.sleep(2)

robot.disconnect()
print("\n✓ Disconnected")
