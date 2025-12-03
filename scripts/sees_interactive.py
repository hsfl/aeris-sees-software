#!/usr/bin/env python3
"""
SEEs Interactive Console with Command Control

Commands:
- on   - Start data collection (streams CSV data)
- off  - Stop data collection
- snap - Save ±2.5s window from 30-second circular buffer

How snap works:
- Maintains 30s rolling buffer of data
- When you type 'snap' at time T (e.g., 21:05:15):
  - Waits 2.5s to collect post-snap data
  - Extracts data from (T-2.5s) to (T+2.5s)
  - Saves to: SEEs.YYYYMMDD.HHMMSS.csv (e.g., SEEs.20251113.210515.csv)

Directory structure:
~/Aeris/data/sees/YYYYMMDD.HHMM/
├── SEEs.YYYYMMDD.HHMM.log          (full session log)
├── SEEs.YYYYMMDD.HHMM.stream.csv   (streaming data when ON)
├── SEEs.YYYYMMDD.HHMMSS.csv        (snap: ±2.5s around HHMMSS)
└── ...

Usage:
    python3 sees_interactive.py /dev/ttyACM0
    python3 sees_interactive.py /dev/ttyACM0 -v    # Verbose mode

Controls:
    on   - Start collecting (builds 30s buffer)
    off  - Stop collecting
    snap - Capture ±2.5s window centered on snap time
    Ctrl+C to exit
"""

import serial
import sys
import select
import termios
import tty
import argparse
from datetime import datetime
from pathlib import Path
from collections import deque
import time

# Configuration
BUFFER_DURATION = 30.0  # seconds of rolling buffer to maintain
SNAP_WINDOW = 2.5  # seconds before and after snap (±2.5s = 5s total)
BAUD_RATE = 115200

class CircularBuffer:
    """Time-based circular buffer for data"""

    def __init__(self, duration_seconds):
        self.duration = duration_seconds
        self.buffer = deque()

    def add(self, timestamp, data_line):
        """Add a data point with timestamp"""
        self.buffer.append((timestamp, data_line))
        self._cleanup_old_entries(timestamp)

    def _cleanup_old_entries(self, current_time):
        """Remove entries older than buffer duration"""
        cutoff_time = current_time - self.duration
        while self.buffer and self.buffer[0][0] < cutoff_time:
            self.buffer.popleft()

    def get_all(self):
        """Get all buffered data"""
        return [data for _, data in self.buffer]

    def get_window(self, center_time, window_seconds):
        """
        Get data within ±window_seconds of center_time

        Args:
            center_time: Center timestamp (Unix time)
            window_seconds: Half-width of window in seconds

        Returns:
            List of data lines within [center_time - window, center_time + window]
        """
        start_time = center_time - window_seconds
        end_time = center_time + window_seconds

        window_data = []
        for timestamp, data in self.buffer:
            if start_time <= timestamp <= end_time:
                window_data.append(data)

        return window_data

    def clear(self):
        """Clear the buffer"""
        self.buffer.clear()


def create_session_directory():
    """Create timestamped session directory"""
    base_dir = Path.home() / "Aeris" / "data" / "sees"
    session_timestamp = datetime.now().strftime("%Y%m%d.%H%M")
    session_dir = base_dir / session_timestamp
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir, session_timestamp


def generate_snap_filename(snap_time):
    """
    Generate snap filename: SEEs.YYYYMMDD.HHMMSS.csv

    Args:
        snap_time: Unix timestamp of snap command

    Returns:
        Filename like "SEEs.20251113.210515.csv"
    """
    dt = datetime.fromtimestamp(snap_time)
    return f"SEEs.{dt.strftime('%Y%m%d.%H%M%S')}.csv"


def generate_log_filename(session_timestamp):
    """Generate session log filename"""
    return f"SEEs.{session_timestamp}.log"


def generate_stream_filename(session_timestamp):
    """Generate streaming CSV filename"""
    return f"SEEs.{session_timestamp}.stream.csv"


