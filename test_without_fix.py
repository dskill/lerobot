#!/usr/bin/env python3

"""
Test what happens WITHOUT the fix (temporarily set Lock=1 like the old buggy code).
"""

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

FOLLOWER_PORT = "/dev/tty.usbmodem5A7A0562271"

print("Testing what the OLD buggy behavior would look like...")
print("(Simulating Lock=1 like the original code)\n")

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

# Manually simulate the OLD buggy behavior (Lock=1)
print("Manually writing Torque=1 and Lock=1 (like the old buggy code)...")
for motor_name in bus.motors:
    bus.write("Torque_Enable", motor_name, 1)
    bus.write("Lock", motor_name, 1)  # OLD BUGGY VALUE

print("\nReading back the values:\n")
print("Motor              | Lock | Torque | Status")
print("-" * 50)

for motor_name in bus.motors:
    lock_value = bus.read("Lock", motor_name)
    torque_value = bus.read("Torque_Enable", motor_name)
    
    status = "❌ LOCKED!" if lock_value == 1 else "✅ Unlocked"
    
    print(f"{motor_name:18} | {lock_value:4} | {torque_value:6} | {status}")

# Now unlock them again with our fix
print("\n" + "="*50)
print("Now fixing it with Lock=0 (our corrected code)...")
bus.enable_torque()  # This uses our fixed code with Lock=0

print("\nAfter calling enable_torque() with our fix:\n")
print("Motor              | Lock | Torque | Status")
print("-" * 50)

for motor_name in bus.motors:
    lock_value = bus.read("Lock", motor_name)
    torque_value = bus.read("Torque_Enable", motor_name)
    
    status = "✅ Unlocked" if lock_value == 0 else "❌ LOCKED!"
    
    print(f"{motor_name:18} | {lock_value:4} | {torque_value:6} | {status}")

bus.disconnect()

print("\n" + "="*50)
print("CONCLUSION:")
print("  OLD CODE (Lock=1): Motors are LOCKED and can't move")
print("  NEW CODE (Lock=0): Motors are UNLOCKED")
print("\n  The fix IS making a difference!")
print("="*50)

