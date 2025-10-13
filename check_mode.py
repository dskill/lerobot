#!/usr/bin/env python3
"""
Check what mode the SO-101 arm is configured for
"""
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus, OperatingMode

PORT = "/dev/tty.usbmodem5A7A0562271"  # Follower arm

print("=" * 60)
print("SO-101 MODE CHECK")
print("=" * 60)

bus = FeetechMotorsBus(
    port=PORT,
    motors={"gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100)},
)

bus.connect()
print("✓ Connected!")

# Check operating mode
operating_mode = bus.read("Operating_Mode", "gripper", normalize=False)
mode_name = {
    0: "POSITION (Follower mode - receives commands)",
    1: "VELOCITY (Constant speed mode)",
    2: "PWM (Open-loop mode)",
    3: "STEP (Step servo mode)"
}.get(operating_mode, f"UNKNOWN ({operating_mode})")

print(f"\nOperating Mode: {mode_name}")
print(f"Torque Enable: {bus.read('Torque_Enable', 'gripper', normalize=False)}")
print(f"Lock Status: {bus.read('Lock', 'gripper', normalize=False)}")

# Check which calibration files exist
import os
cache_dir = os.path.expanduser("~/.cache/lerobot/calibration/")
if os.path.exists(cache_dir):
    print(f"\nCalibration files found:")
    for f in os.listdir(cache_dir):
        if "so101" in f.lower():
            print(f"  - {f}")
else:
    print("\nNo calibration directory found")

print("\n" + "=" * 60)
if operating_mode != OperatingMode.POSITION.value:
    print("⚠️  ISSUE FOUND!")
    print("=" * 60)
    print(f"Motor is in mode {operating_mode} (not POSITION mode)")
    print("\nThis happens when calibrated as a LEADER (for manual control)")
    print("\nTO FIX - Recalibrate as FOLLOWER:")
    print(f"  lerobot-calibrate --robot.type=so101_follower --robot.port={PORT}")
else:
    print("✓ Motor is in POSITION mode (correct for follower)")
    print("=" * 60)

bus.disconnect()

