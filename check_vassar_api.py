#!/usr/bin/env python3
"""Check what's available in the Vassar Feetech SDK."""

import vassar_feetech_servo_sdk.controller as controller

print("Available in vassar_feetech_servo_sdk.controller:")
print()
for item in dir(controller):
    if not item.startswith('_'):
        print(f"  - {item}")
        obj = getattr(controller, item)
        if hasattr(obj, '__doc__') and obj.__doc__:
            doc = obj.__doc__.split('\n')[0]
            print(f"    {doc}")
        print()

