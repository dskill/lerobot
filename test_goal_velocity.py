#!/usr/bin/env python3

"""
Test if setting Goal_Velocity enables motor movement.
Hypothesis: Motors are locked in position (Lock=1 correct) but have no velocity set.
"""

import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

FOLLOWER_PORT = "/dev/tty.usbmodem5A7A0562271"

print("="*70)
print("TEST: Does setting Goal_Velocity enable movement?")
print("="*70)
print()

bus = FeetechMotorsBus(
    port=FOLLOWER_PORT,
    motors={
        "gripper": Motor(6, "sts3215", MotorNormMode.RANGE_M100_100),
    },
)

bus.connect()
print("✅ Connected to follower arm (motor 6 - gripper)")

# Load calibration if it exists, otherwise use raw values
calibration_path = "/Users/drew/.cache/huggingface/lerobot/calibration/robots/so101_follower/None.json"
try:
    import json
    with open(calibration_path, 'r') as f:
        calibration_data = json.load(f)
        if "gripper" in calibration_data:
            from lerobot.motors import MotorCalibration
            bus.calibration = {
                "gripper": MotorCalibration(**calibration_data["gripper"])
            }
            print("✅ Loaded calibration data")
        else:
            print("⚠️  No gripper calibration found, will use raw values")
except FileNotFoundError:
    print("⚠️  No calibration file found, will use raw values")
print()

# Revert to Lock=1 (the correct setting)
print("Setting Lock=1 (correct setting)...")
bus.write("Torque_Enable", "gripper", 1)
bus.write("Lock", "gripper", 1)
print()

# Read current state using address lookups
print("Current motor state:")
from lerobot.motors.motors_bus import get_address
model = bus.motors["gripper"].model

addr, length = get_address(bus.model_ctrl_table, model, "Present_Position")
start_pos_raw = bus._read(addr, length, 6)[0]

addr, length = get_address(bus.model_ctrl_table, model, "Lock")
lock = bus._read(addr, length, 6)[0]

addr, length = get_address(bus.model_ctrl_table, model, "Torque_Enable")
torque = bus._read(addr, length, 6)[0]

addr, length = get_address(bus.model_ctrl_table, model, "Goal_Velocity")
goal_vel = bus._read(addr, length, 6)[0]

addr, length = get_address(bus.model_ctrl_table, model, "Acceleration")
acceleration = bus._read(addr, length, 6)[0]

start_pos = start_pos_raw

print(f"  Present_Position: {start_pos}")
print(f"  Lock: {lock}")
print(f"  Torque_Enable: {torque}")
print(f"  Goal_Velocity: {goal_vel}")
print(f"  Acceleration: {acceleration}")
print()

# Test 1: Try to move WITHOUT setting Goal_Velocity (current behavior)
print("-" * 70)
print("TEST 1: Move WITHOUT Goal_Velocity (current behavior)")
print("-" * 70)

target_pos_raw = start_pos_raw + 300
print(f"Writing Goal_Position = {target_pos_raw} (raw) (no Goal_Velocity set)")

addr, length = get_address(bus.model_ctrl_table, model, "Goal_Position")
bus._write(addr, length, 6, target_pos_raw)

time.sleep(2)

addr, length = get_address(bus.model_ctrl_table, model, "Present_Position")
end_pos_raw = bus._read(addr, length, 6)[0]

addr, length = get_address(bus.model_ctrl_table, model, "Present_Current")
current = bus._read(addr, length, 6)[0]

addr, length = get_address(bus.model_ctrl_table, model, "Moving")
moving = bus._read(addr, length, 6)[0]

end_pos = end_pos_raw

print(f"After 2 seconds:")
print(f"  Present_Position: {end_pos} (delta: {end_pos - start_pos})")
print(f"  Present_Current: {current}")
print(f"  Moving: {moving}")

test1_moved = abs(end_pos_raw - start_pos_raw) > 10
print(f"  Result: {'✅ MOVED' if test1_moved else '❌ NO MOVEMENT'}")
print()

# Return to start
addr, length = get_address(bus.model_ctrl_table, model, "Goal_Position")
bus._write(addr, length, 6, start_pos_raw)
time.sleep(2)

# Test 2: Try to move WITH Goal_Velocity set
print("-" * 70)
print("TEST 2: Move WITH Goal_Velocity set")
print("-" * 70)

