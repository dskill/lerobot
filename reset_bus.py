#!/usr/bin/env python3

"""
Reset the motor bus - helps when motors aren't detected.
"""

import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

FOLLOWER_PORT = "/dev/tty.usbmodem5A7A0562271"

print("Attempting to reset motor bus...")
print(f"Port: {FOLLOWER_PORT}")
print()

try:
    # Try to connect and immediately disconnect
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
    
    print("Connecting...")
    bus.connect()
    print("✅ Connected")
    
    print("Disconnecting...")
    bus.disconnect()
    print("✅ Disconnected")
    
    print()
    print("Bus reset successful. Wait 3 seconds and try calibration again.")
    time.sleep(3)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("If this doesn't work, try:")
    print("1. Power cycle the follower arm (unplug power, wait 5s, plug back in)")
    print("2. Replug the USB cable")
    print("3. Check if another program is using the port")

