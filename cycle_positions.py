#!/usr/bin/env python3

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
Simple script to cycle SO-101 Follower arm between two positions.
No web UI or Flask - just pure position cycling.
"""

import time
import argparse
import sys
import signal

from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

# Default positions (from your web app recording)
DEFAULT_POSITION_1 = {
    'shoulder_pan': 34.221038615179765,
    'shoulder_lift': -42.34071396294623,
    'elbow_flex': 0.4166666666666714,
    'wrist_flex': 0.10718113612004743,
    'wrist_roll': 0.033411293017039156,
    'gripper': 49.86320109439124
}

DEFAULT_POSITION_2 = {
    'shoulder_pan': -14.114513981358186,
    'shoulder_lift': 32.85133303208315,
    'elbow_flex': 0.4166666666666714,
    'wrist_flex': 0.10718113612004743,
    'wrist_roll': 0.033411293017039156,
    'gripper': 49.86320109439124
}

# Global flag for graceful shutdown
running = True


def signal_handler(sig, frame):
    """Handle Ctrl+C for graceful shutdown."""
    global running
    print("\n\n🛑 Stopping cycle...")
    running = False


def cycle_positions(robot, position_1, position_2, interval, verbose=False):
    """
    Cycle between two positions indefinitely.
    
    Args:
        robot: Connected SO101Follower instance
        position_1: First position dictionary
        position_2: Second position dictionary
        interval: Time in seconds between moves
        verbose: Print detailed status
    """
    global running
    
    print("\n" + "="*60)
    print("🔄 Starting Position Cycling")
    print("="*60)
    print(f"Position 1: {position_1}")
    print(f"Position 2: {position_2}")
    print(f"Interval: {interval} seconds")
    print(f"Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    current_target = 1  # Start with position 1
    cycle_count = 0
    
    while running:
        try:
            # Select target position
            if current_target == 1:
                target_position = position_1
                position_name = "Position 1"
            else:
                target_position = position_2
                position_name = "Position 2"
            
            # Send robot to target position
            action = {f"{motor}.pos": pos for motor, pos in target_position.items()}
            robot.send_action(action)
            
            cycle_count += 1
            print(f"[Cycle {cycle_count}] Moving to {position_name}")
            
            if verbose:
                # Wait a bit then read actual position
                time.sleep(0.5)
                try:
                    obs = robot.get_observation()
                    print(f"  Actual positions: {obs}")
                except Exception as e:
                    print(f"  (Could not read positions: {e})")
            
            # Toggle target for next iteration
            current_target = 2 if current_target == 1 else 1
            
            # Wait for the interval (check running flag periodically)
            sleep_time = 0
            while sleep_time < interval and running:
                time.sleep(0.5)
                sleep_time += 0.5
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚠️  Error during cycle: {e}")
            if not running:
                break
            print("Continuing...")
    
    print(f"\n✅ Completed {cycle_count} cycles")


def main():
    """Main entry point."""
    global running
    
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Cycle SO-101 Follower arm between two positions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Cycle with 15 second interval (default)
  python3 cycle_positions.py
  
  # Cycle with 5 second interval
  python3 cycle_positions.py --interval 5
  
  # Use custom port and 10 second interval
  python3 cycle_positions.py --port /dev/tty.usbmodem5A7A0562271 --interval 10
  
  # Verbose mode
  python3 cycle_positions.py -v --interval 3
        """
    )
    
    parser.add_argument('--interval', '-i', type=float, default=15.0,
                        help='Time in seconds between position changes (default: 15)')
    parser.add_argument('--port', '-p', type=str, default='/dev/ttyACM0',
                        help='Serial port for robot (default: /dev/ttyACM0 for Linux, use /dev/tty.usbmodem5A7A0562271 for macOS)')
    parser.add_argument('--mac', action='store_true',
                        help='Use macOS port (/dev/tty.usbmodem5A7A0562271)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print detailed position information')
    parser.add_argument('--center-first', '-c', action='store_true',
                        help='Move to center position before starting cycle')
    
    args = parser.parse_args()
    
    # Determine port
    if args.mac:
        port = '/dev/tty.usbmodem5A7A0562271'
    else:
        port = args.port
    
    # Validate interval
    if args.interval < 0.5:
        print("⚠️  Warning: Interval too short, setting to 0.5 seconds minimum")
        args.interval = 0.5
    
    robot = None
    
    try:
        # Initialize robot
        print("Initializing SO-101 Follower arm...")
        print(f"Port: {port}")
        
        config = SO101FollowerConfig(
            port=port,
            id=None,  # Use None to match calibration file name
            use_degrees=False  # Using normalized -100 to 100 range
        )
        
        robot = SO101Follower(config)
        
        print("Connecting to follower arm...")
        robot.connect(calibrate=True)
        
        if not robot.is_connected:
            print("❌ Failed to connect to robot!")
            return 1
        
        print("✅ Robot connected successfully!")
        
        # Move to center if requested
        if args.center_first:
            print("\nMoving to center position first...")
            center_action = {
                "shoulder_pan.pos": 0.0,
                "shoulder_lift.pos": 0.0,
                "elbow_flex.pos": 0.0,
                "wrist_flex.pos": 0.0,
                "wrist_roll.pos": 0.0,
                "gripper.pos": 50.0
            }
            robot.send_action(center_action)
            time.sleep(2.0)
            print("✅ Centered")
        
        # Start cycling
        cycle_positions(
            robot,
            DEFAULT_POSITION_1,
            DEFAULT_POSITION_2,
            args.interval,
            verbose=args.verbose
        )
        
        # Return to center on exit
        if robot.is_connected:
            print("\nReturning to center position...")
            center_action = {
                "shoulder_pan.pos": 0.0,
                "shoulder_lift.pos": 0.0,
                "elbow_flex.pos": 0.0,
                "wrist_flex.pos": 0.0,
                "wrist_roll.pos": 0.0,
                "gripper.pos": 50.0
            }
            robot.send_action(center_action)
            time.sleep(1.0)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        if args.verbose:
            print(f"\nFull traceback:\n{traceback.format_exc()}")
        return 1
    
    finally:
        # Cleanup
        if robot and robot.is_connected:
            print("\nDisconnecting robot...")
            robot.disconnect()
            print("✅ Robot disconnected")


if __name__ == '__main__':
    sys.exit(main())

