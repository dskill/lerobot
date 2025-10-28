#!/usr/bin/env python3
"""
Check the operating mode of Feetech servos using Vassar SDK.
Based on: https://github.com/vassar-robotics/feetech-servo-sdk/blob/d60242c8e1d17ffc97ea5723e1256a5def86414f/vassar_feetech_servo_sdk/controller.py#L882
"""

from vassar_feetech_servo_sdk.controller import ServoController

# Your follower arm port
PORT = "/dev/tty.usbmodem5A7A0562271"
BAUDRATE = 1000000
MOTOR_IDS = [1, 2, 3, 4, 5, 6]

print("=" * 70)
print("CHECKING FEETECH SERVO OPERATING MODES")
print("=" * 70)
print(f"Port: {PORT}")
print(f"Motor IDs: {MOTOR_IDS}")
print()

# Create controller
controller = ServoController(
    servo_ids=MOTOR_IDS,
    servo_type='sts',
    port=PORT,
    baudrate=BAUDRATE
)

print("Connecting...")
controller.connect()
print("✅ Connected!\n")

print("Reading Operating Modes:")
print("-" * 70)
print("Mode 0 = Position Control Mode")
print("Mode 1 = Speed Control Mode")
print("Mode 3 = PWM Control Mode (step servo mode)")
print("-" * 70)

# Access the underlying SCS bus to read operating mode directly
# Operating_Mode is at address 33 in the control table
try:
    for motor_id in MOTOR_IDS:
        # Read Operating_Mode register (address 33)
        mode = controller.scs.ReadByte(motor_id, 33)
        
        mode_name = {
            0: "Position Control (normal)",
            1: "Speed Control",
            3: "PWM Control (step servo)"
        }.get(mode[0] if isinstance(mode, tuple) else mode, f"Unknown ({mode})")
        
        if mode is not None:
            mode_value = mode[0] if isinstance(mode, tuple) else mode
            if mode_value == 0:
                status = "✅ CORRECT"
            else:
                status = "⚠️ WRONG - Should be 0!"
            print(f"Motor {motor_id}: Mode {mode_value} = {mode_name} {status}")
        else:
            print(f"Motor {motor_id}: ❌ Could not read mode")
            
except Exception as e:
    print(f"❌ Error reading modes: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("OTHER IMPORTANT REGISTERS:")
print("=" * 70)

# Check other critical registers
try:
    for motor_id in MOTOR_IDS:
        print(f"\nMotor {motor_id}:")
        
        # Torque Enable (address 40)
        torque = controller.scs.ReadByte(motor_id, 40)
        torque_val = torque[0] if isinstance(torque, tuple) else torque
        print(f"  Torque Enable: {torque_val} (0=off, 1=on)")
        
        # Lock (address 55)
        lock = controller.scs.ReadByte(motor_id, 55)
        lock_val = lock[0] if isinstance(lock, tuple) else lock
        print(f"  Lock: {lock_val} (0=EPROM writable/freespin, 1=position control)")
        
        # Goal_Velocity (address 46-47, 2 bytes)
        goal_vel = controller.scs.ReadWord(motor_id, 46)
        goal_vel_val = goal_vel[0] if isinstance(goal_vel, tuple) else goal_vel
        print(f"  Goal_Velocity: {goal_vel_val}")
        
        # Acceleration (address 41)
        accel = controller.scs.ReadByte(motor_id, 41)
        accel_val = accel[0] if isinstance(accel, tuple) else accel
        print(f"  Acceleration: {accel_val}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 70)
print("DIAGNOSIS:")
print("=" * 70)
print("For proper operation in LeRobot:")
print("  • Operating_Mode should be 0 (Position Control)")
print("  • Torque_Enable should be 1 (on)")
print("  • Lock should be 1 during operation (0 during calibration)")
print("  • Goal_Velocity should be set (e.g., 600)")
print("  • Acceleration should be set (e.g., 20-25)")

controller.disconnect()
print("\n✅ Done!")

