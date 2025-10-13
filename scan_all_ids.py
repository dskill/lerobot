#!/usr/bin/env python3
"""
Scan for ANY motor IDs (1-50) on the connected port
"""
from lerobot.motors.feetech import FeetechMotorsBus

PORT = "/dev/tty.usbmodem5A7A0574331"

print("=" * 70)
print("SCANNING FOR ANY MOTOR IDS (1-50)")
print("=" * 70)
print(f"Port: {PORT}")

bus = FeetechMotorsBus(port=PORT, motors={})
bus._connect(handshake=False)
print("✓ Bus connected\n")

print("Scanning for motors...")
found_motors = {}

for motor_id in range(1, 51):
    try:
        model = bus.ping(motor_id, num_retry=0)
        if model:
            found_motors[motor_id] = model
            print(f"  ✓ Found motor ID {motor_id}: Model #{model}")
    except:
        pass
    
    # Show progress every 10 IDs
    if motor_id % 10 == 0:
        print(f"  ...scanned up to ID {motor_id}")

bus.port_handler.closePort()

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if found_motors:
    print(f"Found {len(found_motors)} motor(s):")
    for id_, model in found_motors.items():
        print(f"  ID {id_}: Model #{model}")
else:
    print("No motors found on any ID (1-50)")
    print("\nThis means:")
    print("1. The arm is not powered")
    print("2. The motors are on different IDs > 50")
    print("3. Communication issue with this port")

