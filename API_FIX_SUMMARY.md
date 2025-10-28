# Feetech Servo SDK API Fixes

## Summary
Fixed compatibility issues with `feetech-servo-sdk` v1.0.0 after rebase. The SDK API changed, removing packet_handler parameter from sync operations and byte manipulation utility functions.

## Source of scservo-sdk
The `scservo-sdk` module comes from the **`feetech-servo-sdk` package** installed via pip:
- **Package**: `feetech-servo-sdk==1.0.0`
- **PyPI**: https://pypi.org/project/feetech-servo-sdk/
- **GitHub**: https://github.com/Adam-Software/FEETECH-Servo-Python-SDK
- **Location**: `/venv/lib/python3.10/site-packages/scservo_sdk/`

It is **NOT** from the Gitee repository (that's a different/older version).

## Changes Made

### 1. Fixed GroupSyncRead/GroupSyncWrite API (feetech.py)

**File**: `src/lerobot/motors/feetech/feetech.py` (lines 134-135)

**Old API** (4 parameters):
```python
self.sync_reader = scs.GroupSyncRead(self.port_handler, self.packet_handler, 0, 0)
self.sync_writer = scs.GroupSyncWrite(self.port_handler, self.packet_handler, 0, 0)
```

**New API** (3 parameters):
```python
self.sync_reader = scs.GroupSyncRead(self.port_handler, 0, 0)
self.sync_writer = scs.GroupSyncWrite(self.port_handler, 0, 0)
```

**Reason**: The `packet_handler` parameter was removed from the constructor in the new SDK version.

### 2. Fixed Byte Manipulation Functions (feetech.py)

**File**: `src/lerobot/motors/feetech/feetech.py` (lines 69-94)

**Old Code** (using SDK functions):
```python
def _split_into_byte_chunks(value: int, length: int) -> list[int]:
    import scservo_sdk as scs

    if length == 1:
        data = [value]
    elif length == 2:
        data = [scs.SCS_LOBYTE(value), scs.SCS_HIBYTE(value)]
    elif length == 4:
        data = [
            scs.SCS_LOBYTE(scs.SCS_LOWORD(value)),
            scs.SCS_HIBYTE(scs.SCS_LOWORD(value)),
            scs.SCS_LOBYTE(scs.SCS_HIWORD(value)),
            scs.SCS_HIBYTE(scs.SCS_HIWORD(value)),
        ]
    return data
```

**New Code** (local helper functions):
```python
def _split_into_byte_chunks(value: int, length: int) -> list[int]:
    # Helper functions for byte manipulation (replicate scservo_sdk internal methods)
    def lobyte(w: int) -> int:
        return w & 0xFF

    def hibyte(w: int) -> int:
        return (w >> 8) & 0xFF

    def loword(l: int) -> int:
        return l & 0xFFFF

    def hiword(h: int) -> int:
        return (h >> 16) & 0xFFFF

    if length == 1:
        data = [value]
    elif length == 2:
        data = [lobyte(value), hibyte(value)]
    elif length == 4:
        data = [
            lobyte(loword(value)),
            hibyte(loword(value)),
            lobyte(hiword(value)),
            hibyte(hiword(value)),
        ]
    return data
```

**Reason**: `SCS_LOBYTE`, `SCS_HIBYTE`, `SCS_LOWORD`, `SCS_HIWORD` are no longer exported by the SDK. They still exist as internal methods in `protocol_packet_handler.py` but aren't publicly accessible. We replicate the logic locally.

### 3. Fixed test_gripper.py to Set Goal_Velocity and Acceleration

**File**: `test_gripper.py` (lines 54-78)

**Problem**: The gripper wasn't moving because only `Goal_Position` was being set.

**Old Code**:
```python
bus.write("Goal_Position", "gripper", target_open, normalize=False)
```

**New Code**:
```python
bus.write("Goal_Position", "gripper", target_open, normalize=False)
# IMPORTANT: Feetech motors need Goal_Velocity AND Acceleration for movement!
bus.write("Goal_Velocity", "gripper", 600, normalize=False)
bus.write("Acceleration", "gripper", 20, normalize=False)
```

**Reason**: Feetech STS3215 motors in POSITION mode require all three parameters:
- `Goal_Position` - WHERE to move
- `Goal_Velocity` - HOW FAST to move (600 = smooth, fast movement)
- `Acceleration` - HOW SMOOTHLY to accelerate (20 = gentle acceleration at 30 Hz)

Without `Goal_Velocity`, motors won't execute movement even though they're torque-enabled.

## Testing

After these fixes:
1. ✅ `test_gripper.py` should successfully connect to the motor
2. ✅ The gripper should physically move when commanded
3. ✅ No API errors about missing attributes or wrong parameter counts

## Related Documentation

See the repo-specific rules for full details on:
- Why Goal_Velocity and Acceleration are required
- Tuning parameters for different control rates
- The full SO-101 setup and calibration process

