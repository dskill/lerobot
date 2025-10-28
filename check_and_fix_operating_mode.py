#!/usr/bin/env python3
"""
Check and fix Feetech servo operating modes.
Based on Vassar Robotics feedback - servos might be in wrong mode!

Operating Mode register (address 33):
  0 = Position Control Mode (CORRECT for LeRobot)
  1 = Speed/Velocity Control Mode (WRONG - explains the issue!)
  3 = PWM Control Mode (step servo)
"""

from lerobot.motors.feetech import FeetechMotorsBus

PORT = "/dev/tty.usbmodem5A7A0562271"
BAUDRATE = 1000000
MOTOR_IDS = [1, 2, 3, 4, 5, 6]

print("=" * 70)
print("CHECKING AND FIXING FEETECH SERVO OPERATING MODES")
print("=" * 70)
print(f"Port: {PORT}")
print(f"Motor IDs: {MOTOR_IDS}")
print()

# Create bus without motor configuration (for direct register access)
bus = FeetechMotorsBus(port=PORT, motors={})
bus._connect(handshake=False)
print("✅ Connected to bus\n")

print("STEP 1: Reading Current Operating Modes")
print("-" * 70)

modes = {}
for motor_id in MOTOR_IDS:
    try:
        # Read Operating_Mode register (address 33)
        mode = bus.read("Operating_Mode", motor_id)
        modes[motor_id] = mode
        
        mode_name = {
            0: "Position Control",
            1: "Speed/Velocity Control",
            3: "PWM Control (step)"
        }.get(mode, f"Unknown")
        
        if mode == 0:
            print(f"Motor {motor_id}: Mode {mode} ({mode_name}) ✅ CORRECT")
        else:
            print(f"Motor {motor_id}: Mode {mode} ({mode_name}) ⚠️ WRONG - NEEDS FIX!")
            
    except Exception as e:
        print(f"Motor {motor_id}: ❌ Error reading - {e}")
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
    print("This explains why Goal_Position wasn't working!")
    print("In velocity control mode, the servo ignores position commands.")
    print()
    
    response = input("Fix these motors? (yes/no): ").strip().lower()
    
    if response == 'yes':
        print()
        print("STEP 2: Fixing Operating Modes")
        print("-" * 70)
        
        for motor_id in needs_fix:
            try:
                # Disable torque first (required to change operating mode)
                print(f"Motor {motor_id}: Disabling torque...")
                bus.write("Torque_Enable", motor_id, 0)
                
                # Set Operating_Mode to 0 (Position Control)
                print(f"Motor {motor_id}: Setting mode to 0 (Position Control)...")
                bus.write("Operating_Mode", motor_id, 0)
                
                # Re-enable torque
                print(f"Motor {motor_id}: Re-enabling torque...")
                bus.write("Torque_Enable", motor_id, 1)
                
                # Verify the change
                new_mode = bus.read("Operating_Mode", motor_id)
                if new_mode == 0:
                    print(f"Motor {motor_id}: ✅ Successfully fixed! Now in mode {new_mode}\n")
                else:
                    print(f"Motor {motor_id}: ⚠️  Still in mode {new_mode} - might need power cycle\n")
                    
            except Exception as e:
                print(f"Motor {motor_id}: ❌ Error fixing - {e}\n")
        
        print("=" * 70)
        print("VERIFICATION: Re-reading all modes")
        print("-" * 70)
        
        all_fixed = True
        for motor_id in MOTOR_IDS:
            try:
                mode = bus.read("Operating_Mode", motor_id)
                mode_name = {0: "Position", 1: "Velocity", 3: "PWM"}.get(mode, "Unknown")
                
                if mode == 0:
                    print(f"Motor {motor_id}: Mode {mode} ({mode_name}) ✅")
                else:
                    print(f"Motor {motor_id}: Mode {mode} ({mode_name}) ❌")
                    all_fixed = False
            except Exception as e:
                print(f"Motor {motor_id}: ❌ Error - {e}")
                all_fixed = False
        
        print()
        if all_fixed:
            print("🎉 SUCCESS! All motors are now in Position Control mode!")
            print()
            print("Next steps:")
            print("  1. Try your teleoperation script: python3 teleop_so101.py")
            print("  2. The motors should now respond to Goal_Position commands")
        else:
            print("⚠️  Some motors still in wrong mode. Try:")
            print("  1. Power cycle the arm (turn off/on)")
            print("  2. Run this script again")
    else:
        print("\nSkipping fix. Motors remain in current mode.")
        
else:
    print()
    print("=" * 70)
    print("✅ ALL MOTORS ALREADY IN CORRECT MODE!")
    print("=" * 70)
    print("All servos are in Position Control mode (0).")
    print("Your Goal_Position commands should work fine.")

print()
print("ADDITIONAL INFO: Other Key Registers")
print("-" * 70)
for motor_id in MOTOR_IDS[:2]:  # Check first 2 motors as examples
    try:
        torque = bus.read("Torque_Enable", motor_id)
        lock = bus.read("Lock", motor_id)
        pos = bus.read("Present_Position", motor_id)
        print(f"Motor {motor_id}: Torque={torque}, Lock={lock}, Position={pos}")
    except Exception as e:
        print(f"Motor {motor_id}: Error - {e}")

bus.disconnect()
print()
print("✅ Done!")

