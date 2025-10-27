#!/usr/bin/env python3
"""
Test specifically for Waveshare Bus Servo Adapter v1.1 issues
"""
import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

PORT = "/dev/tty.usbmodem5A7A0574331"  # Follower arm

print("=" * 70)
print("WAVESHARE BUS SERVO ADAPTER V1.1 TEST")
print("=" * 70)
print("Jumper: USB-SERVO set to B (external power) ✓")
print("Power: 12V 5A connected")

bus = FeetechMotorsBus(
    port=PORT,
    motors={"gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100)},
)

bus.connect()

# The issue might be that Lock=1 is a HARDWARE write-protect on Waveshare
print("\n" + "=" * 70)
print("ATTEMPTING DIFFERENT UNLOCK SEQUENCE")
print("=" * 70)

# Method 1: Try writing to EPROM with specific sequence
print("\n1. Disable torque completely...")
bus.disable_torque("gripper")
time.sleep(0.5)

print("2. Write Lock=55 first (unlock code for some boards)...")
try:
    bus.write("Lock", "gripper", 55, normalize=False)
    time.sleep(0.1)
except:
    pass

print("3. Write Lock=0 (actual unlock)...")
bus.write("Lock", "gripper", 0, normalize=False)
time.sleep(0.1)

print("4. Write Operating_Mode...")
bus.write("Operating_Mode", "gripper", 0, normalize=False)

print("5. Set all protections to max...")
bus.write("Max_Temperature_Limit", "gripper", 80, normalize=False)
bus.write("Max_Voltage_Limit", "gripper", 140, normalize=False)
bus.write("Min_Voltage_Limit", "gripper", 60, normalize=False)
bus.write("Max_Torque_Limit", "gripper", 1000, normalize=False)

print("6. Enable torque...")
bus.enable_torque("gripper")
time.sleep(0.5)

lock = bus.read("Lock", "gripper", normalize=False)
print(f"\nLock status: {lock}")

# Try a different approach - write directly without checking Lock
print("\n" + "=" * 70)
print("FORCE WRITE ATTEMPT (IGNORE LOCK)")
print("=" * 70)

initial_pos = bus.read("Present_Position", "gripper", normalize=False)
print(f"Current position: {initial_pos}")

# Try writing Goal_Position multiple times rapidly
print("\nSending rapid position commands...")
target = initial_pos + 300
for i in range(5):
    bus.write("Goal_Position", "gripper", target, normalize=False)
    time.sleep(0.1)
    
pos = bus.read("Present_Position", "gripper", normalize=False)
current = bus.read("Present_Current", "gripper", normalize=False)
print(f"After rapid writes: Pos={pos}, Current={current}")

if abs(pos - initial_pos) < 50:
    print("\n" + "=" * 70)
    print("CRITICAL HARDWARE CHECKS")
    print("=" * 70)
    print("\n1. CHECK THE SERVO POWER CONNECTION:")
    print("   - The 12V power should connect to the screw terminals")
    print("   - Usually labeled 'VM+' and 'VM-' or 'SERVO+' and 'GND'")
    print("   - NOT the USB port")
    print("")
    print("2. CHECK THE GROUND CONNECTION:")
    print("   - The power supply GND MUST connect to the board's GND")
    print("   - This creates a common ground with USB")
    print("")
    print("3. MEASURE VOLTAGE AT THE SERVO CONNECTOR:")
    print("   - Use a multimeter between red and brown servo wires")
    print("   - Should read 12V when powered")
    print("   - If 0V, the board isn't routing power to servos")
    print("")
    print("4. TRY A DIFFERENT SERVO PORT:")
    print("   - The board might have dead ports")
    print("   - Try connecting the gripper to port 1 instead of 6")
    print("")
    print("5. THE NUCLEAR OPTION:")
    print("   - Connect the leader arm to this Waveshare board")
    print("   - Run: python test.py (after changing port)")
    print("   - If leader also fails = board hardware issue")
    print("   - If leader works = follower servo issue")

bus.disconnect()
print("\n✓ Disconnected")