def parse_data_line(line):
    """
    Parse CSV data line: time_ms,voltage_V,hit,cum_counts
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

    # Validate CSV format: time_ms,voltage_V,hit,cum_counts
    parts = line.split(',')
    if len(parts) == 4:
        try:
            float(parts[0])  # time_ms
            float(parts[1])  # voltage_V
            int(parts[2])    # hit
            int(parts[3])    # cum_counts
            return line
        except ValueError:
            return None

    return None


def is_data_like(line):
    """
    Check if a line looks like it might be data (numeric with commas).
    Used to suppress partial/malformed data lines in non-verbose mode.
    Catches cases like "s3362.6,0.0804,0,12" where echoed chars prepend data.
    """
    line = line.strip()
    if not line:
        return False

    # If it starts with a digit or minus sign and contains commas, it's probably data
    if (line[0].isdigit() or line[0] == '-') and ',' in line:
        return True

    # Check if it contains comma-separated numbers (data with echo prefix)
    # Pattern: anything followed by digits, comma, digits
    if ',' in line:
        parts = line.split(',')
        # If we have 4 parts and the last 3 look numeric, it's corrupted data
        if len(parts) >= 3:
            try:
                # Try parsing the last few parts as numbers
                float(parts[-3].lstrip('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))
                float(parts[-2])
                float(parts[-1])
                return True
            except (ValueError, IndexError):
                pass

    return False


def interactive_console(port, verbose=False):
    """Interactive console with command control"""

    # Create session directory
    session_dir, session_timestamp = create_session_directory()
    log_filename = generate_log_filename(session_timestamp)
    stream_filename = generate_stream_filename(session_timestamp)
    log_file_path = session_dir / log_filename
    stream_file_path = session_dir / stream_filename

    print("═══════════════════════════════════════════════════")
    print("  SEEs Interactive Console")
    print("═══════════════════════════════════════════════════")
    print(f"  Port:         {port}")
    print(f"  Session dir:  {session_dir}")
    print(f"  Log file:     {log_filename}")
    print(f"  Stream file:  {stream_filename}")
    print(f"  Verbose:      {'ON' if verbose else 'OFF'}")
    print("═══════════════════════════════════════════════════")
    print()
    print("Commands: on, off, snap")
    print("Type commands, Ctrl+C to exit")
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
    stream_file.write("time_ms,voltage_V,hit,cum_counts\n")

    # State tracking
    circular_buffer = CircularBuffer(BUFFER_DURATION)
    pending_snaps = []  # List of (snap_time, snap_count) tuples waiting to complete
    snap_count = 0
    data_streaming = False  # Track if data is actively streaming
    last_data_time = 0  # Last time we received data
    data_count = 0  # Count data lines for status indicator

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
                    # Clear the status line and show prompt
                    sys.stdout.write(f"\r\033[K")  # Clear line
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
                    input_buffer = ""  # Clear on enter
                elif char == '\x7f':  # Backspace
                    if input_buffer:
                        input_buffer = input_buffer[:-1]
                        if not data_streaming:
                            sys.stdout.write('\b \b')
                else:
                    input_buffer += char
                    # Only echo when not streaming - during streaming it corrupts output
                    if not data_streaming:
                        sys.stdout.write(char)
                if not data_streaming:
                    sys.stdout.flush()

            # Check for serial data from Teensy
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                text = data.decode('utf-8', errors='ignore')

                # Write to log file (always)
                log_file.write(text)

                # Add to line buffer for processing
                line_buffer += text

                # Process complete lines only
                while '\n' in line_buffer:
                    line, line_buffer = line_buffer.split('\n', 1)
                    # Strip whitespace and \r from both ends
                    line_clean = line.strip().strip('\r')
                    parsed_line = parse_data_line(line)

                    if parsed_line:
                        # Data line - always silent in non-verbose mode
                        last_data_time = current_time
                        data_count += 1

                        # Update streaming state and indicator (non-verbose only)
                        if not verbose:
                            if not data_streaming:
                                data_streaming = True
                            # Update indicator every 100 lines
                            if data_count % 100 == 0:
                                sys.stdout.write(f"\r\033[K[streaming... {data_count} lines]")
                                sys.stdout.flush()

                        # Add to circular buffer (always maintain 30s rolling buffer)
                        circular_buffer.add(current_time, parsed_line)

                        # Write to streaming CSV
                        stream_file.write(parsed_line + '\n')

                        # In verbose mode, show the data
                        if verbose:
                            sys.stdout.write(f"\r{line_clean}\n")
                            sys.stdout.flush()

                        # Don't process further - this was a data line
                        continue

                    # In non-verbose mode, suppress anything that looks like data
                    if not verbose and is_data_like(line_clean):
                        continue

                    # Handle [SEEs] status messages FIRST - before any filtering
                    # Detect snap command response
                    if '[SEEs] SNAP command received' in line_clean:
                        snap_count += 1
                        snap_time = current_time
                        pending_snaps.append((snap_time, snap_count))

                        # Clear any streaming indicator and show snap message
                        sys.stdout.write(f"\r\033[K📸 SNAP #{snap_count} at {datetime.fromtimestamp(snap_time).strftime('%H:%M:%S')}\n")
                        sys.stdout.write(f"\r\033[K   Waiting {SNAP_WINDOW}s to collect post-snap data...\n")
                        sys.stdout.flush()
                        continue

                    # Handle [SEEs] status messages - always show these prominently
                    if line_clean.startswith('[SEEs]'):
                        # Clear current line (may have streaming indicator), print message on fresh line
                        sys.stdout.write(f"\r\033[K")  # Clear any streaming indicator
                        sys.stdout.write(f"{line_clean}\n")
                        sys.stdout.write(f"\r")  # Position cursor at start of new line for next indicator
                        # Reset data_count so streaming indicator starts fresh after status message
                        data_count = 0
                        sys.stdout.flush()
                        continue

                    # Skip short lines and command echo artifacts in non-verbose mode
                    # (After [SEEs] checks so status messages aren't filtered)
                    if not verbose:
                        # Skip very short lines (echo artifacts)
                        if len(line_clean) <= 4:
                            continue
                        # Skip lines that look like typed commands or their echoes
                        if line_clean.lower() in ('on', 'off', 'snap', 'help'):
                            continue

                    if line_clean:
                        # Non-data line (status message, command response, etc.)
                        # Clear streaming indicator if needed
                        if data_streaming and not verbose:
                            sys.stdout.write("\r\033[K")
                        sys.stdout.write(f"\r{line_clean}\n")
                        sys.stdout.flush()

                        # If not streaming in non-verbose mode, redraw prompt
                        if not data_streaming and not verbose:
                            sys.stdout.write(f"SEEs> {input_buffer}")
                            sys.stdout.flush()

            # Check for completed snaps (wait SNAP_WINDOW seconds after snap to collect ±window)
            completed_snaps = []
            for snap_time, snap_num in pending_snaps:
                elapsed = current_time - snap_time
                if elapsed >= SNAP_WINDOW:
                    # Extract ±SNAP_WINDOW seconds around snap_time
                    window_data = circular_buffer.get_window(snap_time, SNAP_WINDOW)

                    # Save snap to file
                    snap_filename = generate_snap_filename(snap_time)
                    snap_path = session_dir / snap_filename

                    dt = datetime.fromtimestamp(snap_time)
                    with open(snap_path, 'w') as f:
                        f.write("===SEEs SNAP START===\n")
                        f.write(f"Snap time: {dt.strftime('%Y%m%d %H:%M:%S.%f')[:-3]}\n")
                        f.write(f"Window: ±{SNAP_WINDOW}s ({SNAP_WINDOW * 2}s total)\n")
                        f.write(f"Start: {datetime.fromtimestamp(snap_time - SNAP_WINDOW).strftime('%H:%M:%S.%f')[:-3]}\n")
                        f.write(f"End:   {datetime.fromtimestamp(snap_time + SNAP_WINDOW).strftime('%H:%M:%S.%f')[:-3]}\n")
                        f.write(f"Frames: {len(window_data)}\n")
                        f.write("time_ms,voltage_V,hit,cum_counts\n")

                        for data_line in window_data:
                            f.write(data_line + '\n')

                        f.write("===SEEs SNAP END===\n")

                    sys.stdout.write(f"\r\033[K✅ SNAP #{snap_num} SAVED: {snap_filename}\n")
                    sys.stdout.write(f"\r\033[K   Window: {dt.strftime('%H:%M:%S')} ±{SNAP_WINDOW}s\n")
                    sys.stdout.write(f"\r\033[K   Frames: {len(window_data)}\n")
                    sys.stdout.flush()

                    completed_snaps.append((snap_time, snap_num))

            # Remove completed snaps from pending list
            for completed in completed_snaps:
                pending_snaps.remove(completed)

    except KeyboardInterrupt:
        pass

    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        log_file.close()
        stream_file.close()
        ser.close()
        print("\n\n✅ Session closed")
        print(f"📁 Data saved in: {session_dir}")
        print(f"   Snaps captured: {snap_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SEEs Interactive Console with Command Control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 sees_interactive.py /dev/ttyACM0           # Normal mode (clean output)
  python3 sees_interactive.py /dev/ttyACM0 -v        # Verbose mode (full streaming data)
  python3 sees_interactive.py /tmp/tty_sees          # Virtual serial port

In-console commands:
  on         - Start data collection
  off        - Stop data collection
  snap       - Capture ±2.5s window
  Ctrl+C     - Exit
        """
    )
    parser.add_argument("port", help="Serial port (e.g., /dev/ttyACM0 or /tmp/tty_sees)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose mode - show full streaming data output")

    args = parser.parse_args()
    interactive_console(args.port, verbose=args.verbose)
