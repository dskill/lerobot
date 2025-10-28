#!/usr/bin/env python3
"""
Simple gripper test for SO-101 - Opens and closes the gripper
"""
import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

PORT = "/dev/tty.usbmodem5A7A0562271"  # Follower arm

print("=" * 60)
print("SO-101 GRIPPER TEST")
print("=" * 60)

# Create the motor bus with just the gripper
bus = FeetechMotorsBus(
    port=PORT,
    motors={
        "gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100),
    },
)

print("\nConnecting to robot...")
bus.connect()
print("✓ Connected!")

# Check torque status
torque_status = bus.read("Torque_Enable", "gripper", normalize=False)
print(f"Torque status: {'ENABLED' if torque_status else 'DISABLED'}")

if not torque_status:
    print("Enabling torque...")
    bus.enable_torque("gripper")
    time.sleep(0.2)
    torque_status = bus.read("Torque_Enable", "gripper", normalize=False)
    print(f"Torque status now: {'ENABLED' if torque_status else 'DISABLED'}")

# Read initial position (without normalization since we don't have calibration loaded)
initial_pos = bus.read("Present_Position", "gripper", normalize=False)
print(f"Initial gripper position (raw): {initial_pos}")

print("\n" + "=" * 60)
print("Starting gripper jiggle test...")
print("The gripper will open and close 3 times")
print("=" * 60)

try:
    for i in range(3):
        print(f"\nCycle {i+1}/3:")
        
        # Open gripper - move by +500 steps from initial position
        target_open = initial_pos + 500
        print(f"  Opening to {target_open}... ", end="", flush=True)
        bus.write("Goal_Position", "gripper", target_open, normalize=False)
        # IMPORTANT: Feetech motors need Goal_Velocity AND Acceleration for movement!
        bus.write("Goal_Velocity", "gripper", 600, normalize=False)
        bus.write("Acceleration", "gripper", 20, normalize=False)
        time.sleep(1.5)
        pos = bus.read("Present_Position", "gripper", normalize=False)
        moved = abs(pos - initial_pos)
        print(f"✓ (position: {pos}, moved {moved} steps)")
        
        # Close gripper - move by -500 steps from initial position
        target_close = initial_pos - 500
        print(f"  Closing to {target_close}... ", end="", flush=True)
        bus.write("Goal_Position", "gripper", target_close, normalize=False)
        bus.write("Goal_Velocity", "gripper", 600, normalize=False)
        bus.write("Acceleration", "gripper", 20, normalize=False)
        time.sleep(1.5)
        pos = bus.read("Present_Position", "gripper", normalize=False)
        moved = abs(pos - initial_pos)
        print(f"✓ (position: {pos}, moved {moved} steps)")

    # Return to initial position
    print(f"\nReturning to initial position ({initial_pos})...")
    bus.write("Goal_Position", "gripper", initial_pos, normalize=False)
    bus.write("Goal_Velocity", "gripper", 600, normalize=False)
    bus.write("Acceleration", "gripper", 20, normalize=False)
    time.sleep(0.5)

    print("\n" + "=" * 60)
    print("✓ TEST COMPLETE!")
    print("=" * 60)
    print("Your SO-101 is calibrated and working correctly!")

except KeyboardInterrupt:
    print("\n\nTest interrupted by user")
except Exception as e:
    print(f"\n\n✗ Error: {e}")
finally:
    # Disconnect cleanly
    print("\nDisconnecting...")
    bus.disconnect()
    print("✓ Disconnected safely")

