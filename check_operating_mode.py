#!/usr/bin/env python3

"""
Check Operating_Mode of follower motors to see if they're in the correct mode.
Operating_Mode should be 0 (POSITION) for position control.
"""

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

FOLLOWER_PORT = "/dev/tty.usbmodem5A7A0562271"

print("="*70)
print("Checking Operating_Mode of Follower Motors")
print("="*70)
print()

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
print("✅ Connected to follower arm\n")

print("Operating_Mode values:")
print("  0 = POSITION mode (correct for position control)")
print("  1 = VELOCITY mode (continuous speed)")
print("  2 = PWM mode")
print("  3 = STEP mode")
print()

print("-" * 70)
print(f"{'Motor':<20} | {'Operating_Mode':<15} | Status")
print("-" * 70)

all_correct = True
for motor_name, motor in bus.motors.items():
    from lerobot.motors.motors_bus import get_address
    
    addr, length = get_address(bus.model_ctrl_table, motor.model, "Operating_Mode")
    mode = bus._read(addr, length, motor.id)[0]
    
    status = "✅ POSITION" if mode == 0 else f"❌ Mode {mode} (should be 0)"
    print(f"{motor_name:<20} | {mode:<15} | {status}")
    
    if mode != 0:
        all_correct = False

print("-" * 70)
print()

if all_correct:
    print("✅ All motors are in POSITION mode (Operating_Mode=0)")
    print()
    print("This is CORRECT for position control.")
    print()
    print("Conclusion: Operating_Mode is not the issue.")
    print("The Goal_Velocity fix is still needed for Feetech motors.")
else:
    print("❌ Some motors are NOT in POSITION mode!")
    print()
    print("This could be the real problem!")
    print()
    print("Fixing by setting Operating_Mode=0 for all motors...")
    
    for motor_name, motor in bus.motors.items():
        addr, length = get_address(bus.model_ctrl_table, motor.model, "Operating_Mode")
        bus._write(addr, length, motor.id, 0)
        print(f"  Set {motor_name} to POSITION mode")
    
    print()
    print("✅ Fixed! All motors now in POSITION mode.")
    print()
    print("Now try teleoperation WITHOUT Goal_Velocity to see if it works.")

bus.disconnect()
print()
print("="*70)

