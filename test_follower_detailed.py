#!/usr/bin/env python3
"""
Detailed diagnostic for follower arm movement issues
"""
import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus, OperatingMode

PORT = "/dev/tty.usbmodem5A7A0562271"  # Follower arm

print("=" * 70)
print("DETAILED FOLLOWER ARM DIAGNOSTIC")
print("=" * 70)

bus = FeetechMotorsBus(
    port=PORT,
    motors={"gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100)},
)

bus.connect()
print("✓ Connected!")

# Check all relevant parameters
print("\n" + "=" * 70)
print("MOTOR STATUS BEFORE FIXES")
print("=" * 70)

params_to_check = [
    ("Operating_Mode", False),
    ("Torque_Enable", False),
    ("Lock", False),
    ("Present_Position", False),
    ("Goal_Position", False),
    ("Max_Position_Limit", False),
    ("Min_Position_Limit", False),
]

print(f"{'Parameter':<25} | Value")
print("-" * 70)
for param, normalize in params_to_check:
    try:
        value = bus.read(param, "gripper", normalize=normalize)
        print(f"{param:<25} | {value}")
    except Exception as e:
        print(f"{param:<25} | ERROR: {e}")

# Now fix the configuration
print("\n" + "=" * 70)
print("APPLYING FIXES")
print("=" * 70)

print("1. Disabling torque...")
bus.disable_torque("gripper")

print("2. Setting Operating_Mode to POSITION (0)...")
bus.write("Operating_Mode", "gripper", OperatingMode.POSITION.value, normalize=False)

print("3. Setting Lock to 0 (unlocked)...")
bus.write("Lock", "gripper", 0, normalize=False)

print("4. Checking position limits...")
min_pos = bus.read("Min_Position_Limit", "gripper", normalize=False)
max_pos = bus.read("Max_Position_Limit", "gripper", normalize=False)
print(f"   Min: {min_pos}, Max: {max_pos}")
if min_pos == max_pos:
    print("   ⚠️  Limits are the same! Setting to full range...")
    bus.write("Min_Position_Limit", "gripper", 0, normalize=False)
    bus.write("Max_Position_Limit", "gripper", 4095, normalize=False)

print("5. Enabling torque...")
bus.enable_torque("gripper")
time.sleep(0.2)

# Verify fixes
print("\n" + "=" * 70)
print("MOTOR STATUS AFTER FIXES")
print("=" * 70)

print(f"{'Parameter':<25} | Value")
print("-" * 70)
for param, normalize in params_to_check:
    try:
        value = bus.read(param, "gripper", normalize=normalize)
        print(f"{param:<25} | {value}")
    except Exception as e:
        print(f"{param:<25} | ERROR: {e}")

# Now try to move
print("\n" + "=" * 70)
print("MOVEMENT TEST")
print("=" * 70)

initial_pos = bus.read("Present_Position", "gripper", normalize=False)
print(f"Initial position: {initial_pos}")

print("\nAttempting to move +300 steps...")
target = initial_pos + 300
bus.write("Goal_Position", "gripper", target, normalize=False)
print(f"Goal set to: {target}")

print("Waiting 2 seconds...")
time.sleep(2.0)

final_pos = bus.read("Present_Position", "gripper", normalize=False)
moved = abs(final_pos - initial_pos)

print(f"Final position: {final_pos}")
print(f"Movement: {moved} steps")

if moved > 50:
    print("\n✓ SUCCESS! Motor is moving!")
    
    print("\nReturning to initial position...")
    bus.write("Goal_Position", "gripper", initial_pos, normalize=False)
    time.sleep(1.5)
    
    print("\nTesting opposite direction (-300 steps)...")
    target = initial_pos - 300
    bus.write("Goal_Position", "gripper", target, normalize=False)
    time.sleep(2.0)
    final_pos = bus.read("Present_Position", "gripper", normalize=False)
    print(f"Position: {final_pos} (moved {abs(final_pos - initial_pos)} steps)")
    
    print("\nReturning to initial position...")
    bus.write("Goal_Position", "gripper", initial_pos, normalize=False)
    time.sleep(1.5)
    
    print("\n" + "=" * 70)
    print("✓ FOLLOWER ARM IS WORKING!")
    print("=" * 70)
    print("You can now use test_gripper.py or other control scripts.")
else:
    print("\n✗ PROBLEM: Motor still not moving")
    print("\nPossible issues:")
    print("1. Motor might be physically stuck or blocked")
    print("2. There might be a hardware issue")
    print("3. Check if you can manually move the gripper (with torque off)")

bus.disconnect()
print("\n✓ Disconnected")


