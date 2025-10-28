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
import argparse

from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

# Logger (level will be set based on command-line args)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Robot configuration
FOLLOWER_PORT_LINUX = "/dev/ttyACM0"  # Linux/Raspberry Pi
FOLLOWER_PORT_MAC = "/dev/tty.usbmodem5A7A0562271"  # macOS
FOLLOWER_PORT = FOLLOWER_PORT_LINUX  # Default to Linux

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
    <title>CEDARBOT SO-101</title>
    <meta name="viewport" content="width=800, initial-scale=1.0, user-scalable=no">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-touch-callout: none;
            -webkit-user-select: none;
            user-select: none;
        }

        @keyframes flicker {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.97; }
        }

        body {
            font-family: 'Courier New', monospace;
            background: #000;
            color: #0f0;
            overflow: hidden;
            width: 800px;
            height: 480px;
            position: relative;
            text-shadow: 0 0 5px #0f0;
        }

        /* CRT Scanlines */
        body::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 0, 0, 0.15),
                rgba(0, 0, 0, 0.15) 1px,
                transparent 1px,
                transparent 2px
            );
            pointer-events: none;
            z-index: 1000;
            animation: flicker 0.15s infinite;
        }

        /* CRT Glow */
        body::after {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(ellipse at center, transparent 0%, rgba(0,0,0,0.3) 100%);
            pointer-events: none;
            z-index: 999;
        }

        .container {
            width: 800px;
            height: 480px;
            padding: 15px;
            display: grid;
            grid-template-rows: auto 1fr auto;
            gap: 10px;
        }

        .header {
            text-align: center;
            border: 2px solid #0f0;
            padding: 8px;
            background: rgba(0, 255, 0, 0.05);
        }

        .header h1 {
            font-size: 20px;
            letter-spacing: 4px;
            margin-bottom: 3px;
        }

        .status {
            font-size: 11px;
            letter-spacing: 2px;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 180px 180px 1fr 120px;
            gap: 10px;
        }

        .control-section {
            border: 2px solid #0f0;
            padding: 8px;
            background: rgba(0, 255, 0, 0.02);
            display: flex;
            flex-direction: column;
        }

        .section-title {
            font-size: 10px;
            letter-spacing: 2px;
            margin-bottom: 8px;
            text-align: center;
            border-bottom: 1px solid #0f0;
            padding-bottom: 4px;
        }

        /* XY Pad Controller */
        .xy-pad {
            width: 160px;
            height: 160px;
            border: 2px solid #0f0;
            position: relative;
            background: rgba(0, 255, 0, 0.05);
            margin: auto;
            cursor: crosshair;
        }

        .xy-pad::before {
            content: "";
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: rgba(0, 255, 0, 0.3);
        }

        .xy-pad::after {
            content: "";
            position: absolute;
            left: 50%;
            top: 0;
            bottom: 0;
            width: 1px;
            background: rgba(0, 255, 0, 0.3);
        }

        .xy-cursor {
            position: absolute;
            width: 16px;
            height: 16px;
            border: 2px solid #0f0;
            border-radius: 50%;
            background: rgba(0, 255, 0, 0.3);
            transform: translate(-50%, -50%);
            box-shadow: 0 0 10px #0f0;
            pointer-events: none;
        }

        .xy-labels {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 5px;
            margin-top: 5px;
            font-size: 10px;
        }

        .xy-label {
            text-align: center;
            padding: 3px;
            border: 1px solid #0f0;
            background: rgba(0, 255, 0, 0.05);
        }

        /* Vertical Gripper Slider */
        .gripper-slider-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            flex: 1;
        }

        .gripper-slider-track {
            width: 30px;
            height: 180px;
            background: rgba(0, 255, 0, 0.1);
            border: 2px solid #0f0;
            position: relative;
            cursor: pointer;
        }

        .gripper-slider-fill {
            position: absolute;
            bottom: 0;
            width: 100%;
            background: rgba(0, 255, 0, 0.3);
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            transition: height 0.1s;
        }

        .gripper-slider-thumb {
            position: absolute;
            width: 100%;
            height: 6px;
            background: #0f0;
            box-shadow: 0 0 10px #0f0;
            transition: bottom 0.1s;
            pointer-events: none;
        }

        .gripper-value {
            text-align: center;
            font-size: 14px;
            padding: 4px;
            border: 1px solid #0f0;
            background: rgba(0, 255, 0, 0.05);
            min-width: 60px;
        }

        /* Vertical Sliders */
        .slider-group {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            flex: 1;
        }

        .slider-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
            flex: 1;
        }

        .slider-label {
            font-size: 10px;
            letter-spacing: 1px;
            text-align: center;
        }

        .slider-track {
            width: 30px;
            height: 180px;
            background: rgba(0, 255, 0, 0.1);
            border: 2px solid #0f0;
            position: relative;
            cursor: pointer;
        }

        .slider-fill {
            position: absolute;
            bottom: 0;
            width: 100%;
            background: rgba(0, 255, 0, 0.3);
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            transition: height 0.1s;
        }

        .slider-thumb {
            position: absolute;
            width: 100%;
            height: 6px;
            background: #0f0;
            box-shadow: 0 0 10px #0f0;
            transition: bottom 0.1s;
            pointer-events: none;
        }
        
        .slider-value {
            text-align: center;
            font-size: 14px;
            padding: 4px;
            border: 1px solid #0f0;
            background: rgba(0, 255, 0, 0.05);
            min-width: 60px;
        }

        /* Gripper Control */
        .gripper-buttons {
            display: flex;
            flex-direction: column;
            gap: 5px;
            width: 100%;
        }

        .btn {
            flex: 1;
            padding: 10px;
            border: 2px solid #0f0;
            background: rgba(0, 255, 0, 0.05);
            color: #0f0;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            cursor: pointer;
            letter-spacing: 1px;
            transition: all 0.1s;
        }

        .btn:active {
            background: rgba(0, 255, 0, 0.2);
            box-shadow: inset 0 0 10px #0f0;
        }

        .footer {
            display: flex;
            gap: 10px;
        }

        .emergency-btn {
            flex: 1;
            padding: 15px;
            border: 3px solid #0f0;
            background: rgba(0, 255, 0, 0.1);
            color: #0f0;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 3px;
            cursor: pointer;
            transition: all 0.1s;
        }

        .emergency-btn:active {
            background: rgba(0, 255, 0, 0.3);
            box-shadow: inset 0 0 20px #0f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SO-101 CONTROL SYSTEM</h1>
            <div class="status" id="status">[ SYSTEM ONLINE ]</div>
        </div>

        <div class="main-grid">
            <!-- Shoulder XY Control -->
            <div class="control-section">
                <div class="section-title">SHOULDER</div>
                <div class="xy-pad" id="shoulder-pad" data-x="shoulder_pan" data-y="shoulder_lift">
                    <div class="xy-cursor" id="shoulder-cursor"></div>
                </div>
                <div class="xy-labels">
                    <div class="xy-label">PAN: <span id="shoulder_pan_value">0</span></div>
                    <div class="xy-label">LIFT: <span id="shoulder_lift_value">0</span></div>
                </div>
            </div>

            <!-- Wrist XY Control -->
            <div class="control-section">
                <div class="section-title">WRIST</div>
                <div class="xy-pad" id="wrist-pad" data-x="wrist_roll" data-y="wrist_flex">
                    <div class="xy-cursor" id="wrist-cursor"></div>
                </div>
                <div class="xy-labels">
                    <div class="xy-label">ROLL: <span id="wrist_roll_value">0</span></div>
                    <div class="xy-label">FLEX: <span id="wrist_flex_value">0</span></div>
                </div>
            </div>

            <!-- Sliders Section -->
            <div class="control-section">
                <div class="section-title">ELBOW</div>
                <div class="slider-group">
                    <div class="slider-item">
                        <div class="slider-track" data-motor="elbow_flex">
                            <div class="slider-fill" id="elbow_flex_fill"></div>
                            <div class="slider-thumb" id="elbow_flex_thumb"></div>
                        </div>
                        <div class="slider-value" id="elbow_flex_value">0</div>
                    </div>
                </div>
            </div>

            <!-- Gripper -->
            <div class="control-section">
                <div class="section-title">GRIPPER</div>
                <div class="gripper-slider-container">
                    <div class="gripper-slider-track" id="gripper-track">
                        <div class="gripper-slider-fill" id="gripper-fill"></div>
                        <div class="gripper-slider-thumb" id="gripper-thumb"></div>
                    </div>
                    <div class="gripper-value" id="gripper_value">50</div>
                </div>
                <div class="gripper-buttons">
                    <button class="btn" onclick="setMotor('gripper', 100)">OPEN</button>
                    <button class="btn" onclick="setMotor('gripper', 0)">CLOSE</button>
                </div>
            </div>
        </div>

        <div class="footer">
            <button class="emergency-btn" onclick="emergencyStop()">[ RETURN TO CENTER ]</button>
        </div>
    </div>

    <script>
        // Motor positions
        const positions = {
            shoulder_pan: 0,
            shoulder_lift: 0,
            elbow_flex: 0,
            wrist_flex: 0,
            wrist_roll: 0,
            gripper: 50
        };

        // Rate limiting: 30Hz = 33.33ms between updates
        const UPDATE_INTERVAL = 33; // milliseconds
        const lastUpdateTime = {};
        const pendingUpdates = {};
        let updateTimer = null;

        // Initialize timestamps
        Object.keys(positions).forEach(motor => {
            lastUpdateTime[motor] = 0;
            pendingUpdates[motor] = null;
        });

        // Process pending updates at 30Hz
        function processPendingUpdates() {
            const now = Date.now();
            Object.keys(pendingUpdates).forEach(motor => {
                if (pendingUpdates[motor] !== null && (now - lastUpdateTime[motor]) >= UPDATE_INTERVAL) {
                    sendMotorCommand(motor, pendingUpdates[motor]);
                    lastUpdateTime[motor] = now;
                    pendingUpdates[motor] = null;
                }
            });
        }

        // Start the update timer
        setInterval(processPendingUpdates, UPDATE_INTERVAL);

        // XY Pad Controller
        class XYPad {
            constructor(padId, cursorId, motorX, motorY) {
                this.pad = document.getElementById(padId);
                this.cursor = document.getElementById(cursorId);
                this.motorX = motorX;
                this.motorY = motorY;
                this.isDragging = false;
                
                this.pad.addEventListener('mousedown', this.startDrag.bind(this));
                this.pad.addEventListener('touchstart', this.startDrag.bind(this));
                document.addEventListener('mousemove', this.drag.bind(this));
                document.addEventListener('touchmove', this.drag.bind(this));
                document.addEventListener('mouseup', this.endDrag.bind(this));
                document.addEventListener('touchend', this.endDrag.bind(this));
                
                this.updateCursor();
            }
            
            startDrag(e) {
                this.isDragging = true;
                this.updatePosition(e);
            }
            
            drag(e) {
                if (this.isDragging) {
                    this.updatePosition(e);
                }
            }
            
            endDrag() {
                this.isDragging = false;
            }
            
            updatePosition(e) {
                const rect = this.pad.getBoundingClientRect();
                const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
                const y = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top;
                
                const normX = Math.max(0, Math.min(1, x / rect.width));
                const normY = Math.max(0, Math.min(1, y / rect.height));
                
                let valueX = Math.round((normX * 200) - 100);
                let valueY = Math.round(((1 - normY) * 200) - 100);
                
                // Apply inversions based on motor
                if (this.motorY === 'shoulder_lift') {
                    valueY = -valueY;  // Invert shoulder up/down
                }
                if (this.motorX === 'wrist_roll') {
                    valueX = -valueX;  // Invert wrist roll
                }
                if (this.motorY === 'wrist_flex') {
                    valueY = -valueY;  // Invert wrist flex
                }
                
                positions[this.motorX] = valueX;
                positions[this.motorY] = valueY;
                
                this.updateCursor();
                scheduleMotorUpdate(this.motorX, valueX);
                scheduleMotorUpdate(this.motorY, valueY);
            }
            
            updateCursor() {
                // Get actual position values (which may be inverted)
                let dispX = positions[this.motorX];
                let dispY = positions[this.motorY];
                
                // Reverse the inversion for display positioning
                if (this.motorY === 'shoulder_lift') {
                    dispY = -dispY;
                }
                if (this.motorX === 'wrist_roll') {
                    dispX = -dispX;
                }
                if (this.motorY === 'wrist_flex') {
                    dispY = -dispY;
                }
                
                const x = ((dispX + 100) / 200) * 100;
                const y = ((100 - dispY) / 200) * 100;
                this.cursor.style.left = x + '%';
                this.cursor.style.top = y + '%';
                document.getElementById(this.motorX + '_value').textContent = positions[this.motorX];
                document.getElementById(this.motorY + '_value').textContent = positions[this.motorY];
            }
        }

        // Vertical Gripper Slider Controller
        class GripperSlider {
            constructor(trackId, fillId, thumbId) {
                this.track = document.getElementById(trackId);
                this.fill = document.getElementById(fillId);
                this.thumb = document.getElementById(thumbId);
                this.motor = 'gripper';
                this.isDragging = false;
                
                this.track.addEventListener('mousedown', this.startDrag.bind(this));
                this.track.addEventListener('touchstart', this.startDrag.bind(this));
                document.addEventListener('mousemove', this.drag.bind(this));
                document.addEventListener('touchmove', this.drag.bind(this));
                document.addEventListener('mouseup', this.endDrag.bind(this));
                document.addEventListener('touchend', this.endDrag.bind(this));
                
                this.updateSlider();
            }
            
            startDrag(e) {
                this.isDragging = true;
                this.updatePosition(e);
            }
            
            drag(e) {
                if (this.isDragging) {
                    this.updatePosition(e);
                }
            }
            
            endDrag() {
                this.isDragging = false;
            }
            
            updatePosition(e) {
                const rect = this.track.getBoundingClientRect();
                const y = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top;
                const norm = Math.max(0, Math.min(1, y / rect.height));
                // Top = 100 (open), bottom = 0 (close) - FLIPPED
                const value = Math.round((1 - norm) * 100);
                
                positions[this.motor] = value;
                this.updateSlider();
                scheduleMotorUpdate(this.motor, value);
            }
            
            updateSlider() {
                const percent = positions[this.motor];
                this.fill.style.height = percent + '%';
                this.thumb.style.bottom = percent + '%';
                document.getElementById(this.motor + '_value').textContent = positions[this.motor];
            }
        }

        // Vertical Slider Controller (for -100 to 100 range)
        class Slider {
            constructor(motor) {
                this.motor = motor;
                this.track = document.querySelector(`[data-motor="${motor}"]`);
                this.fill = document.getElementById(`${motor}_fill`);
                this.thumb = document.getElementById(`${motor}_thumb`);
                this.isDragging = false;
                
                this.track.addEventListener('mousedown', this.startDrag.bind(this));
                this.track.addEventListener('touchstart', this.startDrag.bind(this));
                document.addEventListener('mousemove', this.drag.bind(this));
                document.addEventListener('touchmove', this.drag.bind(this));
                document.addEventListener('mouseup', this.endDrag.bind(this));
                document.addEventListener('touchend', this.endDrag.bind(this));
                
                this.updateSlider();
            }
            
            startDrag(e) {
                this.isDragging = true;
                this.updatePosition(e);
            }
            
            drag(e) {
                if (this.isDragging) {
                    this.updatePosition(e);
                }
            }
            
            endDrag() {
                this.isDragging = false;
            }
            
            updatePosition(e) {
                const rect = this.track.getBoundingClientRect();
                const y = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top;
                const norm = Math.max(0, Math.min(1, y / rect.height));
                // Top = -100, Bottom = 100 (FLIPPED)
                const value = Math.round((norm * 200) - 100);
                
                positions[this.motor] = value;
                this.updateSlider();
                scheduleMotorUpdate(this.motor, value);
            }
            
            updateSlider() {
                // Convert -100 to 100 range to 0-100 percent for display
                const percent = ((positions[this.motor] + 100) / 200) * 100;
                // Thumb position: inverted so it follows finger (top = 100% from bottom, bottom = 0% from bottom)
                const thumbPosition = 100 - percent;
                this.thumb.style.bottom = thumbPosition + '%';
                // Fill grows from bottom up to the thumb
                this.fill.style.height = thumbPosition + '%';
                document.getElementById(this.motor + '_value').textContent = positions[this.motor];
            }
        }

        // Initialize controllers
        const shoulderPad = new XYPad('shoulder-pad', 'shoulder-cursor', 'shoulder_pan', 'shoulder_lift');
        const wristPad = new XYPad('wrist-pad', 'wrist-cursor', 'wrist_roll', 'wrist_flex');
        const gripperSlider = new GripperSlider('gripper-track', 'gripper-fill', 'gripper-thumb');
        const elbowSlider = new Slider('elbow_flex');

        function setMotor(motor, value) {
            positions[motor] = value;
            
            if (motor === 'gripper') {
                gripperSlider.updateSlider();
            }
            
            scheduleMotorUpdate(motor, value);
        }

        // Schedule a motor update (will be rate-limited to 30Hz)
        function scheduleMotorUpdate(motor, position) {
            pendingUpdates[motor] = position;
        }

        // Actually send the motor command to the server
        function sendMotorCommand(motor, position) {
            fetch('/api/motor', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({motor: motor, position: position})
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error('Error:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        }

        function emergencyStop() {
            fetch('/api/center', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    positions.shoulder_pan = 0;
                    positions.shoulder_lift = 0;
                    positions.elbow_flex = 0;
                    positions.wrist_flex = 0;
                    positions.wrist_roll = 0;
                    positions.gripper = 50;
                    
                    shoulderPad.updateCursor();
                    wristPad.updateCursor();
                    elbowSlider.updateSlider();
                    gripperSlider.updateSlider();
                }
            })
            .catch(error => console.error('Error:', error));
        }

        // Poll positions
        setInterval(() => {
            fetch('/api/positions')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Object.keys(data.positions).forEach(motor => {
                            positions[motor] = Math.round(data.positions[motor]);
                        });
                        shoulderPad.updateCursor();
                        wristPad.updateCursor();
                        elbowSlider.updateSlider();
                        gripperSlider.updateSlider();
                    }
                })
                .catch(error => console.error('Error:', error));
        }, 2000);
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

            # Send command to robot - use send_action() like teleop does
            if robot and robot.is_connected:
                action = {f"{motor_name}.pos": position}
                logger.debug(f"Sending action: {action}")
                robot.send_action(action)
                
                # Check motor status after sending command (only in verbose mode)
                if logger.isEnabledFor(logging.DEBUG):
                    time.sleep(0.05)  # 50ms delay to let motor start moving
                    try:
                        status = robot.bus.read("Status", motor_name, normalize=False)
                        moving = robot.bus.read("Moving", motor_name, normalize=False)
                        goal_pos_actual = robot.bus.read("Goal_Position", motor_name, normalize=False)
                        goal_vel_actual = robot.bus.read("Goal_Velocity", motor_name, normalize=False)
                        present_pos = robot.bus.read("Present_Position", motor_name, normalize=False)
                        lock = robot.bus.read("Lock", motor_name, normalize=False)
                        logger.debug(f"Motor {motor_name} | Target={position} | GoalPos={goal_pos_actual} | PresentPos={present_pos} | GoalVel={goal_vel_actual} | Lock={lock} | Status={status:#04x} | Moving={moving}")
                    except Exception as e:
                        logger.warning(f"Could not read motor status: {e}")
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
                logger.debug("All motors centered")
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


