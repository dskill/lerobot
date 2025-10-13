#!/usr/bin/env python3

"""
Verify that the Lock parameter fix is working.
This reads the Lock and Torque_Enable values from the motors.
"""

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

# Connect to follower arm
FOLLOWER_PORT = "/dev/tty.usbmodem5A7A0562271"

print("Connecting to follower arm to verify Lock parameter...")
print(f"Port: {FOLLOWER_PORT}\n")

bus = FeetechMotorsBus(
    port=FOLLOWER_PORT,
    motors={
        "shoulder_pan": Motor(1, "sts3215", MotorNormMode.RANGE_M100_100),
        "shoulder_lift": Motor(2, "sts3215", MotorNormMode.RANGE_M100_100),
        "elbow_flex": Motor(3, "sts3215", MotorNormMode.RANGE_M100_100),
        "wrist_flex": Motor(4, "sts3215", MotorNormMode.RANGE_M100_100),
        "wrist_roll": Motor(5, "sts3215", MotorNormMode.RANGE_M100_100),
        "gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100),
    },
)

bus.connect()

# Enable torque - this calls our fixed enable_torque() method
print("Calling enable_torque() - this should set Lock=0 with our fix...")
bus.enable_torque()

print("\nReading Lock and Torque_Enable values from all motors:\n")
print("Motor              | Lock | Torque | Expected")
print("-" * 50)

all_correct = True
for motor_name in bus.motors:
    lock_value = bus.read("Lock", motor_name)
    torque_value = bus.read("Torque_Enable", motor_name)
    
    expected_lock = 0  # Should be 0 with our fix
    expected_torque = 1  # Should be 1 (enabled)
    
    status = "✅" if (lock_value == expected_lock and torque_value == expected_torque) else "❌"
    
    print(f"{motor_name:18} | {lock_value:4} | {torque_value:6} | Lock=0, Torque=1 {status}")
    
    if lock_value != expected_lock or torque_value != expected_torque:
        all_correct = False

bus.disconnect()

print("\n" + "="*50)
if all_correct:
    print("✅ SUCCESS! The Lock fix IS WORKING!")
    print("   All motors have Lock=0 and Torque=1")
    print("\n   This proves enable_torque() is setting Lock=0 correctly.")
else:
    print("❌ PROBLEM! The Lock fix may NOT be working!")
    print("   Some motors have incorrect Lock or Torque values.")
    print("\n   The code change might not be active, or there's another issue.")
print("="*50)

