#!/usr/bin/env python3
"""
Diagnose why Waveshare board won't allow writes to motors
"""
import time
from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

# Both ports for comparison
FOLLOWER_PORT = "/dev/tty.usbmodem5A7A0562271"  # Not working
LEADER_PORT = "/dev/tty.usbmodem5A7A0574331"    # Working

print("=" * 70)
print("WAVESHARE WRITE PROTECTION DIAGNOSIS")
print("=" * 70)

# Test LEADER first (known working)
print("\n1. Testing LEADER arm (known working):")
print(f"   Port: {LEADER_PORT}")

leader_bus = FeetechMotorsBus(
    port=LEADER_PORT,
    motors={"gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100)},
)
leader_bus.connect()

# Try a simple write
try:
    leader_bus.disable_torque("gripper")
    leader_bus.write("Max_Torque_Limit", "gripper", 1000, normalize=False)
    print("   ✓ Write successful on leader!")
    leader_bus.enable_torque("gripper")
except Exception as e:
    print(f"   ✗ Write failed on leader: {e}")

leader_bus.disconnect()

# Test FOLLOWER (not working)
print("\n2. Testing FOLLOWER arm (not working):")
print(f"   Port: {FOLLOWER_PORT}")

follower_bus = FeetechMotorsBus(
    port=FOLLOWER_PORT,
    motors={"gripper": Motor(6, "sts3215", MotorNormMode.RANGE_0_100)},
)
follower_bus.connect()

# Try the same write
try:
    follower_bus.disable_torque("gripper")
    print("   Torque disabled, attempting write...")
    follower_bus.write("Max_Torque_Limit", "gripper", 1000, normalize=False)
    print("   ✓ Write successful on follower!")
    follower_bus.enable_torque("gripper")
except Exception as e:
    print(f"   ✗ Write failed on follower: {e}")

# Check if it's a timeout issue
print("\n3. Testing with longer timeout:")
follower_bus.set_timeout(5000)  # 5 second timeout
try:
    follower_bus.write("Max_Torque_Limit", "gripper", 1000, normalize=False)
    print("   ✓ Write successful with longer timeout!")
except Exception as e:
    print(f"   ✗ Still fails with longer timeout: {e}")

# Try different baudrates
print("\n4. Testing different baudrates:")
follower_bus.disconnect()

for baudrate in [1_000_000, 115_200, 57_600]:
    print(f"   Testing {baudrate} baud...")
    test_bus = FeetechMotorsBus(port=FOLLOWER_PORT, motors={})
    test_bus._connect(handshake=False)
    test_bus.set_baudrate(baudrate)
    
    # Try to ping
    model = test_bus.ping(6, raise_on_error=False)
    if model:
        print(f"     ✓ Communication works at {baudrate}")
        # Try write
        try:
            test_bus.packet_handler.write1ByteTxRx(test_bus.port_handler, 6, 40, 0)  # Disable torque
            print(f"     ✓ Write works at {baudrate}!")
        except:
            print(f"     ✗ Write fails at {baudrate}")
    else:
        print(f"     ✗ No communication at {baudrate}")
    
    test_bus.port_handler.closePort()

print("\n" + "=" * 70)
print("DIAGNOSIS SUMMARY")
print("=" * 70)

print("""
If leader works but follower doesn't:
1. Different Waveshare board or configuration
2. Follower board has write-protect enabled
3. Follower motors are locked at hardware level

SOLUTION OPTIONS:
1. Swap the leader and follower connections to test if it's board-specific
2. Check for physical differences between the boards
3. Use Feetech's official debug tool to unlock the motors
4. Try a different USB cable (some only carry power, not data properly)
""")

follower_bus.disconnect()



