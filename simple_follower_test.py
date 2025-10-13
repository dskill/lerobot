#!/usr/bin/env python3
"""
Simple follower test following EXACT pattern from examples
"""
import time
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

# Testing with LEADER arm port
PORT = "/dev/tty.usbmodem5A7A0574331"

print("=" * 70)
print("SIMPLE FOLLOWER TEST - Following Examples")
print("=" * 70)

# EXACTLY like in the examples
print("\n1. Creating SO101FollowerConfig...")
follower_config = SO101FollowerConfig(
    port=PORT,
    id="my_follower_arm",
    use_degrees=True  # Use degrees like in examples
)

print("2. Creating SO101Follower robot...")
follower = SO101Follower(follower_config)

print("3. Connecting robot (bypassing calibration)...")
follower.connect(calibrate=False)  # Skip calibration, just connect

if not follower.is_connected:
    raise ValueError("Robot is not connected!")

print("\n✓✓✓ Robot connected successfully!")

# Now test movement
print("\n" + "=" * 70)
print("TESTING MOVEMENT")
print("=" * 70)

# Read all motor positions (raw values, no calibration)
print("\nCurrent positions (raw encoder values):")
for motor_name in follower.bus.motors.keys():
    pos = follower.bus.read("Present_Position", motor_name, normalize=False)
    print(f"  {motor_name:15s}: {pos}")

# Move gripper
print("\n Testing gripper movement...")
initial_gripper = follower.bus.read("Present_Position", "gripper", normalize=False)
print(f"  Initial: {initial_gripper}")

print("  Moving +500 encoder steps...")
follower.bus.write("Goal_Position", "gripper", initial_gripper + 500, normalize=False)
time.sleep(2.0)

final_gripper = follower.bus.read("Present_Position", "gripper", normalize=False)
print(f"  Final: {final_gripper}")

if abs(final_gripper - initial_gripper) > 50:
    print("\n✓✓✓ SUCCESS! Robot is working!")
    
    # Return to initial
    print("\n  Returning to initial position...")
    follower.bus.write("Goal_Position", "gripper", initial_gripper, normalize=False)
    time.sleep(1.5)
    
    # Quick test all motors
    print("\n  Testing all motors with small movements...")
    for motor_name in follower.bus.motors.keys():
        initial = follower.bus.read("Present_Position", motor_name, normalize=False)
        follower.bus.write("Goal_Position", motor_name, initial + 100, normalize=False)
        time.sleep(0.3)
        final = follower.bus.read("Present_Position", motor_name, normalize=False)
        moved = abs(final - initial)
        status = "✓" if moved > 10 else "✗"
        print(f"    {motor_name:15s}: {status} (moved {moved} steps)")
        # Return to initial
        follower.bus.write("Goal_Position", motor_name, initial, normalize=False)
else:
    print(f"\n✗ Robot still not moving (only {abs(final_gripper - initial_gripper)} steps movement)")
    print("\nDEBUG INFO:")
    for motor_name in ["gripper"]:
        lock = follower.bus.read("Lock", motor_name, normalize=False)
        torque = follower.bus.read("Torque_Enable", motor_name, normalize=False)
        mode = follower.bus.read("Operating_Mode", motor_name, normalize=False)
        print(f"  {motor_name}: Lock={lock}, Torque={torque}, Mode={mode}")

# Disconnect properly
print("\n4. Disconnecting...")
follower.disconnect()
print("✓ Done!")
