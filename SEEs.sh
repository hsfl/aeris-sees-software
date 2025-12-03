#!/bin/bash
# SEEs Unified Console
#
# Interactive console with automatic session logging
# All data automatically saved to timestamped session folders
#
# Usage: ./SEEs.sh [port] [-v]
#        Default port: /dev/ttyACM0
#        -v: Verbose mode (show all streaming data)

# Parse arguments - find port and flags separately
PORT="/dev/ttyACM0"
VERBOSE=""

for arg in "$@"; do
    if [[ "$arg" == "-v" || "$arg" == "--verbose" ]]; then
        VERBOSE="-v"
    elif [[ "$arg" != -* ]]; then
        PORT="$arg"
    fi
done

# Just run the interactive Python script - it handles everything
exec python3 scripts/sees_interactive.py "$PORT" $VERBOSE
