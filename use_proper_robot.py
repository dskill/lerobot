#!/usr/bin/env python3
"""
Use the PROPER robot initialization - this should handle everything correctly
"""
import time
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

PORT = "/dev/tty.usbmodem5A7A0562271"  # Follower arm

print("=" * 70)
print("USING PROPER ROBOT CLASS")
print("=" * 70)

# Create robot with proper config - this handles ALL initialization
config = SO101FollowerConfig(port=PORT)
robot = SO101Follower(config)

print("\nConnecting robot (this will load calibration and configure motors)...")
try:
    # Connect with calibration - this runs the full initialization sequence
    robot.connect(calibrate=False)  # Use existing calibration
    print("✓ Robot connected!")
    
    # The robot.connect() method calls configure() which properly sets up the motors
    # Let's test if it works now
    
    print("\n" + "=" * 70)
    print("TESTING GRIPPER MOVEMENT")
    print("=" * 70)
    
    # Read initial gripper position
    initial = robot.bus.read("Present_Position", "gripper", normalize=False)
    print(f"Initial gripper position: {initial}")
    
    # Test movement
    print("\nMoving gripper +500 steps...")
    robot.bus.write("Goal_Position", "gripper", initial + 500, normalize=False)
    time.sleep(2.0)
    
    final = robot.bus.read("Present_Position", "gripper", normalize=False)
    moved = abs(final - initial)
    print(f"Final position: {final} (moved {moved} steps)")
    
    if moved > 50:
        print("\n✓✓✓ SUCCESS! Robot is working!")
        print("\nThe issue was not using the proper robot class!")
        print("Always use SO101Follower for control, not raw FeetechMotorsBus")
        
        # Return to initial
        robot.bus.write("Goal_Position", "gripper", initial, normalize=False)
        time.sleep(1.5)
    else:
        print("\n✗ Still not moving even with proper initialization")
        print("\nForce recalibration might help:")
        print("robot.calibrate()  # This will redo the full calibration")
    
    robot.disconnect()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nTry forcing recalibration:")
    print("robot.connect(calibrate=True)")

print("\n✓ Done")

