#!/usr/bin/env python

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Simple teleoperation script for SO-101 Leader and Follower arms.
This directly maps leader joint positions to follower joint positions.
"""

import time

from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig
from lerobot.utils.robot_utils import busy_wait

# Control loop frequency
FPS = 30

# Configure your ports (from agents.md)
LEADER_PORT = "/dev/tty.usbmodem5A7A0574331"
FOLLOWER_PORT = "/dev/tty.usbmodem5A7A0562271"

# Initialize the robot and teleoperator config
# Note: id=None matches the calibration files created by lerobot-calibrate
follower_config = SO101FollowerConfig(
    port=FOLLOWER_PORT,
    id=None,  # Use None to match calibration file name
    use_degrees=False  # Using normalized -100 to 100 range
)

leader_config = SO101LeaderConfig(
    port=LEADER_PORT,
    id=None,  # Use None to match calibration file name
    use_degrees=False  # Using normalized -100 to 100 range
)

# Initialize the robot and teleoperator
print("Initializing SO-101 Follower and Leader arms...")
print(f"Follower port: {FOLLOWER_PORT}")
print(f"Leader port: {LEADER_PORT}")
follower = SO101Follower(follower_config)
leader = SO101Leader(leader_config)

# Connect to the robot and teleoperator
print("Connecting to follower arm...")
follower.connect(calibrate=True)  # Load calibration or calibrate if needed

print("Connecting to leader arm...")
leader.connect(calibrate=True)  # Load calibration or calibrate if needed

if not follower.is_connected or not leader.is_connected:
    raise ValueError("Failed to connect to robot or teleoperator!")

print("\n" + "="*60)
print("✅ SO-101 Teleoperation Active!")
print("="*60)
print("Move the LEADER arm, and the FOLLOWER arm will follow.")
print("Press Ctrl+C to stop.\n")

try:
    iteration = 0
    while True:
        t0 = time.perf_counter()

        # Get leader arm position
        leader_action = leader.get_action()

        # Send the same action to follower (direct joint mapping)
        follower.send_action(leader_action)

        # Print status every 30 iterations (once per second at 30 FPS)
        if iteration % 30 == 0:
            print(f"[{iteration:5d}] Leader → Follower | ", end="")
            # Print first 3 joint positions for monitoring
            motors = list(leader_action.keys())[:3]
            for motor in motors:
                val = leader_action[motor]
                print(f"{motor}: {val:6.1f} | ", end="")
            print()

        iteration += 1

        # Maintain consistent loop timing
        elapsed = time.perf_counter() - t0
        busy_wait(max(1.0 / FPS - elapsed, 0.0))

except KeyboardInterrupt:
    print("\n\n🛑 Stopping teleoperation...")

finally:
    print("Disconnecting from arms...")
    follower.disconnect()
    leader.disconnect()
    print("✅ Disconnected successfully!")

