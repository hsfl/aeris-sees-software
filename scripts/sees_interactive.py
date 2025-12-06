#!/usr/bin/env python3
"""
SEEs Interactive Console - Body Cam Mode

The Teensy is ALWAYS streaming data (body cam mode).
The Teensy maintains the circular buffer and saves snaps to its SD card.
This console just logs the stream to the computer and forwards commands.

Commands:
- snap - Tell Teensy to save ±2.5s window to SD card

Directory structure:
~/Aeris/data/sees/YYYYMMDD.HHMM/
├── SEEs.YYYYMMDD.HHMM.log          (full session log - raw serial)
├── SEEs.YYYYMMDD.HHMM.stream.csv   (full streaming data - parsed CSV)
└── ...

Snaps are saved on Teensy SD card: snaps/snap_NNNNN_TTTTTTTTTT.csv

Usage:
    python3 sees_interactive.py /dev/ttyACM0
    python3 sees_interactive.py /dev/ttyACM0 -v    # Verbose mode

Controls:
    snap   - Capture ±2.5s window (saved to Teensy SD card)
    Ctrl+C - Exit
"""

import serial
import sys
import select
import termios
import tty
import argparse
from datetime import datetime
from pathlib import Path
import time

# Configuration
BAUD_RATE = 115200


def create_session_directory():
    """Create timestamped session directory"""
    base_dir = Path.home() / "Aeris" / "data" / "sees"
    session_timestamp = datetime.now().strftime("%Y%m%d.%H%M")
    session_dir = base_dir / session_timestamp
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir, session_timestamp


def generate_log_filename(session_timestamp):
    """Generate session log filename"""
    return f"SEEs.{session_timestamp}.log"


def generate_stream_filename(session_timestamp):
    """Generate streaming CSV filename"""
    return f"SEEs.{session_timestamp}.stream.csv"


def parse_data_line(line):
    """
    Parse CSV data line: time_ms,voltage_V,hit,total_hits
    Returns parsed line or None if not valid data
    """
    line = line.strip()

    # Skip empty lines
    if not line:
        return None

    # Skip obvious non-data lines (status messages, headers)
    if line.startswith('[SEEs]') or line.startswith('SEEs>') or 'voltage_V' in line:
        return None

    # Skip lines that start with non-numeric characters
    if line[0].isalpha() or line[0] in '═─✅📸📊⏸':
        return None

    # Validate CSV format: time_ms,voltage_V,hit,total_hits
    parts = line.split(',')
    if len(parts) == 4:
        try:
            float(parts[0])  # time_ms
            float(parts[1])  # voltage_V
            int(parts[2])    # hit
            int(parts[3])    # total_hits
            return line
        except ValueError:
            return None

    return None


