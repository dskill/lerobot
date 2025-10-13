#!/usr/bin/env python3
"""
Simple control test for SO-101 robot arm
Reads current positions and allows basic movement
"""
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

PORT = "/dev/tty.usbmodem5A7A0574331"

print("=" * 60)
print("SO-101 CONTROL TEST")
print("=" * 60)

# Create the motor bus with all 6 motors
bus = FeetechMotorsBus(
    port=PORT,
    motors={
        "shoulder_pan": Motor(1, "sts3215", MotorNormMode.DEGREES),
        "shoulder_lift": Motor(2, "sts3215", MotorNormMode.DEGREES),
        "elbow_flex": Motor(3, "sts3215", MotorNormMode.DEGREES),
        "wrist_flex": Motor(4, "sts3215", MotorNormMode.DEGREES),
        "wrist_roll": Motor(5, "sts3215", MotorNormMode.DEGREES),
        "gripper": Motor(6, "sts3215", MotorNormMode.DEGREES),
    },
)

print("\nConnecting to robot...")
bus.connect()
print("✓ Connected!")

# Read current positions
print("\n" + "=" * 60)
print("CURRENT POSITIONS (in degrees)")
print("=" * 60)
positions = bus.sync_read("Present_Position")
for motor_name, pos in positions.items():
    print(f"  {motor_name:20s}: {pos:7.2f}°")

# Read velocities
print("\n" + "=" * 60)
print("CURRENT VELOCITIES")
print("=" * 60)
velocities = bus.sync_read("Present_Velocity", normalize=False)
for motor_name, vel in velocities.items():
    print(f"  {motor_name:20s}: {vel}")

# Check if torque is enabled
print("\n" + "=" * 60)
print("TORQUE STATUS")
print("=" * 60)
for motor_name in bus.motors.keys():
    torque = bus.read("Torque_Enable", motor_name, normalize=False)
    status = "ENABLED ✓" if torque else "DISABLED ✗"
    print(f"  {motor_name:20s}: {status}")

print("\n" + "=" * 60)
print("INFO")
print("=" * 60)
print("Your SO-101 is working! You can now:")
print("  1. Use lerobot-record to record demonstrations")
print("  2. Use lerobot-replay to replay recorded data")
print("  3. Use lerobot-teleoperate for teleoperation")
print("  4. Train policies with your recorded data")
print("\nFor safety, torque should be DISABLED when manually moving the arm.")
print("Enable torque when you want the motors to hold position or move.")

# Disconnect cleanly
bus.disconnect()
print("\n✓ Disconnected safely")

