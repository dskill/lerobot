#!/usr/bin/env python3
"""
Check and fix Feetech servo operating modes using direct scservo_sdk functions.
Based on Vassar Robotics feedback - servos might be in velocity control mode!
"""

import scservo_sdk as scs

PORT = "/dev/tty.usbmodem5A7A0562271"
BAUDRATE = 1000000
MOTOR_IDS = [1, 2, 3, 4, 5, 6]

# Register addresses for STS3215
ADDR_OPERATING_MODE = 33
ADDR_TORQUE_ENABLE = 40
ADDR_LOCK = 55
ADDR_PRESENT_POSITION = 56

print("=" * 70)
print("CHECKING AND FIXING FEETECH SERVO OPERATING MODES")
print("=" * 70)
print(f"Port: {PORT}")
print(f"Motor IDs: {MOTOR_IDS}")
print()

# Initialize port
port_handler = scs.PortHandler(PORT)

# Open port
if not port_handler.openPort():
    print("❌ Failed to open port")
    exit(1)

# Set baudrate
if not port_handler.setBaudRate(BAUDRATE):
    print("❌ Failed to set baudrate")
    exit(1)

print("✅ Connected to bus\n")

print("STEP 1: Reading Current Operating Modes")
print("-" * 70)
print("Mode 0 = Position Control (CORRECT)")
print("Mode 1 = Velocity Control (WRONG - explains the issue!)")
print("Mode 3 = PWM Control")
print("-" * 70)

modes = {}
for motor_id in MOTOR_IDS:
    try:
        # Read Operating_Mode using sms_sts module
        mode, result, error = scs.sms_sts.read1ByteTxRx(port_handler, motor_id, ADDR_OPERATING_MODE)
        
        if result == scs.COMM_SUCCESS:
            modes[motor_id] = mode
            
            mode_name = {
                0: "Position Control",
                1: "Velocity Control",
                3: "PWM Control"
            }.get(mode, f"Unknown")
            
            if mode == 0:
                print(f"Motor {motor_id}: Mode {mode} ({mode_name}) ✅ CORRECT")
            else:
                print(f"Motor {motor_id}: Mode {mode} ({mode_name}) ⚠️ WRONG!")
        else:
            print(f"Motor {motor_id}: ❌ Communication error (result={result})")
            modes[motor_id] = None
            
    except Exception as e:
        print(f"Motor {motor_id}: ❌ Error - {e}")
        modes[motor_id] = None

# Check if any motors need fixing
needs_fix = [mid for mid, mode in modes.items() if mode is not None and mode != 0]

if needs_fix:
    print()
    print("=" * 70)
    print(f"⚠️  FOUND {len(needs_fix)} MOTOR(S) IN WRONG MODE!")
    print("=" * 70)
    print(f"Motors needing fix: {needs_fix}")
    print()
    print("🔍 ROOT CAUSE FOUND!")
    print("In velocity control mode, servos ignore Goal_Position commands.")
    print("This explains why your motors weren't moving!")
    print()
    
    response = input("Fix these motors now? (yes/no): ").strip().lower()
    
    if response == 'yes':
        print()
        print("STEP 2: Fixing Operating Modes")
        print("-" * 70)
        
        import time
        
        for motor_id in needs_fix:
            try:
                print(f"\nMotor {motor_id}:")
                
                # Step 1: Disable torque (required to change operating mode)
                print(f"  Disabling torque...")
                result, error = scs.sms_sts.write1ByteTxRx(port_handler, motor_id, ADDR_TORQUE_ENABLE, 0)
                if result != scs.COMM_SUCCESS:
                    print(f"  ❌ Failed to disable torque (result={result})")
                    continue
                time.sleep(0.05)
                
                # Step 2: Set Operating_Mode to 0 (Position Control)
                print(f"  Setting mode to 0 (Position Control)...")
                result, error = scs.sms_sts.write1ByteTxRx(port_handler, motor_id, ADDR_OPERATING_MODE, 0)
                if result != scs.COMM_SUCCESS:
                    print(f"  ❌ Failed to set operating mode (result={result})")
                    continue
                time.sleep(0.05)
                
                # Step 3: Re-enable torque
                print(f"  Re-enabling torque...")
                result, error = scs.sms_sts.write1ByteTxRx(port_handler, motor_id, ADDR_TORQUE_ENABLE, 1)
                if result != scs.COMM_SUCCESS:
                    print(f"  ❌ Failed to enable torque (result={result})")
                    continue
                time.sleep(0.05)
                
                # Verify the change
                new_mode, result, error = scs.sms_sts.read1ByteTxRx(port_handler, motor_id, ADDR_OPERATING_MODE)
                if result == scs.COMM_SUCCESS and new_mode == 0:
                    print(f"  ✅ Successfully fixed! Now in Position Control mode")
                else:
                    print(f"  ⚠️  Still in mode {new_mode} - might need power cycle")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print()
        print("=" * 70)
        print("VERIFICATION: Re-reading all modes")
        print("-" * 70)
        
        all_fixed = True
        for motor_id in MOTOR_IDS:
            mode, result, error = scs.sms_sts.read1ByteTxRx(port_handler, motor_id, ADDR_OPERATING_MODE)
            
            if result == scs.COMM_SUCCESS:
                mode_name = {0: "Position", 1: "Velocity", 3: "PWM"}.get(mode, "Unknown")
                
                if mode == 0:
                    print(f"Motor {motor_id}: Mode {mode} ({mode_name}) ✅")
                else:
                    print(f"Motor {motor_id}: Mode {mode} ({mode_name}) ❌")
                    all_fixed = False
            else:
                print(f"Motor {motor_id}: ❌ Communication error")
                all_fixed = False
        
        print()
        if all_fixed:
            print("🎉 SUCCESS! All motors are now in Position Control mode!")
            print()
            print("Next steps:")
            print("  1. Try your teleoperation: python3 teleop_so101.py")
            print("  2. Motors should now respond properly to position commands!")
            print()
            print("✅ The issue was: Servos were in velocity mode, ignoring positions.")
            print("✅ Now fixed: Servos are in position mode, will follow Goal_Position.")
        else:
            print("⚠️  Some motors still in wrong mode.")
            print("Try power cycling the arm and running this script again.")
    else:
        print("\nSkipping fix. Motors remain in current mode.")
        
else:
    print()
    print("=" * 70)
    print("✅ ALL MOTORS ALREADY IN CORRECT MODE!")
    print("=" * 70)
    print("All servos are in Position Control mode (0).")
    print()
    print("If you're still having movement issues, the problem is likely:")
    print("  ✅ NOT the operating mode (it's correct)")
    print("  ✅ You've already fixed Goal_Velocity and Acceleration")
    print()
    print("Your setup should be working! Try: python3 teleop_so101.py")

# Close port
port_handler.closePort()
print()
print("✅ Done!")

