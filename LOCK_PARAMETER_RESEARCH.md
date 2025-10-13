# Lock Parameter Research Findings

## Investigation: Does Lock=1 actually prevent movement?

### Web Search Results Summary

**Finding:** No specific technical documentation found online for the Feetech STS3215 Lock parameter.

**Searches Performed:**
1. "Feetech STS3215 Lock parameter register 55 documentation"
2. "Feetech servo Lock register control table STS SMS series"
3. "SCServo SDK Lock parameter what does it do"
4. "site:gitee.com/ftservo Lock parameter register"
5. "STS3215 control table datasheet PDF"
6. "Lock register 48 OR 55 feetech servo"
7. "TheRobotStudio SO-101 Lock parameter documentation"

**Results:**
- ❌ No official Feetech STS3215 datasheet found
- ❌ No control table documentation with Lock parameter explanation
- ❌ No SO-101 specific Lock parameter documentation
- ❌ SCServo SDK source code doesn't document Lock purpose
- ⚠️  Generic AI-generated responses suggesting Lock might be for "securing position"

### Code Analysis

**From `src/lerobot/motors/feetech/tables.py`:**
```python
"Lock": (55, 1),  # Address 55, 1 byte
```

**No comments explaining what Lock does!**

**From `src/lerobot/motors/feetech/feetech.py`:**

Original implementation (commit d4ee470b, July 2024):
```python
def disable_torque(self, motors: str | list[str] | None = None, num_retry: int = 0) -> None:
    for motor in self._get_motors_list(motors):
        self.write("Torque_Enable", motor, TorqueMode.DISABLED.value, num_retry=num_retry)
        self.write("Lock", motor, 0, num_retry=num_retry)  # Lock=0 when disabling

def enable_torque(self, motors: str | list[str] | None = None, num_retry: int = 0) -> None:
    for motor in self._get_motors_list(motors):
        self.write("Torque_Enable", motor, TorqueMode.ENABLED.value, num_retry=num_retry)
        self.write("Lock", motor, 1, num_retry=num_retry)  # Lock=1 when enabling
```

**Analysis:**
- `disable_torque()` sets `Lock=0` 
- `enable_torque()` originally set `Lock=1`
- No comments explaining the reasoning
- No tests verify Lock behavior
- No GitHub issues about Lock

### Key Observations

1. **Symmetry suggests intention:** 
   - disable → Lock=0
   - enable → Lock=1
   - This suggests the original author thought Lock=1 was the "enabled" or "active" state

2. **Lack of documentation:**
   - Control tables don't explain Lock
   - No manufacturer docs accessible
   - No community knowledge base

3. **No reported issues:**
   - Code existed 3+ months
   - Affects all SO-100/SO-101 users
   - Zero GitHub issues
   - This is the strongest evidence that Lock=1 might be correct!

### Possible Explanations

#### Hypothesis A: Lock=1 is correct, we misunderstood it
**Evidence:**
- Original code was intentional (enable→Lock=1, disable→Lock=0)
- No users reported issues
- "Lock" might not mean "prevent movement"

**Possible meanings of Lock:**
- Lock=1: "Lock in position when stopped" (maintain position with torque)
- Lock=1: "Lock motor settings" (prevent parameter changes)
- Lock=1: "Engage motor control" (activate control loop)
- Lock=0: "Free-wheeling mode" (no position holding)

#### Hypothesis B: Lock doesn't affect movement at all
**Evidence:**
- No current issue reports despite Lock=1 in production
- Our follower still doesn't move with Lock=0
- Lock might be for EEPROM writes or other non-movement functions

#### Hypothesis C: Lock works differently than we think
**Evidence:**
- Feetech motors have quirky behaviors
- Documentation is sparse
- Multiple firmware versions may behave differently

### Empirical Test Needed

We created `test_lock_hypothesis.py` to definitively test:

1. **Test 1:** Lock=0, Torque=1, write Goal_Position → Does it move?
2. **Test 2:** Lock=1, Torque=1, write Goal_Position → Does it move?

**Possible outcomes:**

| Test 1 (Lock=0) | Test 2 (Lock=1) | Conclusion |
|----------------|----------------|------------|
| ✅ Moves | ❌ No move | Lock=1 prevents movement (our "fix" is correct) |
| ❌ No move | ❌ No move | Lock doesn't affect movement (problem is elsewhere) |
| ✅ Moves | ✅ Moves | Lock=1 doesn't prevent movement (original code was fine) |
| ❌ No move | ✅ Moves | Lock has inverted logic (very unlikely) |

### Critical Questions

1. **Why does the leader arm work?**
   - Leader arm uses same `enable_torque()` function
   - Leader should have Lock=1 too (with old code)
   - Yet leader reads positions fine
   - **Key difference:** Leader is only READ, not commanded to move

2. **Is Lock about WRITING or MOVING?**
   - Maybe Lock=1 prevents Goal_Position WRITES
   - Our tests show Goal_Position writes succeed
   - But maybe the writes are ignored by firmware?

3. **Do we need Lock for reading vs commanding?**
   - Leader (read-only): Maybe Lock=1 is fine
   - Follower (commanded): Maybe Lock=0 is required
   - This would explain why leader works but follower doesn't!

### Next Steps

**Priority 1: Run empirical test**
```bash
source venv/bin/activate
python3 test_lock_hypothesis.py
```

This will definitively answer: **Does Lock=1 prevent motor movement?**

**Priority 2: If Lock=0 still doesn't work**
- Check Minimum_Startup_Force parameter
- Try setting Goal_Velocity
- Compare every parameter between leader and follower
- Test with FDDebug tool

**Priority 3: Contact sources**
- Email TheRobotStudio support
- Post in Hugging Face Discord
- Check Feetech/SCServo SDK GitHub issues

### Current Status

**What we know:**
- ✅ Lock can be written and read successfully
- ✅ Lock=0 is being set by our fix
- ✅ Goal_Position writes succeed
- ❌ Follower motors still don't move
- ❌ Present_Current always 0

**What we DON'T know:**
- ❓ Does Lock=1 actually prevent movement?
- ❓ Why has nobody else reported this?
- ❓ What is the official purpose of Lock parameter?
- ❓ Why does leader work but follower doesn't?

### Conclusion

**The Lock parameter remains mysterious.** Without official documentation and with zero community reports of issues, we must:

1. **Test empirically** to determine actual behavior
2. **Be open** to the possibility that Lock=1 is correct
3. **Look elsewhere** for the real cause of non-movement

The fact that NO ONE has reported this suggests either:
- Lock=1 is actually fine
- OR everyone has workarounds we don't know about
- OR we're using the system differently than intended

**Run `test_lock_hypothesis.py` to find out!**

