#!/bin/bash
# SEEs Unified Console
#
# Interactive console with automatic session logging and trigger capture
# All data automatically saved to timestamped session folders
#
# Usage: ./SEEs.sh [port]
#        Default port: /dev/ttyACM0

PORT="${1:-/dev/ttyACM0}"

# Just run the interactive Python script - it handles everything
exec python3 scripts/sees_interactive.py "$PORT"
