#!/bin/bash
# SEEs Unified Console
#
# Interactive console with automatic session logging
# All data automatically saved to timestamped session folders
#
# Usage: ./SEEs.sh [port] [-v] [--sim]
#        Default port: /dev/ttyACM0
#        -v: Verbose mode (show all streaming data)
#        --sim: Simulation mode (run native binary)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Look for native binary: first in ~/Aeris/bin (GitHub download), then in repo
if [[ -x "$HOME/Aeris/bin/sees_native" ]]; then
    NATIVE_BIN="$HOME/Aeris/bin/sees_native"
else
    NATIVE_BIN="$SCRIPT_DIR/SEEsDriver/native/sees_native"
fi

# Parse arguments - find port and flags separately
PORT="/dev/ttyACM0"
VERBOSE=""
SIMULATION=""

for arg in "$@"; do
    if [[ "$arg" == "-v" || "$arg" == "--verbose" ]]; then
        VERBOSE="-v"
    elif [[ "$arg" == "--sim" || "$arg" == "--native" ]]; then
        SIMULATION="--native"
    elif [[ "$arg" != -* ]]; then
        PORT="$arg"
    fi
done

# Run the interactive Python script
if [[ -n "$SIMULATION" ]]; then
    if [[ ! -x "$NATIVE_BIN" ]]; then
        echo "Error: Native binary not found at $NATIVE_BIN"
        echo "Build it with: cd SEEsDriver/native && make"
        exit 1
    fi
    # SEEs native needs a data port for simulated ADC data
    DATA_PORT="/tmp/tty_sees"
    if [[ ! -e "$DATA_PORT" ]]; then
        echo "Error: Data port not found at $DATA_PORT"
        echo "Start the data pump: cd tests && python3 virtual_serial_port.py &"
        exit 1
    fi
    exec python3 scripts/sees_interactive.py --native "$NATIVE_BIN" --data "$DATA_PORT" $VERBOSE
else
    exec python3 scripts/sees_interactive.py "$PORT" $VERBOSE
fi
