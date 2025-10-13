#!/usr/bin/env python3
"""
Proper SO-101 test using the Robot class (which loads calibration automatically)
"""
import time
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

PORT = "/dev/tty.usbmodem5A7A0562271"  # Follower arm

print("=" * 60)
print("SO-101 ROBOT TEST (with proper calibration)")
print("=" * 60)

# Create robot with proper config
config = SO101FollowerConfig(port=PORT, use_degrees=True)
robot = SO101Follower(config)

print("\nConnecting to robot...")
robot.connect(calibrate=False)  # Don't re-calibrate, just load existing calibration
print("✓ Connected!")
print(f"✓ Calibrated: {robot.is_calibrated}")

# Read all positions
print("\n" + "=" * 60)
print("CURRENT JOINT POSITIONS")
print("=" * 60)
positions = robot.bus.sync_read("Present_Position")
for motor_name, pos in positions.items():
    print(f"  {motor_name:20s}: {pos:7.2f}°")

# Test gripper
print("\n" + "=" * 60)
print("GRIPPER TEST")
print("=" * 60)

initial_gripper = robot.bus.read("Present_Position", "gripper")
print(f"Initial gripper position: {initial_gripper:.2f}°")

try:
    for i in range(3):
        print(f"\nCycle {i+1}/3:")
        
        # Open
        print("  Opening...", end="", flush=True)
        robot.bus.write("Goal_Position", "gripper", initial_gripper + 20)
        time.sleep(1.0)
        print(" ✓")
        
        # Close
        print("  Closing...", end="", flush=True)
        robot.bus.write("Goal_Position", "gripper", initial_gripper - 20)
        time.sleep(1.0)
        print(" ✓")
    
    # Return to initial
    print(f"\nReturning to initial position...")
    robot.bus.write("Goal_Position", "gripper", initial_gripper)
    time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("✓ TEST COMPLETE!")
    print("=" * 60)
    
except KeyboardInterrupt:
    print("\n\nTest interrupted by user")
except Exception as e:
    print(f"\n\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\nDisconnecting...")
    robot.disconnect()
    print("✓ Disconnected safely")

