#!/usr/bin/env python3
"""
Check and try to fix Minimum_Startup_Force parameter.
"""

import time
from lerobot.robots.so101_follower import SO101Follower
from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig

PORT = "/dev/tty.usbmodem5A7A0562271"

def check_and_fix_startup_force():
    print("=" * 70)
    print("Checking Minimum_Startup_Force")
    print("=" * 70)
    
    config = SO101FollowerConfig(port=PORT)
    robot = SO101Follower(config)
    robot.connect(calibrate=False)
    
    motor = "gripper"
    
    # Check Minimum_Startup_Force
    startup_force = robot.bus.read("Minimum_Startup_Force", motor, normalize=False)
    print(f"\nCurrent Minimum_Startup_Force: {startup_force}")
    
    if startup_force > 100:
        print(f"⚠️  This value is HIGH ({startup_force}), which might prevent movement")
        print("   Attempting to set it to a lower value...")
        
        # Need to disable torque to write to EPROM
        robot.bus.disable_torque(motor)
        robot.bus.write("Minimum_Startup_Force", motor, 0, normalize=False)
        time.sleep(0.1)
        
        # Re-enable torque
        robot.bus.enable_torque(motor)
        time.sleep(0.1)
        
        # Verify
        new_startup_force = robot.bus.read("Minimum_Startup_Force", motor, normalize=False)
        print(f"✅ New Minimum_Startup_Force: {new_startup_force}")
        
        # Now try to move
        print("\nTrying to move motor now...")
        current_pos = robot.bus.read("Present_Position", motor, normalize=False)
        print(f"Current position: {current_pos}")
        
        target_pos = current_pos + 200
        print(f"Target position: {target_pos}")
        robot.bus.write("Goal_Position", motor, target_pos, normalize=False)
        
        time.sleep(3)
        
        final_pos = robot.bus.read("Present_Position", motor, normalize=False)
        current_draw = robot.bus.read("Present_Current", motor, normalize=False)
        
        print(f"Final position: {final_pos}")
        print(f"Current draw: {current_draw}")
        
        movement = abs(final_pos - current_pos)
        if movement > 10:
            print(f"\n✅ SUCCESS! Motor moved {movement} steps!")
        else:
            print(f"\n❌ Still no movement")
    else:
        print(f"✅ Minimum_Startup_Force is reasonable ({startup_force})")
    
    robot.disconnect()

if __name__ == "__main__":
    check_and_fix_startup_force()


