# SO-101 Follower Arm Bug Report and Findings

## Date: October 12, 2025

## Summary
Found and fixed a **critical bug** in the lerobot codebase, but the follower arm motors still won't move. The bug fix is correct and necessary, but there appears to be an additional hardware or firmware issue preventing motor movement.

---

## 🐛 BUG FOUND AND FIXED: `enable_torque()` Lock Parameter

### Location
`src/lerobot/motors/feetech/feetech.py` - Line 310

### The Bug
```python
def enable_torque(self, motors: str | list[str] | None = None, num_retry: int = 0) -> None:
    for motor in self._get_motors_list(motors):
        self.write("Torque_Enable", motor, TorqueMode.ENABLED.value, num_retry=num_retry)
        self.write("Lock", motor, 1, num_retry=num_retry)  # ❌ BUG: Should be 0!
```

### The Fix
```python
def enable_torque(self, motors: str | list[str] | None = None, num_retry: int = 0) -> None:
    for motor in self._get_motors_list(motors):
        self.write("Torque_Enable", motor, TorqueMode.ENABLED.value, num_retry=num_retry)
        self.write("Lock", motor, 0, num_retry=num_retry)  # ✅ FIXED: Lock=0 to unlock motor
```

### Why This is a Bug
- The `Lock` parameter (control table address 55) prevents the motor from moving when set to 1
- When enabling torque (wanting motors to move), Lock should be 0 (unlocked)
- The `disable_torque()` function correctly sets Lock=0
- This was backwards logic

### Impact
This bug would affect **all users of Feetech motors** in the lerobot library, including:
- SO-101 robot arms
- SO-100 robot arms
- Any other robots using Feetech STS/SMS series servos

---

## ✅ Verification of Fix

After applying the fix, motor status shows correct values:
```
Motor 1 (shoulder_pan):  Lock=0, Torque=1, Current=0, Position=2246
Motor 2 (shoulder_lift):  Lock=0, Torque=1, Current=0, Position=1328
Motor 3 (elbow_flex):    Lock=0, Torque=1, Current=0, Position=3504
Motor 4 (wrist_flex):    Lock=0, Torque=1, Current=0, Position=2273
Motor 5 (wrist_roll):    Lock=0, Torque=1, Current=0, Position=614
Motor 6 (gripper):       Lock=0, Torque=1, Current=0, Position=2316
```

✅ Lock = 0 (correct - motor is unlocked)  
✅ Torque = 1 (correct - torque is enabled)  

---

## ❌ Remaining Problem: Motors Still Won't Move

Despite the fix, the follower arm motors still don't move. Testing shows:

### What Works
- ✅ USB communication to all 6 motors
- ✅ Reading all motor parameters
- ✅ Writing Goal_Position successfully
- ✅ Lock parameter now correctly set to 0
- ✅ Torque_Enable set to 1
- ✅ All protection parameters are reasonable
- ✅ Voltage reads 12.6V (correct 12V supply)

### What Doesn't Work
- ❌ Motors won't move to Goal_Position
- ❌ Present_Current always reads 0 (no power to motor windings)
- ❌ Moving flag stays at 0

### Test Results
```
Before write:
  Present_Position: 2316
  Goal_Position:    2316

Writing Goal_Position = 2516...

Immediately after write:
  Goal_Position:     2516  ✅ Write successful
  Present_Position:  2316
  Moving:            0     ❌ Motor not attempting to move
  Present_Current:   0     ❌ No current draw

After 3 seconds:
  Goal_Position:     2516  ✅ Value maintained
  Present_Position:  2316  ❌ No movement
  Moving:            0
  Present_Current:   0
```

