#!/bin/bash
# Quick test of native firmware simulation

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TESTS_DIR="$SCRIPT_DIR/../../tests"

echo "Testing SEEs Native Firmware Simulation"
echo "========================================"
echo ""

# Start data pump
echo "Starting data pump..."
cd "$TESTS_DIR"
python3 virtual_serial_port.py &
VPORT_PID=$!
sleep 2

if [ ! -e /tmp/tty_sees ]; then
    echo "❌ Failed to create virtual port"
    kill $VPORT_PID 2>/dev/null
    exit 1
fi
echo "✅ Virtual port ready: /tmp/tty_sees"

# Run native firmware for 3 seconds
echo ""
echo "Running native firmware (3 seconds)..."
cd "$SCRIPT_DIR"
timeout 3 ./sees_native /tmp/tty_sees 2>&1 | head -50

# Cleanup
kill $VPORT_PID 2>/dev/null || true
rm -f /tmp/tty_sees

echo ""
echo "✅ Test complete"
