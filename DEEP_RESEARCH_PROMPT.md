# Deep Research Investigation: SO-101 Follower Arm Movement Failure

## The Mystery

A Feetech motor Lock parameter bug was discovered in the lerobot codebase where `enable_torque()` sets `Lock=1` instead of `Lock=0`. However:

1. **The bug has existed since July 2024** (commit d4ee470b) - over 3 months
2. **Affects ALL Feetech motor users** (SO-100, SO-101 robots)
3. **NO GitHub issues exist** about this problem
4. **The "fix" doesn't solve the problem** - follower arm still doesn't move

**Key Question:** Why has nobody else reported this if it's such a critical bug?

---

## Current Situation

### What We Know Works:
- ✅ Leader arm (teleoperator) reads positions perfectly
- ✅ USB communication to all 6 follower motors works
- ✅ Calibration completes successfully for both arms
- ✅ Software sends commands without errors
- ✅ Lock parameter can be read and written (verified with test scripts)
- ✅ After "fix": Lock=0, Torque=1 (what we think is correct)
- ✅ Goal_Position writes successfully to follower motors
- ✅ Teleoperation loop runs at 30 FPS with leader position changes

### What Doesn't Work:
- ❌ Follower motors don't physically move at all
- ❌ Present_Current always reads 0 (no power to motor windings)
- ❌ Moving flag stays at 0
- ❌ Present_Position never changes