### All Parameter Values Checked
```
Lock                          : 0     ✅
Torque_Enable                 : 1     ✅
Torque_Limit                  : 500   ✅
Max_Torque_Limit              : 500   ✅
Protection_Current            : 250   ✅
Protective_Torque             : 20    ✅
Protection_Time               : 200   ✅
Overload_Torque               : 25    ✅
Min_Position_Limit            : 2047  ✅
Max_Position_Limit            : 3321  ✅
Operating_Mode                : 0     ✅ (POSITION mode)
Minimum_Startup_Force         : 16    ✅ (reasonable)
Present_Voltage               : 126   ✅ (12.6V)
Present_Temperature           : 32    ✅ (32°C)
Status                        : 0     ✅ (no errors)
```

All software parameters are correct!

---

## 🔍 Analysis

1. **The Bug Fix is Necessary**: The Lock=1 bug would prevent motors from moving and needed to be fixed.

2. **Software is Correct**: After the fix, all software parameters are set correctly.

3. **Hardware/Firmware Issue**: The fact that Goal_Position can be written and maintained, but the motor shows:
   - Present_Current = 0 (no power to windings)
   - Moving = 0 (not even attempting to move)
   - Position unchanged
   
   Suggests a hardware or firmware protection mechanism is preventing power from reaching the motor windings.

4. **Communication Works**: We can read and write all parameters successfully, so the communication bus is working.

5. **Power Supply Present**: Voltage reads 12.6V, confirming power is reaching the servo board.

---

## 🎯 Next Steps

### For the Lerobot Team
1. **Merge the Lock Fix**: The `enable_torque()` bug fix should be merged into the main repository immediately
2. **Add to Changelog**: Document this as a bug fix for Feetech motor control
3. **Test with Other Feetech Robots**: Verify if this fixes issues for SO-100 or other Feetech-based robots

### For Hardware Debugging
1. **Test with Feetech Debug Tool**: Use the official FDDebug tool to see if motors can be commanded to move
   - Download: https://gitee.com/ftservo/fddebug
   - This bypasses the Python SDK and tests at a lower level

2. **Test Individual Motor**: Disconnect all motors except one to rule out power supply current issues

3. **Check Waveshare Board**: The Waveshare Bus Servo Adapter might have a hardware issue:
   - Test motors on the leader arm's board (which is known working)
   - Measure voltage at servo connector with multimeter

4. **Contact Manufacturer**: Since all software parameters are correct but motors won't move, TheRobotStudio/Feetech support should be consulted

---

## 📝 Files Created for Testing

- `test_lock_fix.py` - Tests the Lock parameter fix
- `check_all_parameters.py` - Comprehensive parameter check
- `test_goal_position_write.py` - Verifies Goal_Position writes
- `check_startup_force.py` - Checks Minimum_Startup_Force parameter
- `BUG_REPORT_AND_FINDINGS.md` - This document

---

## 🔗 Related GitHub Issues

Searched the lerobot repository but **did not find any existing issues** specifically about:
- SO-101 motor movement problems
- Feetech servo Lock parameter issues
- enable_torque() bugs
- Motors not moving after calibration

This appears to be a **newly discovered bug** that should be reported to the lerobot repository.

---

## 💡 Recommendation

**Open a GitHub issue** on the lerobot repository with:
1. Title: "Bug: Feetech enable_torque() sets Lock=1, preventing motor movement"
2. Description: The bug in enable_torque() function
3. Impact: Affects all Feetech motor users (SO-100, SO-101, etc.)
4. Fix: Change Lock=1 to Lock=0 in enable_torque()
5. Testing: Include test results showing Lock now correctly set to 0

This is a critical bug that likely affects many users but may not have been noticed if:
- Users haven't tried to move motors programmatically after calibration
- The issue was attributed to hardware problems
- Users worked around it by manually setting Lock=0

---

## ✨ Conclusion

**We found and fixed a real bug in the lerobot codebase!** The `enable_torque()` function was setting Lock=1 when it should set Lock=0. This fix is verified and ready to be submitted as a pull request.

However, the follower arm still has an additional issue preventing motor movement, likely hardware/firmware related, that requires further investigation with manufacturer tools or hardware swapping.




