#!/usr/bin/env python3
"""
Unlock the motor and set proper limits
"""
import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus, OperatingMode

PORT = "/dev/tty.usbmodem5A7A0562271"  # Follower arm

print("=" * 70)
print("UNLOCKING MOTOR AND FIXING LIMITS")
print("=" * 70)

bus = FeetechMotorsBus(
    port=PORT,
    motors={"gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100)},
)

bus.connect()
print("✓ Connected!")

# The Lock parameter needs to be set with torque DISABLED
print("\n1. Disabling torque to modify EEPROM settings...")
bus.disable_torque("gripper")

print("2. Setting position limits to full range (0-4095)...")
bus.write("Min_Position_Limit", "gripper", 0, normalize=False)
bus.write("Max_Position_Limit", "gripper", 4095, normalize=False)

print("3. Setting Operating_Mode to POSITION...")
bus.write("Operating_Mode", "gripper", OperatingMode.POSITION.value, normalize=False)

print("4. UNLOCKING motor (Lock = 0)...")
bus.write("Lock", "gripper", 0, normalize=False)
time.sleep(0.2)

# Verify it's unlocked
lock_status = bus.read("Lock", "gripper", normalize=False)
print(f"   Lock status: {lock_status} {'✓ UNLOCKED' if lock_status == 0 else '✗ STILL LOCKED'}")

print("\n5. Enabling torque...")
bus.enable_torque("gripper")
time.sleep(0.3)

# Check all settings
print("\n" + "=" * 70)
print("CURRENT SETTINGS")
print("=" * 70)
print(f"Operating_Mode:       {bus.read('Operating_Mode', 'gripper', normalize=False)}")
print(f"Torque_Enable:        {bus.read('Torque_Enable', 'gripper', normalize=False)}")
print(f"Lock:                 {bus.read('Lock', 'gripper', normalize=False)}")
print(f"Min_Position_Limit:   {bus.read('Min_Position_Limit', 'gripper', normalize=False)}")
print(f"Max_Position_Limit:   {bus.read('Max_Position_Limit', 'gripper', normalize=False)}")

initial_pos = bus.read("Present_Position", "gripper", normalize=False)
print(f"Present_Position:     {initial_pos}")

# Test movement
print("\n" + "=" * 70)
print("MOVEMENT TEST")
print("=" * 70)

print("\nTest 1: Moving +500 steps...")
target = initial_pos + 500
bus.write("Goal_Position", "gripper", target, normalize=False)
print(f"  Goal: {target}")
time.sleep(2.0)
pos1 = bus.read("Present_Position", "gripper", normalize=False)
print(f"  Result: {pos1} (moved {abs(pos1 - initial_pos)} steps)")

if abs(pos1 - initial_pos) > 50:
    print("  ✓ SUCCESS!")
    
    print("\nTest 2: Moving -500 steps from initial...")
    target = initial_pos - 500
    bus.write("Goal_Position", "gripper", target, normalize=False)
    print(f"  Goal: {target}")
    time.sleep(2.0)
    pos2 = bus.read("Present_Position", "gripper", normalize=False)
    print(f"  Result: {pos2} (moved {abs(pos2 - initial_pos)} steps)")
    
    print("\nTest 3: Returning to initial position...")
    bus.write("Goal_Position", "gripper", initial_pos, normalize=False)
    time.sleep(1.5)
    pos3 = bus.read("Present_Position", "gripper", normalize=False)
    print(f"  Result: {pos3}")
    
    print("\n" + "=" * 70)
    print("✓✓✓ MOTOR IS WORKING! ✓✓✓")
    print("=" * 70)
    print("\nYour follower arm is now ready!")
    print("You can run: python test_gripper.py")
else:
    print("  ✗ Still not moving")
    print("\n  Additional diagnostics:")
    print(f"    Goal_Position:  {bus.read('Goal_Position', 'gripper', normalize=False)}")
    print(f"    Moving status:  {bus.read('Moving', 'gripper', normalize=False)}")
    print(f"    Present_Load:   {bus.read('Present_Load', 'gripper', normalize=False)}")
    print(f"    Present_Current:{bus.read('Present_Current', 'gripper', normalize=False)}")

bus.disconnect()
print("\n✓ Disconnected")




