#!/usr/bin/env python3
"""
Clear movement test - you WILL see the robot move!
"""
import time
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

PORT = "/dev/tty.usbmodem5A7A0574331"  # Leader arm

print("=" * 70)
print("VISIBLE MOVEMENT TEST - YOU WILL SEE THE ROBOT MOVE!")
print("=" * 70)

# Create and connect robot
config = SO101FollowerConfig(port=PORT, use_degrees=True)
robot = SO101Follower(config)

print("\nConnecting to robot...")
robot.connect(calibrate=False)
print("✓ Connected and calibration loaded!")

if not robot.is_calibrated:
    print("ERROR: Robot is not calibrated!")
    exit(1)

print("\n" + "=" * 70)
print("GRIPPER TEST - LARGE MOVEMENTS")
print("=" * 70)

# Get initial position
initial = robot.bus.read("Present_Position", "gripper")
print(f"\nInitial gripper position: {initial:.1f}°")

print("\n⚠️  GRIPPER WILL MOVE NOW! Watch the gripper!")
print("Starting movement test in 2 seconds...")
time.sleep(2)

# OPEN GRIPPER FULLY
print("\n1. OPENING GRIPPER FULLY (to 100%)...")
robot.bus.write("Goal_Position", "gripper", 100.0)  # 100% open
for i in range(5):
    time.sleep(0.5)
    pos = robot.bus.read("Present_Position", "gripper")
    print(f"   Position: {pos:.1f}°")
    if abs(pos - 100.0) < 5:
        print("   ✓ Gripper is OPEN!")
        break

time.sleep(1)

# CLOSE GRIPPER FULLY
print("\n2. CLOSING GRIPPER FULLY (to 0%)...")
robot.bus.write("Goal_Position", "gripper", 0.0)  # 0% closed
for i in range(5):
    time.sleep(0.5)
    pos = robot.bus.read("Present_Position", "gripper")
    print(f"   Position: {pos:.1f}°")
    if abs(pos - 0.0) < 5:
        print("   ✓ Gripper is CLOSED!")
        break

time.sleep(1)

# MOVE TO MIDDLE
print("\n3. MOVING TO MIDDLE (50%)...")
robot.bus.write("Goal_Position", "gripper", 50.0)
for i in range(5):
    time.sleep(0.5)
    pos = robot.bus.read("Present_Position", "gripper")
    print(f"   Position: {pos:.1f}°")
    if abs(pos - 50.0) < 5:
        print("   ✓ Gripper is at MIDDLE!")
        break

print("\n" + "=" * 70)
print("SHOULDER PAN TEST - ROTATING BASE")
print("=" * 70)

initial_shoulder = robot.bus.read("Present_Position", "shoulder_pan")
print(f"\nInitial shoulder position: {initial_shoulder:.1f}°")

print("\n⚠️  SHOULDER WILL ROTATE! Make sure area is clear!")
print("Starting rotation in 2 seconds...")
time.sleep(2)

# ROTATE LEFT
print("\n1. ROTATING LEFT...")
target = initial_shoulder - 45  # 45 degrees left
robot.bus.write("Goal_Position", "shoulder_pan", target)
for i in range(5):
    time.sleep(0.5)
    pos = robot.bus.read("Present_Position", "shoulder_pan")
    print(f"   Position: {pos:.1f}° (target: {target:.1f}°)")
    if abs(pos - target) < 5:
        print("   ✓ Reached target!")
        break

time.sleep(1)

# ROTATE RIGHT
print("\n2. ROTATING RIGHT...")
target = initial_shoulder + 45  # 45 degrees right
robot.bus.write("Goal_Position", "shoulder_pan", target)
for i in range(5):
    time.sleep(0.5)
    pos = robot.bus.read("Present_Position", "shoulder_pan")
    print(f"   Position: {pos:.1f}° (target: {target:.1f}°)")
    if abs(pos - target) < 5:
        print("   ✓ Reached target!")
        break

time.sleep(1)

# RETURN TO CENTER
print("\n3. RETURNING TO CENTER...")
robot.bus.write("Goal_Position", "shoulder_pan", initial_shoulder)
for i in range(5):
    time.sleep(0.5)
    pos = robot.bus.read("Present_Position", "shoulder_pan")
    print(f"   Position: {pos:.1f}° (target: {initial_shoulder:.1f}°)")
    if abs(pos - initial_shoulder) < 5:
        print("   ✓ Back to initial position!")
        break

print("\n" + "=" * 70)
print("ALL MOTORS - WAVE TEST")
print("=" * 70)

print("\n⚠️  ALL JOINTS WILL MOVE IN A WAVE PATTERN!")
print("Starting wave in 2 seconds...")
time.sleep(2)

# Save initial positions
print("\nSaving initial positions...")
initial_positions = {}
for motor in robot.bus.motors.keys():
    initial_positions[motor] = robot.bus.read("Present_Position", motor)
    print(f"  {motor}: {initial_positions[motor]:.1f}°")

# Wave motion
print("\nStarting wave motion...")
wave_offset = 15  # degrees
for cycle in range(2):
    print(f"\nWave cycle {cycle + 1}:")
    
    # Move all motors slightly up
    print("  Moving up...")
    for motor in robot.bus.motors.keys():
        target = initial_positions[motor] + wave_offset
        robot.bus.write("Goal_Position", motor, target)
    time.sleep(1.5)
    
    # Check positions
    for motor in robot.bus.motors.keys():
        pos = robot.bus.read("Present_Position", motor)
        expected = initial_positions[motor] + wave_offset
        moved = abs(pos - initial_positions[motor])
        print(f"    {motor}: {pos:.1f}° (moved {moved:.1f}°)")
    
    # Move all motors back down
    print("  Moving down...")
    for motor in robot.bus.motors.keys():
        target = initial_positions[motor] - wave_offset
        robot.bus.write("Goal_Position", motor, target)
    time.sleep(1.5)
    
    # Check positions
    for motor in robot.bus.motors.keys():
        pos = robot.bus.read("Present_Position", motor)
        expected = initial_positions[motor] - wave_offset
        moved = abs(pos - initial_positions[motor])
        print(f"    {motor}: {pos:.1f}° (moved {moved:.1f}°)")

# Return to initial positions
print("\nReturning to initial positions...")
for motor in robot.bus.motors.keys():
    robot.bus.write("Goal_Position", motor, initial_positions[motor])
time.sleep(2)

# Final check
print("\nFinal positions:")
any_movement = False
for motor in robot.bus.motors.keys():
    pos = robot.bus.read("Present_Position", motor)
    diff = abs(pos - initial_positions[motor])
    print(f"  {motor}: {pos:.1f}° (diff from start: {diff:.1f}°)")
    if diff > 5:
        any_movement = True

print("\n" + "=" * 70)
if any_movement:
    print("✓✓✓ ROBOT IS MOVING SUCCESSFULLY!")
else:
    print("✗ NO MOVEMENT DETECTED")
    print("\nDEBUG INFO:")
    for motor in ["gripper", "shoulder_pan"]:
        lock = robot.bus.read("Lock", motor, normalize=False)
        torque = robot.bus.read("Torque_Enable", motor, normalize=False)
        current = robot.bus.read("Present_Current", motor, normalize=False)
        print(f"  {motor}: Lock={lock}, Torque={torque}, Current={current}")
print("=" * 70)

robot.disconnect()
print("\n✓ Disconnected")
