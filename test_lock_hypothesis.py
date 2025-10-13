#!/usr/bin/env python3

"""
Test if Lock=1 actually prevents motor movement.
This will help us determine if our "fix" was actually fixing anything.
"""

import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

FOLLOWER_PORT = "/dev/tty.usbmodem5A7A0562271"

print("="*60)
print("HYPOTHESIS TEST: Does Lock=1 prevent motor movement?")
print("="*60)
print()

bus = FeetechMotorsBus(
    port=FOLLOWER_PORT,
    motors={
        "test_motor": Motor(6, "sts3215", MotorNormMode.RANGE_M100_100),  # Using gripper motor
    },
)

bus.connect()
print("✅ Connected to follower arm (using motor 6 - gripper)")
print()

# Test 1: Lock=0, try to move
print("-" * 60)
print("TEST 1: Lock=0 (unlocked), Torque=1 (enabled)")
print("-" * 60)

bus.write("Torque_Enable", "test_motor", 1)
bus.write("Lock", "test_motor", 0)

start_pos = bus.read("Present_Position", "test_motor")
print(f"Starting position: {start_pos}")

target_pos = start_pos + 200
print(f"Writing Goal_Position: {target_pos}")
bus.write("Goal_Position", "test_motor", target_pos)

print("Waiting 2 seconds...")
time.sleep(2)

end_pos = bus.read("Present_Position", "test_motor")
current = bus.read("Present_Current", "test_motor")
moving = bus.read("Moving", "test_motor")

print(f"End position: {end_pos}")
print(f"Current: {current}")
print(f"Moving flag: {moving}")
print(f"Movement delta: {end_pos - start_pos}")

test1_moved = abs(end_pos - start_pos) > 10
print(f"Result: {'✅ MOTOR MOVED' if test1_moved else '❌ MOTOR DID NOT MOVE'}")
print()

# Return to start
bus.write("Goal_Position", "test_motor", start_pos)
time.sleep(2)

# Test 2: Lock=1, try to move
print("-" * 60)
print("TEST 2: Lock=1 (LOCKED), Torque=1 (enabled)")
print("-" * 60)

bus.write("Torque_Enable", "test_motor", 1)
bus.write("Lock", "test_motor", 1)

start_pos = bus.read("Present_Position", "test_motor")
print(f"Starting position: {start_pos}")

# Verify Lock was actually set
lock_readback = bus.read("Lock", "test_motor")
print(f"Lock readback: {lock_readback} (should be 1)")

target_pos = start_pos + 200
print(f"Writing Goal_Position: {target_pos}")
bus.write("Goal_Position", "test_motor", target_pos)

print("Waiting 2 seconds...")
time.sleep(2)

end_pos = bus.read("Present_Position", "test_motor")
current = bus.read("Present_Current", "test_motor")
moving = bus.read("Moving", "test_motor")

print(f"End position: {end_pos}")
print(f"Current: {current}")
print(f"Moving flag: {moving}")
print(f"Movement delta: {end_pos - start_pos}")

test2_moved = abs(end_pos - start_pos) > 10
print(f"Result: {'✅ MOTOR MOVED' if test2_moved else '❌ MOTOR DID NOT MOVE'}")
print()

# Cleanup - unlock
bus.write("Lock", "test_motor", 0)
bus.disconnect()

# Analysis
print("="*60)
print("ANALYSIS")
print("="*60)
print()

if test1_moved and not test2_moved:
    print("✅ HYPOTHESIS CONFIRMED!")
    print("   Lock=1 DOES prevent motor movement")
    print("   Lock=0 allows motor movement")
    print()
    print("   Conclusion: Our fix (Lock=1 → Lock=0) is CORRECT!")
    print()
    print("   BUT: This means the follower arm issue is NOT about Lock")
    print("   Something else is preventing movement even with Lock=0")
    
elif not test1_moved and not test2_moved:
    print("❌ HYPOTHESIS REJECTED!")
    print("   Motor doesn't move with Lock=0 OR Lock=1")
    print()
    print("   Conclusion: Lock parameter is NOT the problem!")
    print("   The real issue is preventing ALL movement regardless of Lock")
    print()
    print("   Possible causes:")
    print("   - Power supply issue")
    print("   - Firmware protection mechanism")
    print("   - Missing initialization parameter")
    print("   - Hardware problem with Waveshare board")
    
elif test1_moved and test2_moved:
    print("⚠️  SURPRISING RESULT!")
    print("   Motor moves with BOTH Lock=0 AND Lock=1")
    print()
    print("   Conclusion: Lock=1 does NOT prevent movement!")
    print("   Our original assumption was WRONG")
    print()
    print("   This would explain why nobody reported the 'bug'")
    print("   - Lock might mean something different than we thought")
    print("   - The follower arm issue is completely unrelated to Lock")
    
else:
    print("🤔 UNEXPECTED RESULT!")
    print("   Motor moves with Lock=1 but NOT with Lock=0")
    print()
    print("   This is the opposite of what we expected!")
    print("   Lock might have inverted logic or serve a different purpose")

print()
print("="*60)