def is_data_like(line):
    """
    Check if a line looks like it might be data (numeric with commas).
    Used to suppress partial/malformed data lines in non-verbose mode.
    """
    line = line.strip()
    if not line:
        return False

    # If it starts with a digit or minus sign and contains commas, it's probably data
    if (line[0].isdigit() or line[0] == '-') and ',' in line:
        return True

    # Check if it contains comma-separated numbers (data with echo prefix)
    if ',' in line:
        parts = line.split(',')
        if len(parts) >= 3:
            try:
                float(parts[-3].lstrip('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))
                float(parts[-2])
                float(parts[-1])
                return True
            except (ValueError, IndexError):
                pass

    return False


def interactive_console(port, verbose=False):
    """Interactive console - logs stream and forwards commands to Teensy"""

    # Create session directory
    session_dir, session_timestamp = create_session_directory()
    log_filename = generate_log_filename(session_timestamp)
    stream_filename = generate_stream_filename(session_timestamp)
    log_file_path = session_dir / log_filename
    stream_file_path = session_dir / stream_filename

    print("═══════════════════════════════════════════════════")
    print("  SEEs Interactive Console - Body Cam Mode")
    print("═══════════════════════════════════════════════════")
    print(f"  Port:         {port}")
    print(f"  Session dir:  {session_dir}")
    print(f"  Log file:     {log_filename}")
    print(f"  Stream file:  {stream_filename}")
    print(f"  Verbose:      {'ON' if verbose else 'OFF'}")
    print("═══════════════════════════════════════════════════")
    print()
    print("Command: snap (saves ±2.5s to Teensy SD card)")
    print("Ctrl+C to exit")
    if not verbose:
        print("Use -v flag for full streaming data output")
    print()

    # Open serial port
    ser = serial.Serial(port, BAUD_RATE, timeout=0.1)

    # Wait for connection to stabilize and flush any initial garbage
    time.sleep(0.1)
    ser.reset_input_buffer()

    # Open log files
    log_file = open(log_file_path, 'w', buffering=1)
    stream_file = open(stream_file_path, 'w', buffering=1)
    stream_file.write("time_ms,voltage_V,hit,total_hits\n")

    # State tracking
    snap_count = 0
    data_streaming = False
    last_data_time = 0
    data_count = 0

    # Snap capture state
    capturing_snap = False
    snap_data = []

    # Line buffer for processing complete lines
    line_buffer = ""

    # Input buffer for tracking what user is typing
    input_buffer = ""

    # Save terminal settings
    old_settings = termios.tcgetattr(sys.stdin)

    try:
        # Set terminal to raw mode for character-by-character input
        tty.setraw(sys.stdin.fileno())

        # Show initial prompt
        sys.stdout.write("SEEs> ")
        sys.stdout.flush()

        while True:
            current_time = time.time()

            # Check if data streaming has stopped (no data for 0.5s)
            if data_streaming and (current_time - last_data_time) > 0.5:
                data_streaming = False
                if not verbose:
                    sys.stdout.write(f"\r\033[K")
                    sys.stdout.write(f"SEEs> {input_buffer}")
                    sys.stdout.flush()

            # Check for user keyboard input
            if select.select([sys.stdin], [], [], 0)[0]:
                char = sys.stdin.read(1)

                # Ctrl+C to exit
                if ord(char) == 3:
                    break

                # Send to serial port (Teensy will process commands)
                ser.write(char.encode())

                # Track input buffer (for redrawing prompt later)
                if char == '\r':
                    if not data_streaming:
                        sys.stdout.write('\n')
                    input_buffer = ""
                elif char == '\x7f':  # Backspace
                    if input_buffer:
                        input_buffer = input_buffer[:-1]
                        if not data_streaming:
                            sys.stdout.write('\b \b')
                else:
                    input_buffer += char
                    if not data_streaming:
                        sys.stdout.write(char)
                if not data_streaming:
                    sys.stdout.flush()

            # Check for serial data from Teensy
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                text = data.decode('utf-8', errors='ignore')

                # Write to log file (always - raw serial data)
                log_file.write(text)

                # Add to line buffer for processing
                line_buffer += text

                # Process complete lines only
                while '\n' in line_buffer:
                    line, line_buffer = line_buffer.split('\n', 1)
                    line_clean = line.strip().strip('\r')
                    parsed_line = parse_data_line(line)

                    if parsed_line:
                        # Data line
                        last_data_time = current_time
                        data_count += 1

                        if not verbose:
                            if not data_streaming:
                                data_streaming = True
                            if data_count % 100 == 0:
                                sys.stdout.write(f"\r\033[K[streaming... {data_count} lines]")
                                sys.stdout.flush()

                        # Write to streaming CSV
                        stream_file.write(parsed_line + '\n')

                        if verbose:
                            sys.stdout.write(f"\r{line_clean}\n")
                            sys.stdout.flush()

                        continue

                    # Suppress data-like lines in non-verbose mode
                    if not verbose and is_data_like(line_clean):
                        continue

                    # Handle snap responses from Teensy
                    if '[SEEs] SNAP command received' in line_clean:
                        sys.stdout.write(f"\r\033[K📸 SNAP - capturing...\n")
                        sys.stdout.flush()
                        continue

                    # Start capturing snap data
                    if line_clean == '[SNAP_START]':
                        capturing_snap = True
                        snap_data = []
                        snap_count += 1
                        continue

                    # End of snap data - save to file
                    if line_clean == '[SNAP_END]':
                        if capturing_snap and snap_data:
                            snap_timestamp = datetime.now().strftime("%H%M%S")
                            snap_filename = f"SEEs.{session_timestamp}.{snap_timestamp}.csv"
                            snap_path = session_dir / snap_filename
                            with open(snap_path, 'w') as sf:
                                for snap_line in snap_data:
                                    sf.write(snap_line + '\n')
                            sys.stdout.write(f"\r\033[K✅ Snap saved: {snap_filename} ({len(snap_data)-4} hits)\n")
                            sys.stdout.flush()
                        capturing_snap = False
                        snap_data = []
                        continue

                    # Collect snap data lines
                    if capturing_snap:
                        snap_data.append(line_clean)
                        continue

                    if '[SEEs] Snap captured' in line_clean:
                        sys.stdout.write(f"\r\033[K✅ {line_clean}\n")
                        sys.stdout.flush()
                        continue

                    # Handle [SEEs] status messages
                    if line_clean.startswith('[SEEs]'):
                        sys.stdout.write(f"\r\033[K{line_clean}\n")
                        data_count = 0
                        sys.stdout.flush()
                        continue

                    # Skip short lines and command echoes in non-verbose mode
                    if not verbose:
                        if len(line_clean) <= 4:
                            continue
                        if line_clean.lower() in ('on', 'off', 'snap', 'help'):
                            continue

                    if line_clean:
                        if data_streaming and not verbose:
                            sys.stdout.write("\r\033[K")
                        sys.stdout.write(f"\r{line_clean}\n")
                        sys.stdout.flush()

                        if not data_streaming and not verbose:
                            sys.stdout.write(f"SEEs> {input_buffer}")
                            sys.stdout.flush()

    except KeyboardInterrupt:
        pass

    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        log_file.close()
        stream_file.close()
        ser.close()
        print("\n\n✅ Session closed")
        print(f"📁 Stream saved: {session_dir}")
        print(f"   Snaps on Teensy SD: {snap_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SEEs Interactive Console - Body Cam Mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 sees_interactive.py /dev/ttyACM0           # Normal mode
  python3 sees_interactive.py /dev/ttyACM0 -v        # Verbose mode
  python3 sees_interactive.py /tmp/tty_sees          # Simulation

Body cam mode: Teensy streams continuously. Snaps saved to Teensy SD card.

Commands:
  snap       - Capture ±2.5s window to Teensy SD card
  Ctrl+C     - Exit
        """
    )
    parser.add_argument("port", help="Serial port (e.g., /dev/ttyACM0)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show full streaming data output")

    args = parser.parse_args()
    interactive_console(args.port, verbose=args.verbose)
