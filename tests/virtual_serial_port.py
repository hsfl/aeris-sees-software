#!/usr/bin/env python3
"""
Virtual Serial Port for SEES Testing

Simulates a Teensy 4.1 running SEES firmware (body cam mode) for testing without hardware.
Creates a virtual serial port that behaves like the real Teensy.

Body cam mode: Data streams continuously from power-on.
Commands: snap

Usage:
    python3 virtual_serial_port.py

This creates /tmp/tty_sees virtual serial port that behaves like real hardware.
Connect with: python3 scripts/sees_interactive.py /tmp/tty_sees
"""

import os
import pty
import select
import sys
import time
import termios
from pathlib import Path

# Add parent directory to path for test data generator
sys.path.insert(0, str(Path(__file__).parent))
from test_data_generator import ParticleDetectorSimulator


class VirtualSEEsPort:
    """Virtual serial port that simulates SEES firmware (body cam mode)."""

    def __init__(self, port_path='/tmp/tty_sees'):
        """
        Initialize virtual SEES port.

        Args:
            port_path: Path where virtual serial port will be created
        """
        self.port_path = port_path
        self.master_fd = None
        self.slave_fd = None
        self.running = False
        self.simulator = ParticleDetectorSimulator(seed=42)

        # State - ALWAYS streaming in body cam mode
        self.sample_index = 0
        self.current_data = []
        self.snap_count = 0

    def create_virtual_port(self):
        """Create a virtual serial port using pty."""
        self.master_fd, self.slave_fd = pty.openpty()

        # Disable echo on the slave side to prevent feedback loop
        attrs = termios.tcgetattr(self.slave_fd)
        attrs[3] = attrs[3] & ~termios.ECHO  # Disable ECHO flag
        termios.tcsetattr(self.slave_fd, termios.TCSANOW, attrs)

        # Create symlink to make it accessible
        if os.path.exists(self.port_path):
            os.remove(self.port_path)

        slave_name = os.ttyname(self.slave_fd)
        os.symlink(slave_name, self.port_path)

        print(f"✅ Virtual SEES port created: {self.port_path}")
        print(f"   (Real device: {slave_name})")
        print()
        print("Connect with:")
        print(f"  python3 scripts/sees_interactive.py {self.port_path}")
        print()
        print("Body cam mode: ALWAYS streaming")
        print("Command: snap")
        print("Press Ctrl+C to stop")
        print()

    def send_message(self, message):
        """Send a message to the connected client."""
        if self.master_fd:
            os.write(self.master_fd, message.encode())

    def send_boot_message(self):
        """Send boot message matching real SEES firmware (body cam mode)."""
        boot_msg = (
            "[SEEs] ====================================\r\n"
            "[SEEs] SEEs Particle Detector - Starting\r\n"
            "[SEEs] ====================================\r\n"
            "[SEEs] SD card ready\r\n"
            "[SEEs] Initializing circular buffer...\r\n"
            "[CircularBuffer] Initialized (hits-only mode)\r\n"
            "[CircularBuffer]   Capacity: 30000 hits\r\n"
            "[CircularBuffer]   Memory: 240 KB\r\n"
            "[SnapManager] Initialized\r\n"
            "[SnapManager]   Window: +/-2.5 seconds\r\n"
            "[SnapManager]   Output: snaps/\r\n"
            "[SEEs] Body cam mode: ALWAYS streaming\r\n"
            "[SEEs] Commands: snap\r\n"
            "[SEEs] Data format: time_ms,voltage_V,hit,total_hits\r\n"
            "[SEEs] ====================================\r\n"
            "[SEEs] Ready - buffer recording started\r\n"
            "[SEEs] ====================================\r\n"
        )
        self.send_message(boot_msg)

    def handle_command(self, command):
        """
        Handle incoming command from client.
        Matches real SEES firmware behavior (body cam mode - only snap command).

        Args:
            command: Command string
        """
        cmd = command.strip().lower()

        if cmd == 'snap':
            self.snap_count += 1
            self.send_message("[SEEs] SNAP command received\r\n")
            # Simulate snap capture delay
            time.sleep(0.05)
            self.send_message(f"[SnapManager] Extracting +/-2.5s window...\r\n")
            self.send_message(f"[SnapManager]   Extracted 47 hits\r\n")
            self.send_message(f"[SnapManager] Snap saved: snaps/snap_{self.snap_count:05d}_{int(time.time()*1000000):010d}.csv\r\n")
            self.send_message(f"[SEEs] Snap captured! Total snaps: {self.snap_count}\r\n")
            print(f"📸 SNAP #{self.snap_count} triggered")

        elif cmd and cmd not in ('', '\r', '\n'):
            self.send_message(f"[SEEs] Unknown command: {cmd}\r\n")

    def stream_data(self):
        """Stream data samples continuously (body cam mode).

        Sends batches of 25 samples per call to achieve effective 10kHz rate
        when called every 1ms.
        """
        if self.current_data:
            # Send 25 samples per call to achieve ~10kHz effective rate
            batch_size = 25
            lines = []

            for _ in range(batch_size):
                if self.sample_index < len(self.current_data):
                    time_ms, voltage, hit, total_hits = self.current_data[self.sample_index]
                    lines.append(f"{time_ms:.1f},{voltage:.4f},{hit},{total_hits}\r\n")
                    self.sample_index += 1
                else:
                    # Generate more data when we run out
                    self.current_data = self.simulator.generate_dataset(
                        duration_seconds=60.0,
                        hit_rate_hz=5.0
                    )
                    self.sample_index = 0
                    print("🔄 Generated new data batch")
                    break

            if lines:
                self.send_message(''.join(lines))

    def run(self):
        """Main loop for virtual serial port."""
        self.create_virtual_port()
        self.running = True

        # Generate initial dataset - body cam mode starts immediately
        print("📊 Body cam mode: generating initial data...")
        self.current_data = self.simulator.generate_dataset(
            duration_seconds=60.0,
            hit_rate_hz=5.0
        )
        self.sample_index = 0

        # Wait for connection to stabilize before sending anything
        time.sleep(0.2)

        # Flush any garbage from initial connection
        try:
            readable, _, _ = select.select([self.master_fd], [], [], 0.1)
            if readable:
                os.read(self.master_fd, 1024)  # Discard initial garbage
        except OSError:
            pass

        # Send boot message (matches real firmware)
        self.send_boot_message()

        command_buffer = ""

        try:
            while self.running:
                # Check for incoming data
                readable, _, _ = select.select([self.master_fd], [], [], 0.001)

                if readable:
                    try:
                        data = os.read(self.master_fd, 1024)
                        if data:
                            text = data.decode('utf-8', errors='ignore')

                            for char in text:
                                if char == '\r' or char == '\n':
                                    if command_buffer:
                                        self.handle_command(command_buffer)
                                        command_buffer = ""
                                else:
                                    command_buffer += char

                    except OSError:
                        # Client disconnected
                        pass

                # ALWAYS stream data - body cam mode
                self.stream_data()
                time.sleep(0.001)

        except KeyboardInterrupt:
            print("\n⏹️  Stopping virtual serial port...")

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up virtual port."""
        self.running = False

        if self.master_fd:
            os.close(self.master_fd)
        if self.slave_fd:
            os.close(self.slave_fd)

        if os.path.exists(self.port_path):
            os.remove(self.port_path)

        print("✅ Virtual port closed")


def main():
    """Create and run virtual SEES port."""
    port = VirtualSEEsPort()
    port.run()


if __name__ == "__main__":
    main()
