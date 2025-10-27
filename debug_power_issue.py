#!/usr/bin/env python3
"""
Systematic debugging for SO-101 power issues
"""
import time
from lerobot.scripts.lerobot_find_port import find_available_ports
from lerobot.motors.feetech import FeetechMotorsBus

print("=" * 70)
print("SO-101 POWER DEBUGGING GUIDE")
print("=" * 70)

# Step 1: Check available ports
print("\n1. CHECKING USB CONNECTIONS")
print("-" * 40)
ports = [p for p in find_available_ports() if 'usb' in p.lower()]
if ports:
    print(f"Found {len(ports)} USB port(s):")
    for p in ports:
        print(f"  - {p}")
else:
    print("✗ No USB ports found!")
    print("  Check USB cable connections")
    exit(1)

# Step 2: Test each port
print("\n2. TESTING EACH PORT")
print("-" * 40)

working_ports = []
for port in ports:
    print(f"\nTesting {port}:")
    try:
        bus = FeetechMotorsBus(port=port, motors={})
        bus._connect(handshake=False)
        print(f"  ✓ Port accessible")
        
        # Quick scan for motors
        found = False
        for id_ in [1, 2, 3, 4, 5, 6]:
            if bus.ping(id_, num_retry=0):
                found = True
                print(f"  ✓ Motor ID {id_} responds!")
                break
        
        if found:
            working_ports.append(port)
        else:
            print(f"  ✗ No motors responding")
        
        bus.port_handler.closePort()
    except Exception as e:
        print(f"  ✗ Error: {e}")

# Step 3: Diagnosis
print("\n" + "=" * 70)
print("DIAGNOSIS")
print("=" * 70)

if working_ports:
    print("✓ Working port(s) found:")
    for p in working_ports:
        print(f"  - {p}")
    print("\nNext steps:")
    print("1. Use the working port in your scripts")
    print("2. The other arm needs power")
else:
    print("✗ NO WORKING MOTORS FOUND")
    print("\n" + "=" * 70)
    print("TROUBLESHOOTING CHECKLIST")
    print("=" * 70)
    
    print("\n□ POWER SUPPLY:")
    print("  1. Is the 12V power supply plugged into the wall?")
    print("  2. Is the power supply turned ON (check LED)?")
    print("  3. Is the power cable connected to the Waveshare board?")
    print("  4. Are the screw terminals tight on the board?")
    
    print("\n□ WAVESHARE BOARD:")
    print("  1. Check the USB-SERVO jumper (should be on 'B')")
    print("  2. Look for any LEDs on the board - are they lit?")
    print("  3. Check for burned components or smell")
    
    print("\n□ MOTOR CONNECTIONS:")
    print("  1. Are the 3-pin cables connected to the motors?")
    print("  2. Are the cables daisy-chained between all 6 motors?")
    print("  3. Try connecting just ONE motor directly to the board")
    
    print("\n□ MEASUREMENTS (if you have a multimeter):")
    print("  1. Measure voltage at power input (should be 12V)")
    print("  2. Measure voltage at motor connector:")
    print("     - Red to Brown wire = should be 12V")
    print("     - If 0V, board isn't routing power")
    
    print("\n□ QUICK TESTS:")
    print("  1. Swap power supplies between leader and follower")
    print("  2. Try a different USB cable")
    print("  3. Connect leader arm to follower's Waveshare board")
    
    print("\n" + "=" * 70)
    print("MOST LIKELY CAUSE")
    print("=" * 70)
    print("\nBased on the symptoms (communication works but no motor power):")
    print("→ The 12V power is not reaching the motors")
    print("→ Check power supply and Waveshare board connections")
    print("→ The board might have a blown fuse or damaged power circuit")



