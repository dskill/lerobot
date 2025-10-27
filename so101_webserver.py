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
Web server for controlling SO-101 Follower arm via touchscreen interface.
This provides a browser-based control panel for manual servo control.
"""

from flask import Flask, render_template_string, jsonify, request
import threading
import time
import logging

from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Robot configuration
FOLLOWER_PORT = "/dev/tty.usbmodem5A7A0562271"  # Update this to match your port

# Global robot instance
robot = None
robot_lock = threading.Lock()
current_positions = {
    "shoulder_pan": 0.0,
    "shoulder_lift": 0.0,
    "elbow_flex": 0.0,
    "wrist_flex": 0.0,
    "wrist_roll": 0.0,
    "gripper": 50.0  # Start gripper at mid-position
}

# HTML template for the control interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SO-101 Robot Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }

        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .status {
            text-align: center;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 30px;
            font-weight: bold;
            font-size: 1.1em;
        }

        .status.connected {
            background: #d4edda;
            color: #155724;
            border: 2px solid #c3e6cb;
        }

        .status.disconnected {
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #f5c6cb;
        }

        .motor-control {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }

        .motor-control:hover {
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }

        .motor-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .motor-name {
            font-size: 1.3em;
            font-weight: bold;
            color: #495057;
        }

        .motor-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
            min-width: 80px;
            text-align: right;
        }

        .slider-container {
            display: flex;
            gap: 15px;
            align-items: center;
        }

        input[type="range"] {
            flex: 1;
            height: 8px;
            border-radius: 5px;
            background: #d3d3d3;
            outline: none;
            -webkit-appearance: none;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        input[type="range"]::-moz-range-thumb {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
            border: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        .preset-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }

        button {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            color: white;
        }

        .btn-center {
            background: #667eea;
        }

        .btn-min {
            background: #28a745;
        }

        .btn-max {
            background: #dc3545;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        button:active {
            transform: translateY(0);
        }

        .emergency-stop {
            margin-top: 30px;
            padding: 20px;
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.3em;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
        }

        .emergency-stop:hover {
            background: #c82333;
        }

        .range-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.9em;
            color: #6c757d;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 SO-101 Robot Control</h1>
        <p class="subtitle">Follower Arm Web Interface</p>

        <div id="status" class="status connected">
            ✅ Connected
        </div>

        <!-- Shoulder Pan -->
        <div class="motor-control">
            <div class="motor-header">
                <div class="motor-name">Shoulder Pan</div>
                <div class="motor-value" id="shoulder_pan_value">0</div>
            </div>
            <div class="slider-container">
                <input type="range" id="shoulder_pan" min="-100" max="100" value="0" step="1">
            </div>
            <div class="range-labels">
                <span>-100</span>
                <span>0</span>
                <span>100</span>
            </div>
            <div class="preset-buttons">
                <button class="btn-min" onclick="setMotor('shoulder_pan', -100)">Min</button>
                <button class="btn-center" onclick="setMotor('shoulder_pan', 0)">Center</button>
                <button class="btn-max" onclick="setMotor('shoulder_pan', 100)">Max</button>
            </div>
        </div>

        <!-- Shoulder Lift -->
        <div class="motor-control">
            <div class="motor-header">
                <div class="motor-name">Shoulder Lift</div>
                <div class="motor-value" id="shoulder_lift_value">0</div>
            </div>
            <div class="slider-container">
                <input type="range" id="shoulder_lift" min="-100" max="100" value="0" step="1">
            </div>
            <div class="range-labels">
                <span>-100</span>
                <span>0</span>
                <span>100</span>
            </div>
            <div class="preset-buttons">
                <button class="btn-min" onclick="setMotor('shoulder_lift', -100)">Min</button>
                <button class="btn-center" onclick="setMotor('shoulder_lift', 0)">Center</button>
                <button class="btn-max" onclick="setMotor('shoulder_lift', 100)">Max</button>
            </div>
        </div>

        <!-- Elbow Flex -->
        <div class="motor-control">
            <div class="motor-header">
                <div class="motor-name">Elbow Flex</div>
                <div class="motor-value" id="elbow_flex_value">0</div>
            </div>
            <div class="slider-container">
                <input type="range" id="elbow_flex" min="-100" max="100" value="0" step="1">
            </div>
            <div class="range-labels">
                <span>-100</span>
                <span>0</span>
                <span>100</span>
            </div>
            <div class="preset-buttons">
                <button class="btn-min" onclick="setMotor('elbow_flex', -100)">Min</button>
                <button class="btn-center" onclick="setMotor('elbow_flex', 0)">Center</button>
                <button class="btn-max" onclick="setMotor('elbow_flex', 100)">Max</button>
            </div>
        </div>

        <!-- Wrist Flex -->
        <div class="motor-control">
            <div class="motor-header">
                <div class="motor-name">Wrist Flex</div>
                <div class="motor-value" id="wrist_flex_value">0</div>
            </div>
            <div class="slider-container">
                <input type="range" id="wrist_flex" min="-100" max="100" value="0" step="1">
            </div>
            <div class="range-labels">
                <span>-100</span>
                <span>0</span>
                <span>100</span>
            </div>
            <div class="preset-buttons">
                <button class="btn-min" onclick="setMotor('wrist_flex', -100)">Min</button>
                <button class="btn-center" onclick="setMotor('wrist_flex', 0)">Center</button>
                <button class="btn-max" onclick="setMotor('wrist_flex', 100)">Max</button>
            </div>
        </div>

        <!-- Wrist Roll -->
        <div class="motor-control">
            <div class="motor-header">
                <div class="motor-name">Wrist Roll</div>
                <div class="motor-value" id="wrist_roll_value">0</div>
            </div>
            <div class="slider-container">
                <input type="range" id="wrist_roll" min="-100" max="100" value="0" step="1">
            </div>
            <div class="range-labels">
                <span>-100</span>
                <span>0</span>
                <span>100</span>
            </div>
            <div class="preset-buttons">
                <button class="btn-min" onclick="setMotor('wrist_roll', -100)">Min</button>
                <button class="btn-center" onclick="setMotor('wrist_roll', 0)">Center</button>
                <button class="btn-max" onclick="setMotor('wrist_roll', 100)">Max</button>
            </div>
        </div>

        <!-- Gripper -->
        <div class="motor-control">
            <div class="motor-header">
                <div class="motor-name">Gripper</div>
                <div class="motor-value" id="gripper_value">50</div>
            </div>
            <div class="slider-container">
                <input type="range" id="gripper" min="0" max="100" value="50" step="1">
            </div>
            <div class="range-labels">
                <span>0 (Open)</span>
                <span>50</span>
                <span>100 (Closed)</span>
            </div>
            <div class="preset-buttons">
                <button class="btn-min" onclick="setMotor('gripper', 0)">Open</button>
                <button class="btn-center" onclick="setMotor('gripper', 50)">Half</button>
                <button class="btn-max" onclick="setMotor('gripper', 100)">Close</button>
            </div>
        </div>

        <button class="emergency-stop" onclick="emergencyStop()">
            🛑 RETURN TO CENTER POSITION
        </button>
    </div>

    <script>
        // Update motor value displays when sliders move
        const motors = ['shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper'];

        motors.forEach(motor => {
            const slider = document.getElementById(motor);
            const valueDisplay = document.getElementById(motor + '_value');

            slider.addEventListener('input', function() {
                valueDisplay.textContent = this.value;
            });

            slider.addEventListener('change', function() {
                updateMotor(motor, parseFloat(this.value));
            });
        });

        function setMotor(motor, value) {
            const slider = document.getElementById(motor);
            const valueDisplay = document.getElementById(motor + '_value');
            slider.value = value;
            valueDisplay.textContent = value;
            updateMotor(motor, value);
        }

        function updateMotor(motor, position) {
            fetch('/api/motor', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    motor: motor,
                    position: position
                })
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error('Error:', data.error);
                    alert('Error controlling motor: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }

        function emergencyStop() {
            fetch('/api/center', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reset all sliders to center
                    motors.forEach(motor => {
                        const slider = document.getElementById(motor);
                        const valueDisplay = document.getElementById(motor + '_value');
                        if (motor === 'gripper') {
                            slider.value = 50;
                            valueDisplay.textContent = '50';
                        } else {
                            slider.value = 0;
                            valueDisplay.textContent = '0';
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }

        // Poll current positions every 500ms
        setInterval(() => {
            fetch('/api/positions')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Object.keys(data.positions).forEach(motor => {
                            const valueDisplay = document.getElementById(motor + '_value');
                            if (valueDisplay) {
                                valueDisplay.textContent = Math.round(data.positions[motor]);
                            }
                        });
                    }
                })
                .catch(error => {
                    console.error('Error fetching positions:', error);
                });
        }, 500);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve the main control interface."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/motor', methods=['POST'])
def control_motor():
    """
    API endpoint to control a single motor.

    Expected JSON payload:
    {
        "motor": "shoulder_pan",
        "position": -50.0
    }
    """
    try:
        data = request.json
        motor_name = data.get('motor')
        position = float(data.get('position'))

        if motor_name not in current_positions:
            return jsonify({'success': False, 'error': f'Invalid motor: {motor_name}'}), 400

        # Update current position
        with robot_lock:
            current_positions[motor_name] = position

            # Send command to robot
            if robot and robot.is_connected:
                action = {f"{motor_name}.pos": position}
                robot.send_action(action)
                logger.info(f"Motor {motor_name} set to {position}")
            else:
                logger.warning("Robot not connected, storing position only")

        return jsonify({'success': True, 'motor': motor_name, 'position': position})

    except Exception as e:
        logger.error(f"Error controlling motor: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/center', methods=['POST'])
def center_all():
    """Return all motors to center position."""
    try:
        with robot_lock:
            # Set all motors to center
            for motor in current_positions:
                if motor == 'gripper':
                    current_positions[motor] = 50.0
                else:
                    current_positions[motor] = 0.0

            # Send command to robot
            if robot and robot.is_connected:
                action = {
                    "shoulder_pan.pos": 0.0,
                    "shoulder_lift.pos": 0.0,
                    "elbow_flex.pos": 0.0,
                    "wrist_flex.pos": 0.0,
                    "wrist_roll.pos": 0.0,
                    "gripper.pos": 50.0
                }
                robot.send_action(action)
                logger.info("All motors centered")
            else:
                logger.warning("Robot not connected, storing positions only")

        return jsonify({'success': True, 'message': 'All motors centered'})

    except Exception as e:
        logger.error(f"Error centering motors: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get current positions of all motors."""
    try:
        with robot_lock:
            if robot and robot.is_connected:
                # Read actual positions from robot
                obs = robot.get_observation()
                positions = {}
                for motor in current_positions.keys():
                    key = f"{motor}.pos"
                    if key in obs:
                        positions[motor] = obs[key]
                        current_positions[motor] = obs[key]
                    else:
                        positions[motor] = current_positions[motor]
            else:
                positions = current_positions.copy()

        return jsonify({'success': True, 'positions': positions})

    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def initialize_robot():
    """Initialize the SO-101 follower robot."""
    global robot

    try:
        logger.info("Initializing SO-101 Follower arm...")
        logger.info(f"Port: {FOLLOWER_PORT}")

        config = SO101FollowerConfig(
            port=FOLLOWER_PORT,
            id=None,  # Use None to match calibration file name
            use_degrees=False  # Using normalized -100 to 100 range
        )

        robot = SO101Follower(config)

        logger.info("Connecting to follower arm...")
        robot.connect(calibrate=True)

        if robot.is_connected:
            logger.info("✅ SO-101 Follower connected successfully!")

            # Move to center position
            center_action = {
                "shoulder_pan.pos": 0.0,
                "shoulder_lift.pos": 0.0,
                "elbow_flex.pos": 0.0,
                "wrist_flex.pos": 0.0,
                "wrist_roll.pos": 0.0,
                "gripper.pos": 50.0
            }
            robot.send_action(center_action)
            logger.info("Robot moved to center position")
        else:
            logger.error("Failed to connect to robot!")
            robot = None

    except Exception as e:
        logger.error(f"Error initializing robot: {e}")
        robot = None


def cleanup():
    """Cleanup robot connection."""
    global robot
    if robot and robot.is_connected:
        logger.info("Disconnecting robot...")
        robot.disconnect()
        logger.info("Robot disconnected")


if __name__ == '__main__':
    try:
        # Initialize robot in main thread
        initialize_robot()

        # Start web server
        logger.info("\n" + "="*60)
        logger.info("🌐 SO-101 Web Server Starting!")
        logger.info("="*60)
        logger.info("Access the control panel at:")
        logger.info("  Local:   http://localhost:5000")
        logger.info("  Network: http://<your-ip>:5000")
        logger.info("="*60 + "\n")

        # Run Flask app
        # host='0.0.0.0' allows access from other devices on the network
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

    except KeyboardInterrupt:
        logger.info("\n\n🛑 Shutting down...")

    finally:
        cleanup()
