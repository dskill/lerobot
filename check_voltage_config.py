#!/usr/bin/env python3
"""
Check what voltage the servos are configured for
"""
from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors import Motor, MotorNormMode

print("=" * 70)
print("SERVO VOLTAGE CONFIGURATION CHECK")
print("=" * 70)

# Test with lower voltage first (safer)
test_voltages = [8.4, 7.4, 12.0]

for voltage in test_voltages:
    print(f"\n" + "=" * 70)
    print(f"Testing with {voltage}V assumption")
    print("=" * 70)
    print(f"If servos are configured for {voltage}V:")
    
    if voltage == 7.4:
        print("  - Min voltage limit likely: ~6.5V (65 raw)")
        print("  - Max voltage limit likely: ~8.5V (85 raw)")
        print("  - Typical for 2S LiPo battery systems")
        
    elif voltage == 8.4:
        print("  - Min voltage limit likely: ~7.0V (70 raw)")
        print("  - Max voltage limit likely: ~9.5V (95 raw)")
        print("  - Typical for 2S LiFePO4 battery systems")
        
    elif voltage == 12.0:
        print("  - Min voltage limit likely: ~10.0V (100 raw)")
        print("  - Max voltage limit likely: ~13.0V (130 raw)")
        print("  - Standard for 3S LiPo or 12V power supplies")

print("\n" + "=" * 70)
print("TO DETERMINE YOUR LEADER ARM VOLTAGE:")
print("=" * 70)

print("\n1. CHECK THE ORIGINAL POWER SUPPLY:")
print("   - What voltage is written on the leader arm's power adapter?")
print("   - Common values: 7.4V, 8.4V, or 12V")

print("\n2. CHECK THE SERVO SPECS:")
print("   - STS3215 can work from 6V to 12.6V")
print("   - But each robot is configured for specific voltage")

print("\n3. IF YOU HAVE THE CORRECT VOLTAGE SUPPLY:")
print("   - Connect leader arm to its proper voltage")
print("   - Run this test:")
print("")
print("from lerobot.motors.feetech import FeetechMotorsBus")
print("from lerobot.motors import Motor, MotorNormMode")
print("")
print('PORT = "/dev/tty.usbmodem5A7A0574331"')
print('bus = FeetechMotorsBus(port=PORT, motors={"test": Motor(1, "sts3215", MotorNormMode.RANGE_0_100)})')
print('bus._connect(handshake=False)')
print('')
print('# Read voltage limits from motor 1')
print('min_volt = bus.packet_handler.read1ByteTxRx(bus.port_handler, 1, 15)[0]')
print('max_volt = bus.packet_handler.read1ByteTxRx(bus.port_handler, 1, 14)[0]')
print('print(f"Min voltage: {min_volt/10:.1f}V")')
print('print(f"Max voltage: {max_volt/10:.1f}V")')

print("\n" + "=" * 70)
print("IMPORTANT SAFETY NOTES:")
print("=" * 70)
print("\n⚠️  DO NOT apply 12V to servos configured for 7.4V!")
print("   - Will trigger protection (red LED)")
print("   - Could damage servos if protection fails")
print("\n⚠️  DO NOT apply 7.4V to servos configured for 12V!")
print("   - Won't damage but won't work (undervoltage)")
print("\n✓ SAFE approach:")
print("   1. Find the original power supply specs")
print("   2. Use the correct voltage for each arm")
print("   3. Leader and follower can use different voltages")

print("\n" + "=" * 70)
print("YOUR SITUATION:")
print("=" * 70)
print("\nLeader arm: Probably configured for 7.4V or 8.4V")
print("  → Red LED with 12V = overvoltage protection")
print("  → Need lower voltage power supply")
print("\nFollower arm: Configured for 12V")
print("  → Didn't work with lower voltage")
print("  → Works with 12V (once properly powered)")
print("\nSolution: Use TWO power supplies:")
print("  - Leader: 7.4V or 8.4V supply")
print("  - Follower: 12V supply")

