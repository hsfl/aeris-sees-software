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
~/sees_outputlogs/YYYYMMDD.HHMM/
├── SEEs.YYYYMMDD.HHMM.log          (full session log)
├── SEEs.YYYYMMDD.HHMM.stream.csv   (streaming data when ON)
├── SEEs.YYYYMMDD.HHMMSS.csv        (snap: ±2.5s around HHMMSS)
└── ...

Usage:
    python3 sees_interactive.py /dev/ttyACM0

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
    base_dir = Path.home() / "sees_outputlogs"
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

    # Skip debug messages and headers
    if not line or line.startswith('[SEEs]') or 'voltage_V' in line:
        return None

    # Validate CSV format
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


def interactive_console(port):
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
    print("═══════════════════════════════════════════════════")
    print()
    print("📊 Commands: on, off, snap")
    print("⌨️  Type commands, Ctrl+C to exit")
    print()

    # Open serial port
    ser = serial.Serial(port, BAUD_RATE, timeout=0.1)

    # Open log files
    log_file = open(log_file_path, 'w', buffering=1)
    stream_file = open(stream_file_path, 'w', buffering=1)
    stream_file.write("time_ms,voltage_V,hit,cum_counts\n")

    # State tracking
    circular_buffer = CircularBuffer(BUFFER_DURATION)
    pending_snaps = []  # List of (snap_time, snap_count) tuples waiting to complete
    snap_count = 0

    # Save terminal settings
    old_settings = termios.tcgetattr(sys.stdin)

    try:
        # Set terminal to raw mode for character-by-character input
        tty.setraw(sys.stdin.fileno())

        while True:
            current_time = time.time()

            # Check for user keyboard input
            if select.select([sys.stdin], [], [], 0)[0]:
                char = sys.stdin.read(1)

                # Ctrl+C to exit
                if ord(char) == 3:
                    break

                # Send to serial port (Teensy will process commands)
                ser.write(char.encode())

                # Echo to console
                sys.stdout.write(char)
                sys.stdout.flush()

            # Check for serial data from Teensy
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                text = data.decode('utf-8', errors='ignore')

                # Echo to console
                sys.stdout.write(text)
                sys.stdout.flush()

                # Write to log file
                log_file.write(text)

                # Process line-by-line
                for line in text.split('\n'):
                    parsed_line = parse_data_line(line)

                    if parsed_line:
                        # Add to circular buffer (always maintain 30s rolling buffer)
                        circular_buffer.add(current_time, parsed_line)

                        # Write to streaming CSV
                        stream_file.write(parsed_line + '\n')

                    # Detect snap command response
                    if '[SEEs] SNAP command received' in line:
                        snap_count += 1
                        snap_time = current_time
                        pending_snaps.append((snap_time, snap_count))

                        print(f"\n📸 SNAP #{snap_count} at {datetime.fromtimestamp(snap_time).strftime('%H:%M:%S')}")
                        print(f"   Waiting {SNAP_WINDOW}s to collect post-snap data...\n")

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

                    print(f"\n✅ SNAP #{snap_num} SAVED: {snap_filename}")
                    print(f"   Window: {dt.strftime('%H:%M:%S')} ±{SNAP_WINDOW}s")
                    print(f"   Frames: {len(window_data)}\n")

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
    if len(sys.argv) < 2:
        print("Usage: python3 sees_interactive.py <port>")
        print("\nExample:")
        print("  python3 sees_interactive.py /dev/ttyACM0")
        print("\nCommands:")
        print("  on   - Start data collection")
        print("  off  - Stop data collection")
        print("  snap - Capture ±2.5s window")
        sys.exit(1)

    port = sys.argv[1]
    interactive_console(port)
