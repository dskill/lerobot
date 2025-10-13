#!/usr/bin/env python3
"""
Check servo error status when LED is flashing red
"""
from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors import Motor, MotorNormMode

# Try both ports
PORTS = [
    "/dev/tty.usbmodem5A7A0574331",  # Leader
    "/dev/tty.usbmodem5A7A0562271",  # Follower
]

print("=" * 70)
print("SERVO ERROR DIAGNOSTIC - RED LED")
print("=" * 70)

for port in PORTS:
    print(f"\nChecking port: {port}")
    print("-" * 40)
    
    try:
        bus = FeetechMotorsBus(
            port=port,
            motors={"test": Motor(1, "sts3215", MotorNormMode.RANGE_0_100)},
        )
        bus._connect(handshake=False)
        
        # Check all motors
        for motor_id in range(1, 7):
            model = bus.ping(motor_id, num_retry=0)
            if model:
                print(f"\nMotor ID {motor_id} found - Reading error status:")
                
                # Read error-related parameters
                try:
                    # Voltage
                    voltage = bus.packet_handler.read1ByteTxRx(bus.port_handler, motor_id, 62)[0]
                    actual_voltage = voltage / 10.0
                    print(f"  Voltage: {actual_voltage:.1f}V", end="")
                    if actual_voltage > 12.6:
                        print(" ⚠️  OVERVOLTAGE!")
                    elif actual_voltage < 10.0:
                        print(" ⚠️  UNDERVOLTAGE!")
                    else:
                        print(" ✓")
                    
                    # Temperature
                    temp = bus.packet_handler.read1ByteTxRx(bus.port_handler, motor_id, 63)[0]
                    print(f"  Temperature: {temp}°C", end="")
                    if temp > 70:
                        print(" ⚠️  OVERHEATING!")
                    else:
                        print(" ✓")
                    
                    # Status register (errors)
                    status = bus.packet_handler.read1ByteTxRx(bus.port_handler, motor_id, 65)[0]
                    print(f"  Status Register: {status:08b} (binary)")
                    if status != 0:
                        print("  Error bits:")
                        if status & 0x01: print("    - Bit 0: Voltage Error")
                        if status & 0x02: print("    - Bit 1: Position Error")
                        if status & 0x04: print("    - Bit 2: Temperature Error")
                        if status & 0x08: print("    - Bit 3: Reserved")
                        if status & 0x10: print("    - Bit 4: Reserved")
                        if status & 0x20: print("    - Bit 5: Overload Error")
                        if status & 0x40: print("    - Bit 6: Driver Error")
                        if status & 0x80: print("    - Bit 7: EEP Error")
                    else:
                        print("    No errors in status register")
                    
                    # Load/Current
                    load = bus.packet_handler.read2ByteTxRx(bus.port_handler, motor_id, 60)[0]
                    current = bus.packet_handler.read2ByteTxRx(bus.port_handler, motor_id, 69)[0]
                    print(f"  Load: {load}")
                    print(f"  Current: {current}")
                    
                    # Moving status
                    moving = bus.packet_handler.read1ByteTxRx(bus.port_handler, motor_id, 66)[0]
                    print(f"  Moving: {moving}")
                    
                    # LED Alarm Condition
                    led_alarm = bus.packet_handler.read1ByteTxRx(bus.port_handler, motor_id, 20)[0]
                    print(f"  LED Alarm Setting: {led_alarm:08b}")
                    
                except Exception as e:
                    print(f"  Error reading parameters: {e}")
        
        bus.port_handler.closePort()
        
    except Exception as e:
        print(f"  Cannot access port: {e}")

print("\n" + "=" * 70)
print("DIAGNOSIS")
print("=" * 70)
print("\nRed LED typically means:")
print("1. VOLTAGE ISSUE (most common)")
print("   - Check if voltage is between 11-12.6V")
print("   - Too high = damage risk")
print("   - Too low = won't work")
print("\n2. OVERLOAD")
print("   - Motor blocked or struggling")
print("   - Reduce load or check for obstruction")
print("\n3. OVERHEATING")
print("   - Let motor cool down")
print("   - Check if motor is working too hard")
print("\nTO FIX:")
print("1. Check your power supply voltage with multimeter")
print("2. Make sure it's exactly 12V")
print("3. Power cycle the system")
print("4. If LED stays red, motor might be damaged")

