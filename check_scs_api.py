#!/usr/bin/env python3
"""Check what's available in scservo_sdk."""

import scservo_sdk as scs

print("Available in scservo_sdk:")
print()
for item in sorted(dir(scs)):
    if not item.startswith('_'):
        print(f"  - {item}")

