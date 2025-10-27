#!/usr/bin/env python3
"""
Test if calibration fixed the movement issue
"""
import time
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

PORT = "/dev/tty.usbmodem5A7A0562271"  # Follower arm

print("=" * 70)
print("POST-CALIBRATION TEST")
print("=" * 70)

config = SO101FollowerConfig(port=PORT, use_degrees=True)
robot = SO101Follower(config)

print("\nConnecting to robot...")
robot.connect(calibrate=False)  # Use the new calibration
print("✓ Connected!")
print(f"✓ Calibration loaded: {robot.is_calibrated}")

# Check Lock status on each motor
print("\n" + "=" * 70)
print("CHECKING LOCK STATUS")
print("=" * 70)
for motor_name in robot.bus.motors.keys():
    lock = robot.bus.read("Lock", motor_name, normalize=False)
    torque = robot.bus.read("Torque_Enable", motor_name, normalize=False)
    print(f"{motor_name:15s}: Lock={lock}, Torque={torque}")

# Test gripper movement
print("\n" + "=" * 70)
print("GRIPPER MOVEMENT TEST")
print("=" * 70)

initial = robot.bus.read("Present_Position", "gripper")
print(f"Initial position: {initial:.1f}°")

print("\nOpening gripper...")
robot.bus.write("Goal_Position", "gripper", initial + 30)  # Move 30 degrees
time.sleep(2.0)

final = robot.bus.read("Present_Position", "gripper")
moved = abs(final - initial)
print(f"Final position: {final:.1f}° (moved {moved:.1f}°)")

if moved > 5:
    print("\n✓✓✓ SUCCESS! CALIBRATION FIXED IT!")
    print("\nThe follower arm is now working correctly!")
    
    # Test all motors briefly
    print("\nTesting all motors...")
    for motor_name in robot.bus.motors.keys():
        pos = robot.bus.read("Present_Position", motor_name)
        robot.bus.write("Goal_Position", motor_name, pos + 5)  # Small movement
        time.sleep(0.5)
        new_pos = robot.bus.read("Present_Position", motor_name)
        print(f"  {motor_name:15s}: {pos:.1f}° -> {new_pos:.1f}°")
    
    print("\n✓ All motors working!")
else:
    print("\n✗ Still not moving after calibration")
    print("\nTry:")
    print("1. Power cycle the arm (turn off, wait 30s, turn on)")
    print("2. Run calibration again")
    print("3. Check physical connections")

robot.disconnect()
print("\n✓ Disconnected")



