#!/usr/bin/env python3
"""
Check and fix torque-related parameters
"""
import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus, OperatingMode

PORT = "/dev/tty.usbmodem5A7A0562271"  # Follower arm

print("=" * 70)
print("CHECKING TORQUE SETTINGS")
print("=" * 70)

bus = FeetechMotorsBus(
    port=PORT,
    motors={"gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100)},
)

bus.connect()
print("✓ Connected!")

# Check torque-related parameters
print("\n" + "=" * 70)
print("CURRENT TORQUE SETTINGS")
print("=" * 70)

torque_params = [
    "Max_Torque_Limit",      # Maximum torque in EEPROM
    "Torque_Limit",          # Current torque limit in RAM
    "Torque_Enable",         # Whether torque is on
    "Protective_Torque",     # Protection setting
    "Overload_Torque",       # Overload threshold
    "Protection_Current",    # Current protection
]

for param in torque_params:
    try:
        value = bus.read(param, "gripper", normalize=False)
        print(f"{param:25s}: {value}")
    except Exception as e:
        print(f"{param:25s}: ERROR - {e}")

# Check other important settings
other_params = [
    "Goal_Time",
    "Acceleration",
    "P_Coefficient",
    "D_Coefficient",
    "I_Coefficient",
]

print(f"\n{'Other Settings':25s}:")
for param in other_params:
    try:
        value = bus.read(param, "gripper", normalize=False)
        print(f"{param:25s}: {value}")
    except Exception as e:
        print(f"{param:25s}: ERROR - {e}")

# Now fix the torque limits
print("\n" + "=" * 70)
print("SETTING PROPER TORQUE LIMITS")
print("=" * 70)

bus.disable_torque("gripper")

# Set torque limits (max is 1000 for STS3215)
print("Setting Max_Torque_Limit to 1000 (full power)...")
bus.write("Max_Torque_Limit", "gripper", 1000, normalize=False)

print("Setting Torque_Limit to 1000...")
bus.write("Torque_Limit", "gripper", 1000, normalize=False)

print("Setting Protection_Current to 500...")
bus.write("Protection_Current", "gripper", 500, normalize=False)

print("Setting Acceleration to 50...")
bus.write("Acceleration", "gripper", 50, normalize=False)

print("Setting Operating_Mode to POSITION...")
bus.write("Operating_Mode", "gripper", OperatingMode.POSITION.value, normalize=False)

# Try setting Lock to 0
print("Setting Lock to 0...")
bus.write("Lock", "gripper", 0, normalize=False)

bus.enable_torque("gripper")
print("Torque enabled!")
time.sleep(0.5)

# Check settings again
print("\n" + "=" * 70)
print("SETTINGS AFTER FIX")
print("=" * 70)

for param in torque_params:
    try:
        value = bus.read(param, "gripper", normalize=False)
        print(f"{param:25s}: {value}")
    except Exception as e:
        print(f"{param:25s}: ERROR - {e}")

print(f"\n{'Lock':25s}: {bus.read('Lock', 'gripper', normalize=False)}")
print(f"{'Operating_Mode':25s}: {bus.read('Operating_Mode', 'gripper', normalize=False)}")

# Movement test
print("\n" + "=" * 70)
print("MOVEMENT TEST")
print("=" * 70)

initial_pos = bus.read("Present_Position", "gripper", normalize=False)
print(f"Initial position: {initial_pos}")

print("\nSending movement command (+500 steps)...")
target = initial_pos + 500
bus.write("Goal_Position", "gripper", target, normalize=False)
print(f"Goal: {target}")

# Monitor for 3 seconds
print("\nMonitoring for 3 seconds:")
for i in range(6):
    time.sleep(0.5)
    pos = bus.read("Present_Position", "gripper", normalize=False)
    moving = bus.read("Moving", "gripper", normalize=False)
    load = bus.read("Present_Load", "gripper", normalize=False)
    current = bus.read("Present_Current", "gripper", normalize=False)
    print(f"  {i*0.5:.1f}s: Pos={pos}, Moving={moving}, Load={load}, Current={current}")

final_pos = bus.read("Present_Position", "gripper", normalize=False)
moved = abs(final_pos - initial_pos)

print(f"\nFinal position: {final_pos}")
print(f"Total movement: {moved} steps")

if moved > 50:
    print("\n" + "=" * 70)
    print("✓✓✓ SUCCESS! MOTOR IS MOVING! ✓✓✓")
    print("=" * 70)
else:
    print("\n" + "=" * 70)
    print("✗ STILL NOT MOVING")
    print("=" * 70)
    print("\nThis might indicate a hardware issue:")
    print("- Motor might be faulty")
    print("- Wiring issue preventing power delivery")
    print("- Motor controller board issue")
    print("\nTry testing a different motor (e.g., motor ID 1-5)")

bus.disconnect()
print("\n✓ Disconnected")