def initialize_robot(port=None):
    """Initialize the SO-101 follower robot."""
    global robot
    
    robot_port = port if port is not None else FOLLOWER_PORT

    try:
        logger.info("Initializing SO-101 Follower arm...")
        logger.info(f"Port: {robot_port}")

        config = SO101FollowerConfig(
            port=robot_port,
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
        import traceback
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        robot = None


def cleanup():
    """Cleanup robot connection."""
    global robot
    if robot and robot.is_connected:
        logger.info("Disconnecting robot...")
        robot.disconnect()
        logger.info("Robot disconnected")


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='SO-101 Web Control Server')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose debug logging')
    parser.add_argument('--port', '-p', type=int, default=5001,
                        help='Port to run the web server on (default: 5001)')
    parser.add_argument('--mac', action='store_true',
                        help=f'Use macOS port ({FOLLOWER_PORT_MAC}) instead of Linux port ({FOLLOWER_PORT_LINUX})')
    parser.add_argument('--robot-port', type=str, default=None,
                        help='Serial port for the robot (overrides --mac flag)')
    args = parser.parse_args()
    
    # Determine which port to use
    if args.robot_port:
        robot_port = args.robot_port
    elif args.mac:
        robot_port = FOLLOWER_PORT_MAC
    else:
        robot_port = FOLLOWER_PORT_LINUX

    # Configure logging based on verbose flag
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if args.verbose else '%(message)s'
    )
    
    # Suppress Flask's default logging unless verbose
    if not args.verbose:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    try:
        # Initialize robot in main thread
        initialize_robot(port=robot_port)

        # Start web server
        print("\n" + "="*60)
        print("🌐 CEDARBOT SO-101 Web Server Starting!")
        print("="*60)
        print("Access the control panel at:")
        print(f"  Local:   http://localhost:{args.port}")
        print(f"  Network: http://<your-ip>:{args.port}")
        if args.verbose:
            print("  Debug:   VERBOSE MODE ENABLED")
        print("="*60 + "\n")

        # Run Flask app
        # host='0.0.0.0' allows access from other devices on the network
        app.run(host='0.0.0.0', port=args.port, debug=False, threaded=True)

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")

    finally:
        cleanup()
