#!/usr/bin/env python3
"""
Test if we can actually write Goal_Position and have it stick.
"""

import time
from lerobot.robots.so101_follower import SO101Follower
from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig

PORT = "/dev/tty.usbmodem5A7A0562271"

def test_goal_position_write():
    print("=" * 70)
    print("Testing Goal_Position Write")
    print("=" * 70)
    
    config = SO101FollowerConfig(port=PORT)
    robot = SO101Follower(config)
    robot.connect(calibrate=False)
    
    motor = "gripper"
    
    # Read current position
    current_pos = robot.bus.read("Present_Position", motor, normalize=False)
    current_goal = robot.bus.read("Goal_Position", motor, normalize=False)
    
    print(f"\nBefore write:")
    print(f"  Present_Position: {current_pos}")
    print(f"  Goal_Position:    {current_goal}")
    
    # Try to write a new goal position
    new_goal = current_pos + 200
    print(f"\nWriting Goal_Position = {new_goal}...")
    
    robot.bus.write("Goal_Position", motor, new_goal, normalize=False)
    
    # Wait a moment
    time.sleep(0.1)
    
    # Read back the goal position
    readback_goal = robot.bus.read("Goal_Position", motor, normalize=False)
    readback_present = robot.bus.read("Present_Position", motor, normalize=False)
    moving = robot.bus.read("Moving", motor, normalize=False)
    current_draw = robot.bus.read("Present_Current", motor, normalize=False)
    
    print(f"\nImmediately after write:")
    print(f"  Goal_Position:     {readback_goal}")
    print(f"  Present_Position:  {readback_present}")
    print(f"  Moving:            {moving}")
    print(f"  Present_Current:   {current_draw}")
    
    if readback_goal == new_goal:
        print("\n✅ Goal_Position was written successfully!")
    else:
        print(f"\n❌ Goal_Position write failed! Expected {new_goal}, got {readback_goal}")
    
    # Wait for movement
    print("\nWaiting 3 seconds for movement...")
    time.sleep(3)
    
    final_pos = robot.bus.read("Present_Position", motor, normalize=False)
    final_goal = robot.bus.read("Goal_Position", motor, normalize=False)
    final_moving = robot.bus.read("Moving", motor, normalize=False)
    final_current = robot.bus.read("Present_Current", motor, normalize=False)
    
    print(f"\nAfter 3 seconds:")
    print(f"  Goal_Position:     {final_goal}")
    print(f"  Present_Position:  {final_pos}")
    print(f"  Moving:            {final_moving}")
    print(f"  Present_Current:   {final_current}")
    
    movement = abs(final_pos - current_pos)
    print(f"\nTotal movement: {movement} steps")
    
    if movement > 10:
        print("✅ SUCCESS! Motor moved!")
    elif final_goal != new_goal:
        print("❌ FAILED: Goal_Position was reset or not maintained")
    else:
        print("❌ FAILED: Goal_Position set correctly but motor didn't move")
        print("   This suggests a hardware or firmware issue preventing motor power")
    
    robot.disconnect()

if __name__ == "__main__":
    test_goal_position_write()


