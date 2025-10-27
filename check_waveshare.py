#!/usr/bin/env python3
"""
Check Waveshare-specific settings and potential issues
"""
import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

PORT = "/dev/tty.usbmodem5A7A0562271"  # Follower arm with Waveshare board

print("=" * 70)
print("WAVESHARE BOARD DIAGNOSTIC")
print("=" * 70)
print("\nYou mentioned: Waveshare servo board + 12V 5A power supply")
print("This is important info!\n")

bus = FeetechMotorsBus(
    port=PORT,
    motors={"gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100)},
)

bus.connect()
print("✓ Connected!")

# Check voltage
print("\n" + "=" * 70)
print("POWER DIAGNOSTIC")
print("=" * 70)

voltage = bus.read("Present_Voltage", "gripper", normalize=False)
print(f"Present Voltage: {voltage} (raw value)")
print(f"Actual Voltage: ~{voltage/10:.1f}V")

if voltage < 110:  # Less than 11V
    print("\n⚠️  WARNING: Voltage seems LOW!")
    print("STS3215 motors need 12V to operate properly")
    print("The Waveshare board might be dropping voltage")

# Check temperature (overheating protection?)
temp = bus.read("Present_Temperature", "gripper", normalize=False)
print(f"\nPresent Temperature: {temp}°C")

# Check status register for errors
status = bus.read("Status", "gripper", normalize=False)
print(f"Status Register: {status} (0 = normal)")

# Check voltage limits
min_volt = bus.read("Min_Voltage_Limit", "gripper", normalize=False)
max_volt = bus.read("Max_Voltage_Limit", "gripper", normalize=False)
print(f"\nVoltage Limits: {min_volt} - {max_volt} (raw)")

# IMPORTANT: Check Return Delay Time (affects Waveshare communication)
return_delay = bus.read("Return_Delay_Time", "gripper", normalize=False)
print(f"Return Delay Time: {return_delay} (affects board communication)")

# Check Response Status Level
response_level = bus.read("Response_Status_Level", "gripper", normalize=False)
print(f"Response Status Level: {response_level}")

print("\n" + "=" * 70)
print("WAVESHARE-SPECIFIC FIXES")
print("=" * 70)

bus.disable_torque("gripper")

# Fix 1: Set proper Return Delay Time for Waveshare
print("\n1. Setting Return_Delay_Time to 0 (immediate response)...")
bus.write("Return_Delay_Time", "gripper", 0, normalize=False)

# Fix 2: Ensure voltage limits are appropriate
print("2. Setting voltage limits for 12V operation...")
bus.write("Min_Voltage_Limit", "gripper", 95, normalize=False)   # ~9.5V
bus.write("Max_Voltage_Limit", "gripper", 135, normalize=False)  # ~13.5V

# Fix 3: Clear any error conditions
print("3. Clearing error conditions...")
bus.write("LED_Alarm_Condition", "gripper", 0, normalize=False)
bus.write("Unloading_Condition", "gripper", 0, normalize=False)

# Fix 4: Set Operating Mode and unlock
print("4. Setting Operating_Mode and Lock...")
bus.write("Operating_Mode", "gripper", 0, normalize=False)
bus.write("Lock", "gripper", 0, normalize=False)

# Fix 5: Set proper torque
print("5. Setting torque limits...")
bus.write("Max_Torque_Limit", "gripper", 1000, normalize=False)
bus.write("Torque_Limit", "gripper", 1000, normalize=False)

bus.enable_torque("gripper")
print("\n✓ Torque enabled with Waveshare fixes")

# Test movement
print("\n" + "=" * 70)
print("MOVEMENT TEST")
print("=" * 70)

initial_pos = bus.read("Present_Position", "gripper", normalize=False)
print(f"Initial position: {initial_pos}")

print("\nAttempting movement...")
target = initial_pos + 300
bus.write("Goal_Position", "gripper", target, normalize=False)

# Monitor with more detail
for i in range(4):
    time.sleep(0.5)
    pos = bus.read("Present_Position", "gripper", normalize=False)
    current = bus.read("Present_Current", "gripper", normalize=False)
    voltage = bus.read("Present_Voltage", "gripper", normalize=False)
    status = bus.read("Status", "gripper", normalize=False)
    print(f"  {i*0.5:.1f}s: Pos={pos}, Current={current}, Volt={voltage/10:.1f}V, Status={status}")

final_pos = bus.read("Present_Position", "gripper", normalize=False)
moved = abs(final_pos - initial_pos)

if moved > 50:
    print(f"\n✓ SUCCESS! Motor moved {moved} steps!")
else:
    print(f"\n✗ Still not moving (only {moved} steps)")
    print("\n" + "=" * 70)
    print("WAVESHARE-SPECIFIC ISSUES TO CHECK")
    print("=" * 70)
    print("1. Power: Is 12V 5A actually reaching the motors?")
    print("   - Check voltage at the Waveshare board output")
    print("   - 5A might not be enough for all 6 motors under load")
    print("   ")
    print("2. Waveshare Board Settings:")
    print("   - Is there a jumper/switch for servo power?")
    print("   - Is the board in 'TTL' or 'USB' mode?")
    print("   - Some boards have write-protect jumpers")
    print("   ")
    print("3. Wiring:")
    print("   - Are motor power wires (red/brown) connected to Waveshare?")
    print("   - Signal wires (yellow/white) properly connected?")
    print("   - Ground shared between USB and power supply?")
    print("   ")
    print("4. Try the leader arm on the same Waveshare board")
    print("   - If leader works, it's a configuration issue")
    print("   - If leader also fails, it's a board/power issue")

bus.disconnect()
print("\n✓ Disconnected")



