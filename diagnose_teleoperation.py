#!/usr/bin/env python3

"""
Diagnose teleoperation performance to identify jerkiness causes.
Measures actual loop frequency, timing, and motor response.
"""

import time
import statistics
from collections import deque

from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig
from lerobot.utils.robot_utils import busy_wait

# Target control loop frequency
TARGET_FPS = 30
TARGET_DT = 1.0 / TARGET_FPS

# Configure ports
LEADER_PORT = "/dev/tty.usbmodem5A7A0574331"
FOLLOWER_PORT = "/dev/tty.usbmodem5A7A0562271"

# Configure robots
follower_config = SO101FollowerConfig(port=FOLLOWER_PORT, id=None, use_degrees=False)
leader_config = SO101LeaderConfig(port=LEADER_PORT, id=None, use_degrees=False)

print("="*70)
print("Teleoperation Performance Diagnostics")
print("="*70)
print()

# Initialize
print("Connecting to arms...")
follower = SO101Follower(follower_config)
leader = SO101Leader(leader_config)

follower.connect(calibrate=True)
leader.connect(calibrate=True)

print("✅ Connected to both arms")
print()
print(f"Target frequency: {TARGET_FPS} Hz (every {TARGET_DT*1000:.1f} ms)")
print()
print("Running performance test for 10 seconds...")
print("Move the leader arm to generate realistic workload.")
print()

# Timing measurements
loop_times = deque(maxlen=300)  # Store last 300 samples (10 seconds at 30 Hz)
read_times = deque(maxlen=300)
write_times = deque(maxlen=300)

try:
    iteration = 0
    test_duration = 10.0  # 10 seconds
    start_time = time.perf_counter()
    
    while time.perf_counter() - start_time < test_duration:
        loop_start = time.perf_counter()
        
        # Measure leader read time
        read_start = time.perf_counter()
        leader_action = leader.get_action()
        read_elapsed = time.perf_counter() - read_start
        read_times.append(read_elapsed)
        
        # Measure follower write time
        write_start = time.perf_counter()
        follower.send_action(leader_action)
        write_elapsed = time.perf_counter() - write_start
        write_times.append(write_elapsed)
        
        # Maintain loop timing
        loop_elapsed = time.perf_counter() - loop_start
        loop_times.append(loop_elapsed)
        
        # Print live stats every second
        if iteration % TARGET_FPS == 0 and iteration > 0:
            actual_fps = 1.0 / statistics.mean(list(loop_times)[-30:])
            print(f"[{iteration:3d}] Actual: {actual_fps:.1f} Hz | "
                  f"Loop: {statistics.mean(list(loop_times)[-30:])*1000:.1f}ms | "
                  f"Read: {statistics.mean(list(read_times)[-30:])*1000:.1f}ms | "
                  f"Write: {statistics.mean(list(write_times)[-30:])*1000:.1f}ms")
        
        iteration += 1
        
        # Wait to maintain target frequency
        busy_wait(max(TARGET_DT - loop_elapsed, 0.0))
    
    print()
    print("="*70)
    print("PERFORMANCE ANALYSIS")
    print("="*70)
    print()
    
    # Calculate statistics
    avg_loop_time = statistics.mean(loop_times)
    avg_read_time = statistics.mean(read_times)
    avg_write_time = statistics.mean(write_times)
    avg_fps = 1.0 / avg_loop_time
    
    max_loop_time = max(loop_times)
    min_loop_time = min(loop_times)
    stdev_loop_time = statistics.stdev(loop_times)
    
    print(f"Target Frequency:  {TARGET_FPS:.1f} Hz ({TARGET_DT*1000:.1f} ms per cycle)")
    print(f"Actual Frequency:  {avg_fps:.1f} Hz ({avg_loop_time*1000:.1f} ms per cycle)")
    print()
    print(f"Average Timings:")
    print(f"  Leader read:     {avg_read_time*1000:.2f} ms")
    print(f"  Follower write:  {avg_write_time*1000:.2f} ms")
    print(f"  Busy wait:       {max(TARGET_DT - avg_loop_time, 0)*1000:.2f} ms")
    print(f"  Total loop:      {avg_loop_time*1000:.2f} ms")
    print()
    print(f"Loop Time Variability:")
    print(f"  Min:    {min_loop_time*1000:.2f} ms")
    print(f"  Max:    {max_loop_time*1000:.2f} ms")
    print(f"  StdDev: {stdev_loop_time*1000:.2f} ms")
    print()
    
    # Diagnose issues
    print("="*70)
    print("DIAGNOSIS")
    print("="*70)
    print()
    
    if avg_fps < TARGET_FPS * 0.9:
        print("❌ SLOW LOOP: Not hitting target frequency!")
        print(f"   Running at {avg_fps:.1f} Hz instead of {TARGET_FPS} Hz")
        print(f"   This will cause jerky motion.")
        print()
        if avg_write_time > TARGET_DT * 0.5:
            print("   → Follower writes are too slow")
            print("   → Consider reducing communication overhead")
        if avg_read_time > TARGET_DT * 0.3:
            print("   → Leader reads are slow")
    else:
        print("✅ Loop frequency OK")
        print()
    
    if stdev_loop_time > TARGET_DT * 0.1:
        print("⚠️  HIGH JITTER: Loop timing is inconsistent")
        print(f"   Standard deviation: {stdev_loop_time*1000:.2f} ms")
        print(f"   This causes irregular, jerky motion")
        print()
    else:
        print("✅ Loop timing consistent")
        print()
    
    if avg_fps >= TARGET_FPS * 0.9 and stdev_loop_time < TARGET_DT * 0.1:
        print("✅ Control loop is NOT the problem!")
        print()
        print("Jerkiness is likely due to:")
        print("  1. Goal_Velocity too low (try 400-600)")
        print("  2. Missing Goal_Acceleration (motors start/stop abruptly)")
        print("  3. PID tuning (P_Coefficient=16 might be too low)")
        print()
        print("Try increasing Goal_Velocity to 400 first.")
    
    print()
    print("="*70)

except KeyboardInterrupt:
    print("\n\nTest interrupted by user")

finally:
    print("\nDisconnecting...")
    follower.disconnect()
    leader.disconnect()
    print("✅ Done")

