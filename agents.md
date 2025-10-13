# SO-101 Setup & Configuration Guide

## 🔌 USB Ports
- **Leader Arm:** `/dev/tty.usbmodem5A7A0574331`
- **Follower Arm:** `/dev/tty.usbmodem5A7A0562271`

## 📁 Calibration Files Location
Calibration files are stored in: `/Users/drew/.cache/huggingface/lerobot/calibration/`
- Teleoperators: `/Users/drew/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader/`
- Robots: `/Users/drew/.cache/huggingface/lerobot/calibration/robots/so101_follower/`

## ⚠️ IMPORTANT: Always Activate venv!
```bash
# ALWAYS activate the virtual environment first!
source venv/bin/activate

# Use python3, not python
python3 your_script.py
```

## 🔧 Calibration Commands
```bash
# Calibrate LEADER arm (must be done separately)
lerobot-calibrate --teleop.type=so101_leader --teleop.port=/dev/tty.usbmodem5A7A0574331

# Calibrate FOLLOWER arm (must be done separately)
lerobot-calibrate --robot.type=so101_follower --robot.port=/dev/tty.usbmodem5A7A0562271
```

**Note:** You cannot calibrate both at once - the script only allows teleop OR robot, not both.

**Troubleshooting Calibration:**
- If motors aren't detected, power cycle the arm and wait 5 seconds
- If USB port changes, use `ls -la /dev/tty.usb*` to find new port
- Run `python3 reset_bus.py` if connection gets stuck

## 🎮 Teleoperation
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

## 🎉 ISSUES FOUND AND FIXED!

### Issue 1: Missing Goal_Velocity and Acceleration (CRITICAL)

**Problem:** Feetech STS3215 servos in POSITION mode require THREE parameters for smooth movement, but lerobot was only setting one:

**Required Parameters:**
1. ✅ `Goal_Position` - WHERE to move (was being set)
2. ❌ `Goal_Velocity` - HOW FAST to move (was MISSING!)
3. ❌ `Acceleration` - HOW SMOOTHLY to accelerate (was MISSING!)

**Symptoms:**
- Motors don't move at all (without Goal_Velocity)
- OR motors move but very jerky (without Acceleration)
- Present_Current stays at 0 (no power to motor windings)

**The Fix:**

**Files Modified:**
- `src/lerobot/robots/so101_follower/so101_follower.py`
- `src/lerobot/robots/so100_follower/so100_follower.py`

**Code Changes:**
```python
# OLD (didn't work):
self.bus.sync_write("Goal_Position", goal_pos)

# NEW (works smoothly!):
self.bus.sync_write("Goal_Position", goal_pos)
goal_vel = {motor: 600 for motor in goal_pos}      # Speed
goal_acc = {motor: 20 for motor in goal_pos}       # Smoothness
self.bus.sync_write("Goal_Velocity", goal_vel)
self.bus.sync_write("Acceleration", goal_acc)
```

**Tuning Guide:**

**Goal_Velocity** (speed):
- 50-100: Slow, precise
- 200-400: Moderate, responsive
- **600: Fast, smooth (recommended)** ✨
- 800+: Very fast (use with caution)

**Acceleration** (smoothness vs responsiveness):
- **20: Smooth, gentle (recommended for 30 Hz control)** ✨
- 30-40: More responsive (needs lower control rate ~20 Hz)
- 50+: Very responsive but can be jerky at high update rates

**Key Insight:** Acceleration must match your control loop frequency!
- High update rate (30 Hz) → Lower acceleration (15-25) for smoothness
- Low update rate (20 Hz) → Higher acceleration (30-50) works fine

---

### Issue 2: Calibration EPROM Write Failures

**Problem:** Calibration would record motor ranges but fail when writing to EPROM with:
```
ConnectionError: Failed to write 'Min_Position_Limit' [...] There is no status packet!
```