### Hardware Setup:
- **Leader Arm:** `/dev/tty.usbmodem5A7A0574331` (works perfectly)
- **Follower Arm:** `/dev/tty.usbmodem5A7A0562271` (doesn't move)
- **Motors:** Feetech STS3215 servos (6 per arm)
- **Controller:** Waveshare Bus Servo Adapter boards
- **Power:** 12.6V confirmed at motors
- **OS:** macOS (darwin 24.5.0)
- **Codebase:** lerobot main branch with one modification (Lock=1→0)

---

## Investigation Questions

### 1. Lock Parameter Behavior Investigation

**Question:** Does Lock=1 actually prevent motor movement in Feetech STS3215 servos?

**Research Tasks:**
- [ ] Find official Feetech STS3215 documentation/datasheet
- [ ] Locate control table specification for register 55 (Lock)
- [ ] Determine exact behavior: Does Lock=1 prevent:
  - Goal_Position writes?
  - Motor current activation?
  - Position changes?
  - All of the above?
- [ ] Check if Lock parameter behavior changed between firmware versions
- [ ] Verify if Lock affects follower vs leader arms differently

**Resources to Check:**
- Feetech official docs: https://gitee.com/ftservo
- TheRobotStudio documentation
- SCServo SDK source code
- Community forums/discussions

### 2. Historical Usage Analysis

**Question:** How are other users successfully operating SO-100/SO-101 robots with Lock=1?

**Research Tasks:**
- [ ] Search GitHub for SO-100/SO-101 usage examples
- [ ] Find video demonstrations of working SO-100/SO-101 robots
- [ ] Check if users bypass `enable_torque()` and manually configure motors
- [ ] Look for custom initialization scripts in issues/discussions
- [ ] Check if calibration process sets different Lock values
- [ ] Investigate if `disable_torque_on_disconnect` config affects behavior

**GitHub Search Queries:**
- "SO-101 teleoperation" in:code
- "SO-100 follower" in:code,issues,discussions
- "enable_torque" path:examples/
- "Feetech motor" in:issues

### 3. Leader vs Follower Comparison

**Question:** Why does the leader arm work but follower doesn't with same Lock parameter?

**Research Tasks:**
- [ ] Compare `SO101Leader` vs `SO101Follower` class implementations
- [ ] Check if leader arm bypasses `enable_torque()` somehow
- [ ] Investigate if `disable_torque()` is called on leader (sets Lock=0)
- [ ] Compare motor configuration between leader and follower
- [ ] Check if leader uses different Operating_Mode or other parameters
- [ ] Verify if calibration writes different values for leader vs follower

**Code Locations:**
- `src/lerobot/teleoperators/so101_leader/so101_leader.py`
- `src/lerobot/robots/so101_follower/so101_follower.py`

### 4. Alternative Explanation: Not a Lock Bug?

**Question:** What if Lock=1 is actually correct and the problem is elsewhere?

**Research Tasks:**
- [ ] Investigate Minimum_Startup_Force parameter (currently 16)
  - Is this too high?
  - Should it be 0 for follower motors?
- [ ] Check Torque_Limit (500) - is this preventing movement?
- [ ] Verify Protection_Current (250) isn't triggering falsely
- [ ] Check if Operating_Mode needs different value for follower
- [ ] Investigate if Goal_Velocity needs to be set (not just Goal_Position)
- [ ] Check if Acceleration needs configuration
- [ ] Verify if multiple writes needed (Goal_Position + Go command?)

**Parameter List to Investigate:**
```
Lock: 0
Torque_Enable: 1
Torque_Limit: 500
Minimum_Startup_Force: 16  ⬅️ SUSPICIOUS?
Protection_Current: 250
Operating_Mode: 0
Goal_Position: [written successfully]
Goal_Velocity: [not set?]  ⬅️ MISSING?
Acceleration: [not set?]    ⬅️ MISSING?
```

### 5. Hardware-Specific Investigation

**Question:** Is this a macOS-specific, Waveshare board-specific, or firmware issue?

**Research Tasks:**
- [ ] Check if macOS USB drivers behave differently than Linux
- [ ] Search for Waveshare Bus Servo Adapter known issues
- [ ] Check if firmware version on follower motors differs from leader
- [ ] Investigate if power supply current limiting is the issue
- [ ] Compare motor IDs 1-6 follower vs 1-6 leader (same IDs, different boards)
- [ ] Check if serial communication timing differs between boards

### 6. Calibration Process Analysis

**Question:** Does calibration set parameters that override enable_torque()?

**Research Tasks:**
- [ ] Review `bus.write_calibration()` implementation
- [ ] Check what parameters calibration actually writes to motors
- [ ] Verify if calibration sets Lock parameter
- [ ] See if `configure()` method overwrites Lock value
- [ ] Check calibration JSON files for hidden parameters
- [ ] Compare working examples' calibration values

**Files to Examine:**
- `/Users/drew/.cache/huggingface/lerobot/calibration/robots/so101_follower/None.json`
- `/Users/drew/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader/None.json`

### 7. Communication Protocol Deep Dive

**Question:** Are commands actually reaching the motors correctly?

**Research Tasks:**
- [ ] Enable verbose logging in FeetechMotorsBus
- [ ] Capture actual serial communication with Wireshark/logic analyzer
- [ ] Verify write acknowledgments are received
- [ ] Check if Goal_Position write is being overwritten by something
- [ ] Investigate if sync_write vs individual write makes a difference
- [ ] Check baudrate/timeout settings

### 8. Working Examples Investigation

**Question:** Are there any known-working SO-101 follower deployments?

**Research Tasks:**
- [ ] Find Hugging Face team demonstrations of SO-101
- [ ] Check if TheRobotStudio has reference implementations
- [ ] Search YouTube for SO-101 teleoperation videos
- [ ] Contact maintainers who added SO-101 support (git log authors)
- [ ] Check if SO-100 works but SO-101 doesn't (or vice versa)

**Git Authors to Research:**
```bash
git log --format="%an <%ae>" -- src/lerobot/robots/so101_follower/ | sort -u
git log --format="%an <%ae>" -- src/lerobot/motors/feetech/ | sort -u
```

### 9. Comparison with SO-100

**Question:** Does SO-100 have the same issue? It uses identical code.

**Research Tasks:**
- [ ] Check if SO-100 follower movement has been reported working
- [ ] Compare SO-100 vs SO-101 motor specifications
- [ ] Verify if firmware versions differ
- [ ] Check if control table addresses differ
- [ ] Look for any SO-100 workarounds that might apply

### 10. Register Read/Write Validation

**Question:** Can we read back Goal_Position after writing it?

**Research Tasks:**
- [ ] Write Goal_Position, immediately read Goal_Position - does it match?
- [ ] Check if Goal_Position read-back differs from write value
- [ ] Test if Present_Position ever updates (even slightly)
- [ ] Monitor if Present_Current ever becomes non-zero
- [ ] Check if Moving flag ever becomes 1
- [ ] Verify Status register for error codes

---

## Hypotheses to Test

### Hypothesis 1: Lock=1 is Actually Correct
**Evidence For:**
- Code existed for 3+ months without reports
- Leader arm might work because it's only reading, not commanding
- Maybe follower needs Lock=1 to follow (backwards logic?)

**Test:** Try Lock=1 on leader, Lock=0 on follower - does anything change?

### Hypothesis 2: Additional Initialization Required
**Evidence For:**
- Present_Current = 0 suggests motor controller isn't activated
- Might need specific sequence of commands
- Missing Goal_Velocity or Acceleration setup

**Test:** Try setting Goal_Velocity and Acceleration parameters before movement

### Hypothesis 3: Waveshare Board Hardware Issue
**Evidence For:**
- Leader board works, follower doesn't
- Same motors, different boards
- Power supply might not deliver enough current

**Test:** Swap boards - connect follower motors to leader board

### Hypothesis 4: Firmware Protection Mechanism
**Evidence For:**
- All parameters appear correct
- No software errors
- Motors actively preventing movement

**Test:** Use Feetech's official FDDebug tool to bypass SDK

### Hypothesis 5: macOS-Specific Issue
**Evidence For:**
- Unusual platform for robotics
- USB serial driver differences
- Timing or buffering issues

**Test:** Try on Linux machine

### Hypothesis 6: Present_Position Never Recorded During Calibration
**Evidence For:**
- Calibration might have failed silently
- Range_min/range_max might be invalid
- Motors might be outside valid range

**Test:** Examine calibration JSON files, try forcing recalibration with different positions

---

## Recommended Investigation Order

### Phase 1: Quick Validation (15 minutes)
1. Read follower calibration JSON files - verify they're valid
2. Check if Goal_Position read-back matches write
3. Try setting Goal_Velocity parameter
4. Test with Minimum_Startup_Force = 0

### Phase 2: Deep Comparison (30 minutes)
5. Compare leader vs follower configuration line-by-line
6. Search GitHub for working SO-101 examples
7. Review official Feetech documentation for Lock parameter
8. Check if other users manually configure motors differently

### Phase 3: Hardware Testing (1 hour)
9. Swap Waveshare boards
10. Try FDDebug tool
11. Test single motor disconnected from others
12. Measure actual current draw with multimeter

### Phase 4: Community Research (1 hour)
13. Search for SO-100/SO-101 YouTube videos
14. Contact git commit authors
15. Post question in Hugging Face Discord/forums
16. Check TheRobotStudio support channels

---

## Expected Research Outcomes

After completing this investigation, we should be able to answer:

1. **Is Lock=1 actually a bug?** Or is it correct for this use case?
2. **How do other users avoid this issue?** Workarounds? Different configs?
3. **What's really preventing movement?** Lock, or something else entirely?
4. **Why Present_Current = 0?** What activates motor current?
5. **Is this a known issue?** Just not reported on GitHub?

---

## Data to Collect

Please gather and document:

```bash
# 1. Full motor parameter dump when "working" (leader)
python3 check_all_parameters.py [leader_port]

# 2. Full motor parameter dump when "not working" (follower)
python3 check_all_parameters.py [follower_port]

# 3. Calibration files
cat /Users/drew/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader/None.json
cat /Users/drew/.cache/huggingface/lerobot/calibration/robots/so101_follower/None.json

# 4. Git history of relevant files
git log --oneline --all -- src/lerobot/motors/feetech/
git log --oneline --all -- src/lerobot/robots/so101_follower/
git log --oneline --all -- src/lerobot/teleoperators/so101_leader/

# 5. Check for related issues/PRs
gh issue list --repo huggingface/lerobot --search "feetech OR SO-101 OR SO-100"
gh pr list --repo huggingface/lerobot --search "feetech OR SO-101 OR SO-100" --state all

# 6. Motor firmware versions
# Read from motors if possible
```

---

## Success Criteria

Investigation is complete when we can definitively answer:

**Either:**
- ✅ "Lock=1 IS a bug, and here's why others haven't hit it: [explanation]"

**Or:**
- ✅ "Lock=1 is NOT the issue, the real problem is: [actual cause]"

**And we can:**
- ✅ Make the follower arm physically move
- ✅ Explain why the current setup doesn't work
- ✅ Provide reproducible solution/workaround

---

## Notes for LLM Researcher

- **Be skeptical of obvious answers** - if it were simple, others would have hit it
- **Look for community workarounds** - maybe everyone does something we don't
- **Consider timing issues** - maybe immediate writes fail but delayed ones work
- **Check assumptions** - maybe "Lock" doesn't mean what we think it means
- **Find working examples** - seeing it work elsewhere proves it's possible
- **Test alternative explanations** - don't assume the first bug found is the only one

**Most importantly:** If this was a critical bug affecting everyone, it would have been reported. The fact that it hasn't suggests either:
1. We're doing something different from normal usage, OR
2. The Lock parameter isn't actually the problem, OR  
3. There's a workaround everyone uses that we don't know about

