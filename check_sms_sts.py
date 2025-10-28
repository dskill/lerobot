#!/usr/bin/env python3
"""Check what's in the sms_sts module."""

import scservo_sdk as scs

print("=" * 70)
print("SMS_STS Module (for STS3215 servos):")
print("=" * 70)
for item in sorted(dir(scs.sms_sts)):
    if not item.startswith('_'):
        print(f"  - {item}")

print()
print("=" * 70)
print("protocol_packet_handler Module:")
print("=" * 70)
for item in sorted(dir(scs.protocol_packet_handler)):
    if not item.startswith('_'):
        print(f"  - {item}")

print()
print("=" * 70)
print("Checking for PacketHandler:")
print("=" * 70)
if hasattr(scs, 'PacketHandler'):
    print("✅ scs.PacketHandler exists")
elif hasattr(scs.protocol_packet_handler, 'PacketHandler'):
    print("✅ scs.protocol_packet_handler.PacketHandler exists")
    print(f"   Signature: {scs.protocol_packet_handler.PacketHandler}")
elif hasattr(scs.sms_sts, 'PacketHandler'):
    print("✅ scs.sms_sts.PacketHandler exists")
else:
    print("❌ PacketHandler not found")
    print("\nTrying to import from submodules...")
    try:
        from scservo_sdk.protocol_packet_handler import PacketHandler
        print("✅ Can import: from scservo_sdk.protocol_packet_handler import PacketHandler")
    except:
        print("❌ Cannot import from protocol_packet_handler")
    
    try:
        from scservo_sdk.sms_sts import PacketHandler
        print("✅ Can import: from scservo_sdk.sms_sts import PacketHandler")
    except:
        print("❌ Cannot import from sms_sts")

