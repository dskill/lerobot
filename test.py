#!/usr/bin/env python3
"""
Quick diagnostic tool for SO-101 robot arm
"""
import sys
from lerobot.motors.feetech import FeetechMotorsBus

# SO-101 Follower arm port
PORT = "/dev/tty.usbmodem5A7A0562271"
# Default baudrate for Feetech motors
BAUDRATE = 1_000_000
# Expected motor IDs for SO-101
EXPECTED_IDS = [1, 2, 3, 4, 5, 6]

print("=" * 60)
print("SO-101 DIAGNOSTIC TEST")
print("=" * 60)

# Step 1: Check port accessibility
print(f"\n1. Checking port: {PORT}")
try:
    import serial
    ser = serial.Serial(PORT, BAUDRATE, timeout=0.5)
    print(f"   ✓ Port is accessible")
    ser.close()
except Exception as e:
    print(f"   ✗ Cannot open port: {e}")
    print("\n   TROUBLESHOOTING:")
    print("   - Is the USB cable properly connected?")
    print("   - Try unplugging and replugging the USB cable")
    print("   - Check if another program is using this port")
    sys.exit(1)

# Step 2: Try to connect to the bus
print(f"\n2. Connecting to Feetech bus at {BAUDRATE} baud...")
try:
    # Create a bus without motors first (for scanning)
    bus = FeetechMotorsBus(PORT, {})
    bus._connect(handshake=False)
    print(f"   ✓ Bus connected")
except Exception as e:
    print(f"   ✗ Failed to connect: {e}")
    sys.exit(1)

# Step 3: Ping individual motor IDs
print(f"\n3. Pinging motors (IDs {EXPECTED_IDS})...")
found_motors = {}
for motor_id in EXPECTED_IDS:
    try:
        model_number = bus.ping(motor_id, num_retry=2)
        if model_number:
            print(f"   ✓ Motor ID {motor_id}: Found (model #{model_number})")
            found_motors[motor_id] = model_number
        else:
            print(f"   ✗ Motor ID {motor_id}: No response")
    except Exception as e:
        print(f"   ✗ Motor ID {motor_id}: Error - {e}")

bus.port_handler.closePort()

# Step 4: Summary
print(f"\n4. Summary")
print(f"   Found {len(found_motors)}/{len(EXPECTED_IDS)} motors")

if len(found_motors) == 0:
    print("\n" + "=" * 60)
    print("NO MOTORS FOUND!")
    print("=" * 60)
    print("\nTROUBLESHOOTING:")
    print("1. ⚡ Is the robot POWERED ON? (needs external power supply)")
    print("2. 🔌 Check all cable connections (USB + power)")
    print("3. 🔄 Try restarting: power off, wait 5s, power on")
    print("4. 📡 The motors need to be daisy-chained with 3-pin cables")
    print("5. 🔧 If new motors, they may need initial setup with FeetechServoConfig tool")
elif len(found_motors) < len(EXPECTED_IDS):
    print(f"\n   ⚠️  WARNING: Missing {len(EXPECTED_IDS) - len(found_motors)} motors!")
    missing = [id for id in EXPECTED_IDS if id not in found_motors]
    print(f"   Missing IDs: {missing}")
else:
    print("\n   ✓ All motors detected! Robot is ready to use.")
    print("\n   Next steps:")
    print("   - Run: lerobot-find-port")
    print("   - Or try the teleoperate/record examples")
