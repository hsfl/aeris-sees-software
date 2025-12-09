#!/usr/bin/env python3
"""
SEEs Interactive Console

The Teensy streams data continuously.
The Teensy maintains the circular buffer and saves snaps to its SD card.
This console logs the stream to the computer and forwards commands.

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
import os
import stat
import fcntl
import subprocess

# Configuration
BAUD_RATE = 115200


class SubprocessSerial:
    """
    Wrapper that provides a serial-like interface for a subprocess.
    Used for simulation mode where we run the native binary directly.
    """
    def __init__(self, cmd, data_port):
        self.proc = subprocess.Popen(
            [cmd, data_port],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0
        )
        # Make stdout non-blocking
        fd = self.proc.stdout.fileno()
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        self._buffer = b""

    @property
    def in_waiting(self):
        """Check how many bytes are available to read"""
        try:
            data = self.proc.stdout.read(4096)
            if data:
                self._buffer += data
        except (BlockingIOError, TypeError):
            pass
        return len(self._buffer)

    def read(self, size=1):
        """Read up to size bytes"""
        try:
            data = self.proc.stdout.read(4096)
            if data:
                self._buffer += data
        except (BlockingIOError, TypeError):
            pass

        result = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return result

    def write(self, data):
        """Write to subprocess stdin"""
        try:
            self.proc.stdin.write(data)
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError):
            pass

    def reset_input_buffer(self):
        """Clear the input buffer"""
        self._buffer = b""
        try:
            while True:
                data = self.proc.stdout.read(4096)
                if not data:
                    break
        except (BlockingIOError, TypeError):
            pass

    def close(self):
        """Terminate the subprocess"""
        self.proc.terminate()
        self.proc.wait()


class PipeSerial:
    """
    Wrapper that provides a serial-like interface for reading from pipes/FIFOs.
    Used for simulation mode where native firmware writes to a named pipe.
    """
    def __init__(self, path):
        self.path = path
        self.fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        self._buffer = b""

    @property
    def in_waiting(self):
        """Check how many bytes are available to read"""
        try:
            data = os.read(self.fd, 4096)
            self._buffer += data
        except BlockingIOError:
            pass
        return len(self._buffer)

    def read(self, size=1):
        """Read up to size bytes"""
        # First try to fill buffer
        try:
            data = os.read(self.fd, 4096)
            self._buffer += data
        except BlockingIOError:
            pass

        # Return requested bytes from buffer
        result = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return result

    def write(self, data):
        """Write not supported for read-only pipe"""
        pass  # Commands go to native firmware's stdin, not back through pipe

    def reset_input_buffer(self):
        """Clear the input buffer"""
        self._buffer = b""
        try:
            while True:
                os.read(self.fd, 4096)
        except BlockingIOError:
            pass

    def close(self):
        """Close the file descriptor"""
        os.close(self.fd)


def is_pipe(path):
    """Check if path is a named pipe (FIFO)"""
    try:
        return stat.S_ISFIFO(os.stat(path).st_mode)
    except:
        return False


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


def interactive_console(port, verbose=False, native_bin=None, data_port=None):
    """Interactive console - logs stream and forwards commands to Teensy

    Args:
        port: Serial port path or pipe path (ignored if native_bin is set)
        verbose: Show full streaming data output
        native_bin: Path to native binary (simulation mode)
        data_port: Data port for native binary (e.g., /tmp/tty_sees)
    """

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
    print("Command: snap (saves ±2.5s to Teensy SD card)")
    print("Ctrl+C to exit")
    if not verbose:
        print("Use -v flag for full streaming data output")
    print()

    # Open serial port, pipe, or subprocess
    if native_bin:
        print(f"  (simulation mode - native binary)")
        print(f"  Binary: {native_bin}")
        print(f"  Data:   {data_port}")
        ser = SubprocessSerial(native_bin, data_port)
    elif is_pipe(port):
        print("  (simulation mode - reading from pipe)")
        ser = PipeSerial(port)
    else:
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
    snap_trigger_time = None

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
                # Convert carriage return to newline for firmware
                if char == '\r':
                    ser.write(b'\n')
                else:
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

                        # If capturing snap, add to snap data
                        if capturing_snap:
                            snap_data.append(parsed_line)
                            continue

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
                        snap_trigger_time = datetime.now()  # Record trigger time for filename
                        sys.stdout.write(f"\r\033[K📸 SNAP - capturing...\n")
                        sys.stdout.flush()
                        continue

                    # Start capturing snap data from firmware
                    if line_clean == '[SNAP_START]':
                        capturing_snap = True
                        snap_data = []
                        snap_count += 1
                        continue

                    # End of snap - save to file
                    if line_clean == '[SNAP_END]':
                        if capturing_snap and snap_data:
                            # Use trigger time (when snap command was sent), not end time
                            snap_time = snap_trigger_time if snap_trigger_time else datetime.now()
                            snap_filename = f"SEEs.{snap_time.strftime('%Y%m%d.%H%M.%S')}.csv"
                            snap_path = session_dir / snap_filename

                            # Count hits and classify by layer based on voltage
                            # Layer thresholds (midpoints between layer voltages):
                            # 1-layer: ~0.25V, 2-layer: ~0.40V, 3-layer: ~0.55V, 4-layer: ~0.70V
                            layer_counts = {1: 0, 2: 0, 3: 0, 4: 0}
                            prev_hit = 0
                            for s in snap_data:
                                parts = s.split(',')
                                if len(parts) >= 3:
                                    try:
                                        voltage = float(parts[1])
                                        hit = int(parts[2])
                                        # Only count on rising edge (transition from 0 to 1)
                                        if hit == 1 and prev_hit == 0:
                                            # Classify by voltage level
                                            if voltage < 0.325:
                                                layer_counts[1] += 1
                                            elif voltage < 0.475:
                                                layer_counts[2] += 1
                                            elif voltage < 0.625:
                                                layer_counts[3] += 1
                                            else:
                                                layer_counts[4] += 1
                                        prev_hit = hit
                                    except ValueError:
                                        pass

                            hits = sum(layer_counts.values())

                            # Calculate start/end times (-7.5s to +2.5s from trigger)
                            from datetime import timedelta
                            start_time = snap_time - timedelta(seconds=7.5)
                            end_time = snap_time + timedelta(seconds=2.5)

                            with open(snap_path, 'w') as sf:
                                # Header metadata matching original format
                                sf.write("===SEEs SNAP START===\n")
                                sf.write(f"Trigger time: {snap_time.strftime('%Y%m%d %H:%M:%S.%f')[:-3]}\n")
                                sf.write("Window: -7.5s to +2.5s (10.0s total)\n")
                                sf.write(f"Start: {start_time.strftime('%H:%M:%S.%f')[:-3]}\n")
                                sf.write(f"End:   {end_time.strftime('%H:%M:%S.%f')[:-3]}\n")
                                sf.write(f"Frames: {len(snap_data)}\n")
                                # Layer hit summary
                                sf.write(f"1:{layer_counts[1]} 2:{layer_counts[2]} 3:{layer_counts[3]} 4:{layer_counts[4]}\n")
                                sf.write("time_ms,voltage_V,hit,total_hits\n")
                                for sample in snap_data:
                                    sf.write(sample + '\n')
                            sys.stdout.write(f"\r\033[K✅ Snap saved: {snap_filename} ({len(snap_data)} samples, {hits} hits)\n")
                            sys.stdout.write(f"   Layers: 1:{layer_counts[1]} 2:{layer_counts[2]} 3:{layer_counts[3]} 4:{layer_counts[4]}\n")
                            sys.stdout.flush()
                        capturing_snap = False
                        snap_data = []
                        continue

                    # Skip header line in snap output
                    if line_clean == 'time_ms,voltage_V,hit,total_hits':
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
        description="SEEs Interactive Console",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 sees_interactive.py /dev/ttyACM0           # Normal mode (real Teensy)
  python3 sees_interactive.py /dev/ttyACM0 -v        # Verbose mode
  python3 sees_interactive.py --native ~/Aeris/bin/sees_native --data /tmp/tty_sees

Teensy streams continuously. Snaps saved to Teensy SD card.

Commands:
  snap       - Capture ±2.5s window to Teensy SD card
  Ctrl+C     - Exit
        """
    )
    parser.add_argument("port", nargs="?", default=None,
                        help="Serial port (e.g., /dev/ttyACM0)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show full streaming data output")
    parser.add_argument("--native", metavar="BINARY",
                        help="Path to native firmware binary (simulation mode)")
    parser.add_argument("--data", metavar="PORT",
                        help="Data port for native binary (e.g., /tmp/tty_sees)")

    args = parser.parse_args()

    if args.native:
        if not args.data:
            parser.error("--data is required when using --native")
        interactive_console(None, verbose=args.verbose,
                          native_bin=args.native, data_port=args.data)
    elif args.port:
        interactive_console(args.port, verbose=args.verbose)
    else:
        parser.error("Either PORT or --native is required")
