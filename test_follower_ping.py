#!/usr/bin/env python3
"""
Quick diagnostic for follower arm
"""
import sys
from lerobot.motors.feetech import FeetechMotorsBus

PORT = "/dev/tty.usbmodem5A7A0562271"
EXPECTED_IDS = [1, 2, 3, 4, 5, 6]

print("=" * 60)
print("FOLLOWER ARM DIAGNOSTIC")
print("=" * 60)

# Step 1: Check port accessibility
print(f"\n1. Checking port: {PORT}")
try:
    import serial
    ser = serial.Serial(PORT, 1_000_000, timeout=0.5)
    print(f"   ✓ Port is accessible")
    ser.close()
except Exception as e:
    print(f"   ✗ Cannot open port: {e}")
    print("\n   TROUBLESHOOTING:")
    print("   - Is the USB cable connected?")
    print("   - Is the FOLLOWER arm powered on?")
    sys.exit(1)

# Step 2: Connect and ping
print(f"\n2. Connecting to bus...")
bus = FeetechMotorsBus(PORT, {})
bus._connect(handshake=False)
print(f"   ✓ Bus connected")

# Step 3: Ping motors
print(f"\n3. Pinging motors (IDs {EXPECTED_IDS})...")
found_motors = {}
for motor_id in EXPECTED_IDS:
    model_number = bus.ping(motor_id, num_retry=2)
    if model_number:
        print(f"   ✓ Motor ID {motor_id}: Found (model #{model_number})")
        found_motors[motor_id] = model_number
    else:
        print(f"   ✗ Motor ID {motor_id}: No response")

bus.port_handler.closePort()

# Summary
print(f"\n4. Summary")
print(f"   Found {len(found_motors)}/{len(EXPECTED_IDS)} motors")

if len(found_motors) == 0:
    print("\n" + "=" * 60)
    print("NO MOTORS FOUND!")
    print("=" * 60)
    print("\nTROUBLESHOOTING:")
    print("1. ⚡ Is the FOLLOWER arm POWERED ON?")
    print("   - Check power supply is connected and switched on")
    print("   - Look for LEDs on the motors")
    print("2. 🔌 Check cable connections:")
    print("   - USB cable fully inserted")
    print("   - 3-pin cables connecting all motors in daisy chain")
    print("3. 🔄 Try power cycling:")
    print("   - Turn off power, wait 5 seconds, turn back on")
    print("4. 🔍 Verify the correct USB port:")
    print("   - Run: python test.py")
    print("   - Make sure this is the follower, not the leader")
elif len(found_motors) < len(EXPECTED_IDS):
    print(f"\n   ⚠️  WARNING: Missing {len(EXPECTED_IDS) - len(found_motors)} motors!")
    missing = [id for id in EXPECTED_IDS if id not in found_motors]
    print(f"   Missing IDs: {missing}")
    print("\n   Check daisy chain connections for missing motors")
else:
    print("\n   ✓ All motors detected!")
    print("\n   Now run:")
    print(f"   lerobot-calibrate --robot.type=so101_follower --robot.port={PORT}")


