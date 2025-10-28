#!/usr/bin/env python3
"""
Test Feetech servos using the Vassar SDK for low-level debugging.
This is an alternative to the LeRobot framework for direct servo control.
"""

# First install: pip install vassar-feetech-servo-sdk

from vassar_feetech_servo_sdk.controller import ServoController

# Your follower arm port
PORT = "/dev/tty.usbmodem5A7A0562271"
BAUDRATE = 1000000  # SO-101 uses 1Mbps

# Expected motor IDs for SO-101 follower
MOTOR_IDS = [1, 2, 3, 4, 5, 6]  # shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper

def test_servos():
    print("🔧 Testing Feetech servos with Vassar SDK")
    print(f"Port: {PORT}")
    print(f"Baudrate: {BAUDRATE}")
    print(f"Motor IDs: {MOTOR_IDS}")
    print()
    
    # Create controller - first param must be servo_ids list
    controller = ServoController(
        servo_ids=MOTOR_IDS,
        servo_type='sts',  # SO-101 uses STS3215 servos
        port=PORT,
        baudrate=BAUDRATE
    )
    
    print("Connecting...")
    controller.connect()
    print("✅ Connected!")
    
    print("📡 Reading servo positions...")
    try:
        # Read all positions at once
        positions = controller.read_all_positions()
        print(f"All positions: {positions}")
        print()
        
        # Read individual servo info
        for motor_id in MOTOR_IDS:
            try:
                pos = controller.read_position(motor_id)
                voltage = controller.read_voltage(motor_id)
                print(f"  ✅ Motor {motor_id}: Position={pos}, Voltage={voltage:.1f}V")
            except Exception as e:
                print(f"  ❌ Motor {motor_id}: Error - {e}")
    except Exception as e:
        print(f"❌ Error reading servos: {e}")
    
    print("\n🎯 Testing movement on motor 1...")
    try:
        import time
        
        # Read initial position
        initial_pos = controller.read_position(1)
        print(f"Initial position: {initial_pos}")
        
        # Move to a new position (small movement)
        target_pos = initial_pos + 100
        print(f"Moving to: {target_pos}")
        
        # Write position (check signature - might just be motor_id, position)
        controller.write_position(1, target_pos)
        time.sleep(1)
        
        # Read new position
        new_pos = controller.read_position(1)
        print(f"New position: {new_pos}")
        print(f"Movement: {abs(new_pos - initial_pos)} steps")
        
        # Move back
        print(f"Moving back to: {initial_pos}")
        controller.write_position(1, initial_pos)
        time.sleep(1)
        
        final_pos = controller.read_position(1)
        print(f"Final position: {final_pos}")
        print("✅ Movement test complete!")
        
    except Exception as e:
        print(f"❌ Movement test failed: {e}")
        import traceback
        traceback.print_exc()
    
    controller.disconnect()
    print("\n✅ Done!")

if __name__ == "__main__":
    try:
        test_servos()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Vassar SDK is installed: pip install vassar-feetech-servo-sdk")
        print("2. Servo power is connected")
        print("3. USB cable is connected")
        print("4. Port is correct")

