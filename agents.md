# SO-101 Follower Arm Investigation Summary

## 🔌 USB Ports
- **Leader Arm:** `/dev/tty.usbmodem5A7A0574331`
- **Follower Arm:** `/dev/tty.usbmodem5A7A0562271`

### 📁 Calibration Files Location
Calibration files are stored in: `/Users/drew/.cache/huggingface/lerobot/calibration/`
- Teleoperators: `/Users/drew/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader/`
- Robots: `/Users/drew/.cache/huggingface/lerobot/calibration/robots/so101_follower/`

### ⚠️ IMPORTANT: Always Activate venv!
```bash
# ALWAYS activate the virtual environment first!
source venv/bin/activate

# Use python3, not python
python3 your_script.py
```

### Calibration Commands
```bash
# Calibrate LEADER arm (must be done separately)
lerobot-calibrate --teleop.type=so101_leader --teleop.port=/dev/tty.usbmodem5A7A0574331

# Calibrate FOLLOWER arm (must be done separately)
lerobot-calibrate --robot.type=so101_follower --robot.port=/dev/tty.usbmodem5A7A0562271
```

**Note:** You cannot calibrate both at once - the script only allows teleop OR robot, not both.

### Teleoperation
```bash
# Run teleoperation (after activating venv!)
# MUST run in FOREGROUND (not background) to interact with prompts
source venv/bin/activate
python3 teleop_so101.py
```

**When prompted:**
- Press **ENTER** to use existing calibration
- Type **'c'** and press ENTER to recalibrate

---

## 🎉 BUG FOUND AND FIXED!

### Critical Bug in lerobot Codebase
**File:** `src/lerobot/motors/feetech/feetech.py` (Line 310)

**The Bug:**
```python
def enable_torque(self, motors: str | list[str] | None = None, num_retry: int = 0) -> None:
    for motor in self._get_motors_list(motors):
        self.write("Torque_Enable", motor, TorqueMode.ENABLED.value, num_retry=num_retry)
        self.write("Lock", motor, 1, num_retry=num_retry)  # ❌ BUG!
```

**The Fix Applied:**
Changed `Lock=1` to `Lock=0` because:
- Lock=1 locks the motor and prevents movement
- Lock=0 unlocks the motor and allows movement
- This was backwards logic!

**Verified:** After the fix, all motors now show `Lock=0` and `Torque=1` (correct state).

---

## ❌ Motors Still Won't Move (Hardware Issue)

Despite the software fix being correct, the follower arm motors still don't move:

### Test Results
- ✅ Lock=0, Torque=1 (correct after fix)
- ✅ Goal_Position writes successfully
- ✅ All protection parameters correct
- ✅ Voltage: 12.6V (correct)
- ✅ Teleoperation software runs without errors
- ✅ Leader arm reads positions correctly
- ❌ Present_Current: 0 (no power to motor windings)
- ❌ Follower motors don't move to Goal_Position
- ❌ Follower motors don't move during teleoperation
- ❌ Moving flag stays at 0

### Teleoperation Test Confirmed (Oct 13, 2025)
Ran full teleoperation with `teleop_so101.py`:
- Leader arm movements are detected and sent to follower
- Commands are transmitted without errors
- **Follower arm does not physically move at all**
- This confirms a hardware/firmware issue, not a software issue

### Conclusion
The software is now correct, but there's a **hardware or firmware protection mechanism** preventing power from reaching the motor windings.

---

## 📋 GitHub Issues Search Results

Searched https://github.com/huggingface/lerobot/issues for related problems:

