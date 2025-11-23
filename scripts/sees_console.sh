#!/bin/bash
# SEEs Console with Automatic Logging (Session-based)
#
# Alternative console using screen for raw serial access
# Use with sees_interactive.py for full features (recommended)
#
# Usage: ./sees_console.sh [port]
#        Default port: /dev/ttyACM0

PORT="${1:-/dev/ttyACM0}"
BASE_DIR="$HOME/Aeris/data/sees"
SESSION_TIMESTAMP=$(date +%Y%m%d.%H%M)
SESSION_DIR="$BASE_DIR/$SESSION_TIMESTAMP"
LOGFILE="$SESSION_DIR/SEEs.$SESSION_TIMESTAMP.log"

# Create session directory if it doesn't exist
mkdir -p "$SESSION_DIR"

echo "═══════════════════════════════════════════════════"
echo "  SEEs Console with Automatic Logging"
echo "═══════════════════════════════════════════════════"
echo "  Port:         $PORT"
echo "  Session dir:  $SESSION_DIR"
echo "  Log file:     SEEs.$SESSION_TIMESTAMP.log"
echo "═══════════════════════════════════════════════════"
echo ""
echo "⚠️  NOTE: This is basic screen logging only"
echo "    For trigger capture, use: ./SEEs.sh"
echo ""
echo "Starting screen session with logging enabled..."
echo "To exit: Ctrl+A then K (kill window)"
echo ""

# Start screen with logging enabled
# -L: Turn on output logging
# -Logfile: Specify log file location
screen -L -Logfile "$LOGFILE" "$PORT" 115200
