#!/usr/bin/env python3
"""
Test script to verify the Lock parameter fix for SO-101 follower arm.
This should now work after fixing the enable_torque() bug.
"""

import time
from lerobot.robots.so101_follower import SO101Follower
from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig

# Follower arm port
PORT = "/dev/tty.usbmodem5A7A0562271"

def test_motor_movement():
    print("=" * 60)
    print("Testing SO-101 Follower Arm with Lock Fix")
    print("=" * 60)
    
    # Connect to the follower arm
    print(f"\nConnecting to follower arm on {PORT}...")
    config = SO101FollowerConfig(port=PORT)
    robot = SO101Follower(config)
    robot.connect(calibrate=False)  # Skip calibration prompt - already calibrated
    
    print("✅ Connected successfully!")
    
    # Check initial status
    print("\n" + "=" * 60)
    print("Checking initial motor status...")
    print("=" * 60)
    
    motor_names = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
    for i, motor_name in enumerate(motor_names, 1):
        lock = robot.bus.read("Lock", motor_name, normalize=False)
        torque = robot.bus.read("Torque_Enable", motor_name, normalize=False)
        current = robot.bus.read("Present_Current", motor_name, normalize=False)
        position = robot.bus.read("Present_Position", motor_name, normalize=False)
        
        print(f"Motor {i} ({motor_name}): Lock={lock}, Torque={torque}, Current={current}, Position={position}")
    
    # Test motor movement using bus directly
    print("\n" + "=" * 60)
    print("Testing motor movement...")
    print("=" * 60)
    
    # Read current gripper position
    current_pos = robot.bus.read("Present_Position", "gripper", normalize=False)
    print(f"\nCurrent gripper position: {current_pos}")
    
    # Test small movement on gripper (motor 6)
    print("\nTesting gripper movement...")
    print("Moving gripper by 100 steps...")
    
    target_pos = current_pos + 100
    print(f"Target position: {target_pos}")
    
    robot.bus.write("Goal_Position", "gripper", target_pos, normalize=False)
    time.sleep(2)
    
    new_pos = robot.bus.read("Present_Position", "gripper", normalize=False)
    print(f"New gripper position: {new_pos}")
    
    # Check if motor moved
    movement = abs(new_pos - current_pos)
    print(f"\nGripper movement: {movement} steps")
    
    if movement > 10:
        print("✅ SUCCESS! Motor moved!")
        
        # Check current draw during movement
        current_draw = robot.bus.read("Present_Current", "gripper", normalize=False)
        print(f"Current draw during/after movement: {current_draw}")
    else:
        print("❌ FAILED: Motor did not move")
        
        # Check status again
        print("\nRechecking gripper status:")
        lock = robot.bus.read("Lock", "gripper", normalize=False)
        torque = robot.bus.read("Torque_Enable", "gripper", normalize=False)
        current_draw = robot.bus.read("Present_Current", "gripper", normalize=False)
        voltage = robot.bus.read("Present_Voltage", "gripper", normalize=False)
        print(f"Lock={lock}, Torque={torque}, Current={current_draw}, Voltage={voltage}")
    
    # Return to original position
    print("\nReturning to original position...")
    robot.bus.write("Goal_Position", "gripper", current_pos, normalize=False)
    time.sleep(2)
    
    final_pos = robot.bus.read("Present_Position", "gripper", normalize=False)
    print(f"Final position: {final_pos}")
    
    robot.disconnect()
    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_motor_movement()

