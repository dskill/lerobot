#!/bin/bash

# Data collection script for deep research investigation
# See DEEP_RESEARCH_PROMPT.md for full context

echo "=============================================="
echo "SO-101 Investigation Data Collection"
echo "=============================================="
echo ""

# Activate venv
source venv/bin/activate

OUTPUT_DIR="research_data_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "📁 Creating output directory: $OUTPUT_DIR"
echo ""

# 1. Calibration files
echo "📋 Collecting calibration files..."
if [ -f "/Users/drew/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader/None.json" ]; then
    cp "/Users/drew/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader/None.json" \
       "$OUTPUT_DIR/leader_calibration.json"
    echo "  ✅ Leader calibration copied"
else
    echo "  ❌ Leader calibration not found"
fi

if [ -f "/Users/drew/.cache/huggingface/lerobot/calibration/robots/so101_follower/None.json" ]; then
    cp "/Users/drew/.cache/huggingface/lerobot/calibration/robots/so101_follower/None.json" \
       "$OUTPUT_DIR/follower_calibration.json"
    echo "  ✅ Follower calibration copied"
else
    echo "  ❌ Follower calibration not found"
fi
echo ""

# 2. Git history
echo "📜 Collecting git history..."
git log --oneline --all -- src/lerobot/motors/feetech/ > "$OUTPUT_DIR/git_history_feetech.txt"
git log --oneline --all -- src/lerobot/robots/so101_follower/ > "$OUTPUT_DIR/git_history_so101_follower.txt"
git log --oneline --all -- src/lerobot/teleoperators/so101_leader/ > "$OUTPUT_DIR/git_history_so101_leader.txt"
echo "  ✅ Git history saved"
echo ""

# 3. Code diff
echo "📝 Collecting code changes..."
git diff src/lerobot/motors/feetech/feetech.py > "$OUTPUT_DIR/lock_parameter_fix.diff"
echo "  ✅ Code diff saved"
echo ""

# 4. USB device info
echo "🔌 Collecting USB device info..."
ls -la /dev/tty.usb* > "$OUTPUT_DIR/usb_devices.txt" 2>&1
echo "  ✅ USB devices listed"
echo ""

# 5. Python environment
echo "🐍 Collecting Python environment info..."
python3 --version > "$OUTPUT_DIR/python_version.txt"
pip list > "$OUTPUT_DIR/pip_packages.txt"
echo "  ✅ Python environment info saved"
echo ""

# 6. System info
echo "💻 Collecting system info..."
uname -a > "$OUTPUT_DIR/system_info.txt"
echo "  ✅ System info saved"
echo ""

# 7. Test scripts results (if they exist)
echo "🧪 Collecting test results..."
if [ -f "verify_lock_fix.py" ]; then
    echo "Running verify_lock_fix.py..."
    python3 verify_lock_fix.py > "$OUTPUT_DIR/verify_lock_fix_output.txt" 2>&1 || true
    echo "  ✅ Lock fix verification saved"
fi
echo ""

# 8. Create summary
cat > "$OUTPUT_DIR/README.md" << 'EOF'
# SO-101 Investigation Data Collection

## Files in this directory:

- `leader_calibration.json` - SO-101 leader arm calibration data
- `follower_calibration.json` - SO-101 follower arm calibration data
- `git_history_*.txt` - Git commit history for relevant files
- `lock_parameter_fix.diff` - The Lock parameter change we made
- `usb_devices.txt` - USB serial devices detected
- `python_version.txt` - Python version info
- `pip_packages.txt` - Installed Python packages
- `system_info.txt` - macOS system information
- `verify_lock_fix_output.txt` - Results of Lock parameter verification

## Context

This data was collected as part of investigating why SO-101 follower arm
motors don't move despite:
- Lock=0, Torque=1 being set correctly
- Goal_Position writes succeeding
- No software errors
- Leader arm working perfectly

See `DEEP_RESEARCH_PROMPT.md` in parent directory for full investigation plan.

## Ports

- Leader: /dev/tty.usbmodem5A7A0574331
- Follower: /dev/tty.usbmodem5A7A0562271
EOF

echo "=============================================="
echo "✅ Data collection complete!"
echo "=============================================="
echo ""
echo "All data saved to: $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "1. Review the collected data"
echo "2. Consult DEEP_RESEARCH_PROMPT.md"
echo "3. Run specific tests based on findings"
echo ""

