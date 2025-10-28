#!/usr/bin/env python3
"""
Direct test of sms_sts read functions.
"""

import scservo_sdk as scs

PORT = "/dev/tty.usbmodem5A7A0562271"
BAUDRATE = 1000000
TEST_MOTOR_ID = 1
ADDR_OPERATING_MODE = 33

print("Testing sms_sts.read1ByteTxRx...")
print(f"Port: {PORT}")
print(f"Motor ID: {TEST_MOTOR_ID}")
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

print("✅ Port opened\n")

# Try different ways to call the function
print("Attempt 1: Call sms_sts.read1ByteTxRx directly")
try:
    result = scs.sms_sts.read1ByteTxRx(port_handler, TEST_MOTOR_ID, ADDR_OPERATING_MODE)
    print(f"  Result type: {type(result)}")
    print(f"  Result: {result}")
    if isinstance(result, tuple):
        print(f"  Unpacked: value={result[0]}, result={result[1]}, error={result[2] if len(result) > 2 else 'N/A'}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("Attempt 2: Use ping to test communication")
try:
    model, result, error = scs.sms_sts.ping(port_handler, TEST_MOTOR_ID)
    print(f"  Ping result: model={model}, result={result}, error={error}")
    print(f"  COMM_SUCCESS = {scs.COMM_SUCCESS}")
    if result == scs.COMM_SUCCESS:
        print(f"  ✅ Motor {TEST_MOTOR_ID} responded!")
    else:
        print(f"  ❌ Motor {TEST_MOTOR_ID} did not respond")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("Attempt 3: Read present position")
try:
    # Present position is at address 56, 2 bytes
    pos_low, result, error = scs.sms_sts.read1ByteTxRx(port_handler, TEST_MOTOR_ID, 56)
    print(f"  Position low byte: {pos_low}, result={result}, error={error}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

port_handler.closePort()
print("\n✅ Done!")