addr, length = get_address(bus.model_ctrl_table, model, "Present_Position")
start_pos_raw = bus._read(addr, length, 6)[0]

# Set a reasonable velocity (e.g., 200 out of ~4096 range)
print(f"Setting Goal_Velocity = 200")
addr, length = get_address(bus.model_ctrl_table, model, "Goal_Velocity")
bus._write(addr, length, 6, 200)

# Verify it was set
goal_vel_readback = bus._read(addr, length, 6)[0]
print(f"Goal_Velocity readback: {goal_vel_readback}")

target_pos_raw = start_pos_raw + 300
print(f"Writing Goal_Position = {target_pos_raw} (raw)")
addr, length = get_address(bus.model_ctrl_table, model, "Goal_Position")
bus._write(addr, length, 6, target_pos_raw)

time.sleep(2)

addr, length = get_address(bus.model_ctrl_table, model, "Present_Position")
end_pos_raw = bus._read(addr, length, 6)[0]

addr, length = get_address(bus.model_ctrl_table, model, "Present_Current")
current = bus._read(addr, length, 6)[0]

addr, length = get_address(bus.model_ctrl_table, model, "Moving")
moving = bus._read(addr, length, 6)[0]

end_pos = end_pos_raw

print(f"After 2 seconds:")
print(f"  Present_Position: {end_pos} (delta: {end_pos - start_pos})")
print(f"  Present_Current: {current}")
print(f"  Moving: {moving}")

test2_moved = abs(end_pos_raw - start_pos_raw) > 10
print(f"  Result: {'✅ MOVED' if test2_moved else '❌ NO MOVEMENT'}")
print()

# Test 3: Try with HIGHER velocity
if not test2_moved:
    print("-" * 70)
    print("TEST 3: Move with HIGHER Goal_Velocity")
    print("-" * 70)
    
    addr, length = get_address(bus.model_ctrl_table, model, "Goal_Position")
    bus._write(addr, length, 6, start_pos_raw)
    time.sleep(2)
    
    addr, length = get_address(bus.model_ctrl_table, model, "Present_Position")
    start_pos_raw = bus._read(addr, length, 6)[0]
    
    print(f"Setting Goal_Velocity = 1000")
    addr, length = get_address(bus.model_ctrl_table, model, "Goal_Velocity")
    bus._write(addr, length, 6, 1000)
    
    target_pos_raw = start_pos_raw + 300
    print(f"Writing Goal_Position = {target_pos_raw} (raw)")
    addr, length = get_address(bus.model_ctrl_table, model, "Goal_Position")
    bus._write(addr, length, 6, target_pos_raw)
    
    time.sleep(3)
    
    addr, length = get_address(bus.model_ctrl_table, model, "Present_Position")
    end_pos_raw = bus._read(addr, length, 6)[0]
    
    addr, length = get_address(bus.model_ctrl_table, model, "Present_Current")
    current = bus._read(addr, length, 6)[0]
    
    addr, length = get_address(bus.model_ctrl_table, model, "Moving")
    moving = bus._read(addr, length, 6)[0]
    
    end_pos = end_pos_raw
    
    print(f"After 3 seconds:")
    print(f"  Present_Position: {end_pos} (delta: {end_pos - start_pos})")
    print(f"  Present_Current: {current}")
    print(f"  Moving: {moving}")
    
    test3_moved = abs(end_pos_raw - start_pos_raw) > 10
    print(f"  Result: {'✅ MOVED' if test3_moved else '❌ NO MOVEMENT'}")
    print()

bus.disconnect()

print("="*70)
print("CONCLUSION:")
print("="*70)

if test1_moved:
    print("⚠️  Motors move even WITHOUT Goal_Velocity set!")
    print("   Goal_Velocity is not the issue.")
elif test2_moved or (not test1_moved and test2_moved):
    print("🎉 BREAKTHROUGH!")
    print("   Setting Goal_Velocity ENABLES movement!")
    print()
    print("   The fix is to set Goal_Velocity when writing Goal_Position.")
    print("   Lock=1 is correct (engages motor).")
elif not test2_moved:
    print("❌ Goal_Velocity didn't help either.")
    print("   The problem is something else entirely.")
    print()
    print("   Next things to try:")
    print("   - Check Goal_Time parameter")
    print("   - Check Operating_Mode (should be 0 for position)")
    print("   - Hardware issue (Waveshare board)")

print("="*70)