**Root Causes:**
1. EPROM writes are SLOW (5-50ms) and need time between writes
2. Lock parameter must be 0 to allow EPROM writes
3. No retries on failed EPROM operations
4. Continuous position reads during calibration could overload the bus

**The Fixes:**

**Files Modified:**
- `src/lerobot/robots/so101_follower/so101_follower.py`
- `src/lerobot/motors/motors_bus.py`
- `src/lerobot/motors/feetech/feetech.py`

**Changes Applied:**

1. **Unlock EPROM before calibration** (so101_follower.py):
```python
self.bus.disable_torque()
# Unlock EPROM for writing by setting Lock=0
for motor in self.bus.motors:
    self.bus.write("Lock", motor, 0, num_retry=2)
time.sleep(0.2)  # Give motors time to unlock
```

2. **Add retries and delays to EPROM writes** (motors_bus.py, feetech.py):
```python
# All EPROM writes now have:
self.write("Min_Position_Limit", motor, value, num_retry=3)
time.sleep(0.05)  # Delay between EPROM writes
```

3. **Add retries to position reads** (motors_bus.py):
```python
positions = self.sync_read("Present_Position", motors, num_retry=3)
time.sleep(0.01)  # Prevent bus overload during continuous reading
```

**Result:** Calibration now completes successfully every time! ✅

---

## 📊 Performance Diagnostics

Use `diagnose_teleoperation.py` to check your control loop performance:

```bash
python3 diagnose_teleoperation.py
```

**Good Performance Metrics:**
- Actual frequency: ≥27 Hz (90% of 30 Hz target)
- Loop time: <33ms average
- Jitter (StdDev): <3ms
- Read time: <2ms
- Write time: <1ms

**If you see jerkiness:**
1. Check actual Hz (should be near 30)
2. Check jitter/StdDev (should be low)
3. If both are good → adjust Acceleration (lower = smoother)
4. If frequency is low → optimize code or reduce update rate

---

## 💡 Understanding Feetech STS3215 Motor Control

**Operating_Mode = 0 (POSITION mode):**
- Motor moves to `Goal_Position` at `Goal_Velocity`
- `Acceleration` controls how smoothly it speeds up/slows down
- `Lock=1` engages torque to hold position (this is CORRECT!)
- All three parameters MUST be set for movement

**Control Table Registers (useful for debugging):**
- Address 40: `Torque_Enable` (0=off, 1=on)
- Address 42: `Goal_Position` (target position)
- Address 46: `Goal_Velocity` (movement speed)
- Address 41: `Acceleration` (acceleration rate)
- Address 55: `Lock` (0=EPROM writable, 1=position control engaged)
- Address 56: `Present_Position` (current position, read-only)
- Address 69: `Present_Current` (current draw, read-only)

**The "Lock" Parameter Explained:**
- When `Lock=1`: Motor engages position control with torque (normal operation)
- When `Lock=0`: Motor is in free-wheel mode OR EPROM is writable
- During calibration: Must set `Lock=0` to write min/max position limits
- During operation: Must set `Lock=1` for motor to hold position and move

---

## 📁 Useful Scripts Created

- `teleop_so101.py` - Main teleoperation script (30 Hz control loop)
- `diagnose_teleoperation.py` - Performance diagnostics and loop timing analysis
- `reset_bus.py` - Reset motor bus when connection gets stuck
- `check_operating_mode.py` - Verify motors are in correct Operating_Mode
- `test_goal_velocity.py` - Empirical test proving Goal_Velocity is required

---

## ✅ Current Status

**Everything is working!** 🎉

The SO-101 follower arm now:
- ✅ Moves smoothly during teleoperation
- ✅ Calibrates successfully without EPROM errors
- ✅ Runs at stable 30 Hz with low jitter
- ✅ Has proper Goal_Velocity and Acceleration set
- ✅ Responds naturally to leader arm movements

**Optimal Settings Found:**
- Control frequency: 30 Hz
- Goal_Velocity: 600
- Acceleration: 20
- Lock: 1 (during operation)
- Operating_Mode: 0 (POSITION mode)
