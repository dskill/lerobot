#!/usr/bin/env python3
"""Simple test to understand the Vassar SDK API."""

from vassar_feetech_servo_sdk.controller import ServoController
import inspect

print("ServoController signature:")
print(inspect.signature(ServoController.__init__))
print()

print("ServoController docstring:")
print(ServoController.__doc__)
print()

# Try different initialization approaches
print("=" * 60)
print("Test 1: Positional arguments")
print("=" * 60)
try:
    controller = ServoController('/dev/tty.usbmodem5A7A0562271', 1000000)
    print("✅ Success with positional args")
    
    # Try to connect
    print("Connecting...")
    controller.connect()
    print("✅ Connected")
    
    # Try reading position from motor 1
    print("Reading position from motor 1...")
    pos = controller.read_position(1)
    print(f"Position: {pos}")
    
    controller.disconnect()
    print("✅ Test passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Test 2: No parameters, then connect")
print("=" * 60)
try:
    controller = ServoController()
    print("✅ Controller created")
    controller.connect()
    print("✅ Connected")
    controller.disconnect()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nAvailable methods:")
for method in dir(ServoController):
    if not method.startswith('_') and callable(getattr(ServoController, method)):
        print(f"  - {method}")