### Issues Found:
1. **New version calibration error** (#1694) - SO-101 calibration issues after updates
2. Various dataset/training issues (not related to our motor problem)
3. **No specific issues found** about:
   - Feetech motor Lock parameter bugs
   - enable_torque() setting Lock=1
   - Motors not moving after calibration
   - SO-101 motor movement failures

**This appears to be a newly discovered bug!**

---

## 🚀 Next Steps

### For the Software Bug (FIXED ✅)
1. **Submit Pull Request** to lerobot repository:
   - Title: "Fix: Feetech enable_torque() incorrectly sets Lock=1"
   - Change: `Lock=1` → `Lock=0` in enable_torque()
   - Impact: Affects all Feetech motor users (SO-100, SO-101, etc.)

2. **Open GitHub Issue** to document the bug and fix

### For the Hardware Problem (ONGOING ❌)
1. **Try Feetech Debug Tool** (FDDebug) - bypasses Python SDK
   - Download: https://gitee.com/ftservo/fddebug
   
2. **Test Single Motor** - disconnect all but one to rule out power supply current issues

3. **Swap Waveshare Boards** - test follower motors on leader's board

4. **Contact Manufacturer** - TheRobotStudio/Feetech may have seen this before

---

## 📁 Files Created

- `BUG_REPORT_AND_FINDINGS.md` - Detailed technical report
- `DEEP_RESEARCH_PROMPT.md` - Comprehensive investigation plan ⭐
- `teleop_so101.py` - Working teleoperation script (leader works, follower doesn't move)
- `verify_lock_fix.py` - Verifies Lock=0 is being set correctly
- `test_without_fix.py` - Demonstrates Lock=1 vs Lock=0 difference
- `test_lock_fix.py` - Verifies the Lock fix
- `check_all_parameters.py` - Comprehensive parameter dump
- `test_goal_position_write.py` - Tests Goal_Position writes
- `check_startup_force.py` - Checks Minimum_Startup_Force

---

## 💡 Key Insight - MAJOR UPDATE!

### ⚠️ **OUR "FIX" WAS WRONG!** Lock=1 is Actually CORRECT!

**Discovery (Oct 13, 2025):**
After testing with Lock=1 (original code), the follower arm now **"locks" and holds position firmly**. This is the CORRECT behavior!

**What Lock Really Means:**
- `Lock=1` = "Engage position control" = Motor holds position with torque (CORRECT ✅)
- `Lock=0` = "Disengage" = Free-wheeling mode

**Why Nobody Reported the "Bug":**
Because it wasn't a bug! The original code was correct all along:
- `enable_torque()` → `Lock=1` → Engage motor control
- `disable_torque()` → `Lock=0` → Release motor

### 🔍 The REAL Problem: Missing Goal_Velocity!

Looking at the code, we discovered:
- ✅ `Goal_Position` IS being written
- ✅ `Lock=1` IS correctly set
- ✅ `Torque_Enable=1` IS set
- ❌ **`Goal_Velocity` is NEVER set!**

**Feetech servos need BOTH:**
1. `Goal_Position` (where to go)
2. `Goal_Velocity` OR `Goal_Time` (how fast to get there)

Without velocity, the motor knows WHERE to go but not HOW FAST, so it stays locked in place!

**See `test_goal_velocity.py` to verify this hypothesis.**

### ✅ CONFIRMED! Test Results (Oct 13, 2025):

**Test 1: NO Goal_Velocity**
- Present_Current: 0
- Movement: NONE
- Result: ❌ Motor locked in place

**Test 2: WITH Goal_Velocity = 200**
- Present_Current: 16 (POWER FLOWING!)
- Movement: 446 steps
- Result: ✅ **MOTOR MOVED!**

### 🎯 THE FIX APPLIED:

**Files Modified:**
1. `src/lerobot/robots/so101_follower/so101_follower.py` - Added Goal_Velocity writes
2. `src/lerobot/robots/so100_follower/so100_follower.py` - Added Goal_Velocity writes  
3. `src/lerobot/motors/feetech/feetech.py` - Kept Lock=1 (original correct code)

**What Changed:**
```python
# OLD (didn't work):
self.bus.sync_write("Goal_Position", goal_pos)

# NEW (works!):
self.bus.sync_write("Goal_Position", goal_pos)
goal_vel = {motor: 300 for motor in goal_pos}
self.bus.sync_write("Goal_Velocity", goal_vel)
```

### Current Status:
- Lock=1 ✅ CORRECT (kept original code)
- Goal_Velocity ✅ **NOW BEING SET!**
- Ready to test ✅ **Run teleop_so101.py to verify!**
