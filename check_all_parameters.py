#!/usr/bin/env python3
"""
Check all relevant motor parameters to identify what's preventing movement.
"""

from lerobot.robots.so101_follower import SO101Follower
from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig

PORT = "/dev/tty.usbmodem5A7A0562271"

def check_all_parameters():
    print("=" * 70)
    print("Comprehensive Motor Parameter Check")
    print("=" * 70)
    
    config = SO101FollowerConfig(port=PORT)
    robot = SO101Follower(config)
    robot.connect(calibrate=False)
    
    motor = "gripper"
    
    # All relevant parameters from the control table
    parameters = [
        "Lock",
        "Torque_Enable",
        "Torque_Limit",
        "Max_Torque_Limit",
        "Protection_Current",
        "Protective_Torque",
        "Protection_Time",
        "Overload_Torque",
        "Over_Current_Protection_Time",
        "Min_Position_Limit",
        "Max_Position_Limit",
        "Present_Position",
        "Goal_Position",
        "Present_Current",
        "Present_Voltage",
        "Present_Temperature",
        "Present_Load",
        "Status",
        "Moving",
        "Operating_Mode",
        "Unloading_Condition",
        "Acceleration",
        "Goal_Velocity",
        "P_Coefficient",
        "D_Coefficient",
        "I_Coefficient",
    ]
    
    print(f"\nParameter values for {motor}:")
    print("-" * 70)
    
    values = {}
    for param in parameters:
        try:
            value = robot.bus.read(param, motor, normalize=False)
            values[param] = value
            print(f"{param:30s}: {value}")
        except Exception as e:
            print(f"{param:30s}: ERROR - {e}")
    
    print("\n" + "=" * 70)
    print("Analysis:")
    print("=" * 70)
    
    # Analyze the values
    issues = []
    
    if values.get("Lock", 1) == 1:
        issues.append("⚠️  Lock is set to 1 (motor is locked)")
    else:
        print("✅ Lock = 0 (motor is unlocked)")
    
    if values.get("Torque_Enable", 0) == 0:
        issues.append("⚠️  Torque_Enable is 0 (torque disabled)")
    else:
        print("✅ Torque_Enable = 1 (torque enabled)")
    
    torque_limit = values.get("Torque_Limit", 0)
    if torque_limit == 0:
        issues.append(f"❌ Torque_Limit is 0 (motor cannot produce any torque!)")
    else:
        print(f"✅ Torque_Limit = {torque_limit}")
    
    max_torque = values.get("Max_Torque_Limit", 0)
    if max_torque == 0:
        issues.append(f"❌ Max_Torque_Limit is 0 (motor cannot produce any torque!)")
    else:
        print(f"✅ Max_Torque_Limit = {max_torque}")
    
    if values.get("Present_Current", -1) == 0:
        issues.append("⚠️  Present_Current is 0 (no power to motor windings)")
    
    if values.get("Status", 0) != 0:
        issues.append(f"⚠️  Status register shows error: {values.get('Status', 0)}")
    
    print(f"\nVoltage: {values.get('Present_Voltage', 0)/10:.1f}V")
    print(f"Temperature: {values.get('Present_Temperature', 0)}°C")
    
    if issues:
        print("\n" + "=" * 70)
        print("ISSUES FOUND:")
        print("=" * 70)
        for issue in issues:
            print(issue)
    
    robot.disconnect()

if __name__ == "__main__":
    check_all_parameters()




