#!/usr/bin/env python3
"""
Virtual Serial Port for SEES Testing

Simulates a Teensy 4.1 running SEES firmware for testing without hardware.
Creates a virtual serial port that responds to SEES commands.

Commands supported:
- on   - Start data collection
- off  - Stop data collection
- snap - Trigger snapshot capture

Usage:
    python3 virtual_serial_port.py

This creates /tmp/tty_sees virtual serial port that behaves like real hardware.
Connect with: python3 sees_interactive.py /tmp/tty_sees
"""

import os
import pty
import select
import sys
import time
import termios
import threading
from pathlib import Path

# Add parent directory to path for test data generator
sys.path.insert(0, str(Path(__file__).parent))
from test_data_generator import ParticleDetectorSimulator


class VirtualSEEsPort:
    """Virtual serial port that simulates SEES firmware."""

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
        self.data_streaming = False
        self.simulator = ParticleDetectorSimulator(seed=42)

        # State
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
        print("Commands: on, off, snap")
        print("Press Ctrl+C to stop")
        print()

    def send_message(self, message):
        """Send a message to the connected client."""
        if self.master_fd:
            os.write(self.master_fd, message.encode())

    def send_boot_message(self):
        """Send boot message matching real SEES firmware."""
        boot_msg = (
            "[SEEs] ====================================\r\n"
            "[SEEs] SEEs Particle Detector - Starting\r\n"
            "[SEEs] ====================================\r\n"
            "[SEEs] SD card ready\r\n"
            "[SEEs] Initializing circular buffer...\r\n"
            "[SEEs] Command-based streaming mode\r\n"
            "[SEEs] Commands: on, off, snap\r\n"
            "[SEEs] Data format: time_ms,voltage_V,hit,cum_counts\r\n"
            "[SEEs] Circular buffer: ACTIVE (body cam mode)\r\n"
            "[SEEs] ====================================\r\n"
            "[SEEs] Ready - buffer recording started\r\n"
            "[SEEs] ====================================\r\n"
        )
        self.send_message(boot_msg)

    def handle_command(self, command):
        """
        Handle incoming command from client.
        Matches real SEES firmware behavior (no prompts, [SEEs] prefixed messages).

        Args:
            command: Command string (on, off, snap, etc.)
        """
        cmd = command.strip().lower()

        if cmd == 'on':
            if not self.data_streaming:
                self.data_streaming = True
                self.sample_index = 0
                # Generate new dataset
                self.current_data = self.simulator.generate_dataset(
                    duration_seconds=60.0,  # Generate 60s of data
                    hit_rate_hz=5.0
                )
                self.send_message("[SEEs] Collection ON\r\n")
                print("📊 Data streaming: ON")

        elif cmd == 'off':
            if self.data_streaming:
                self.data_streaming = False
                self.send_message("[SEEs] Collection OFF\r\n")
                print("⏸️  Data streaming: OFF")

        elif cmd == 'snap':
            # Snap works even when not streaming (buffer always recording)
            self.snap_count += 1
            self.send_message("[SEEs] SNAP command received\r\n")
            self.send_message(f"[SEEs] Snap captured! Total snaps: {self.snap_count}\r\n")
            print(f"📸 SNAP #{self.snap_count} triggered")

        elif cmd and cmd not in ('', '\r', '\n'):
            self.send_message(f"[SEEs] Unknown command: {cmd}\r\n")

    def stream_data(self):
        """Stream data samples when collection is active.

        Sends batches of 25 samples per call to achieve effective 10kHz rate
        when called every 1ms. Extra samples compensate for receiver-side
        processing delays and serial buffering.
        """
        if self.data_streaming and self.current_data:
            # Send 25 samples per call to achieve ~50k frames in 5s window
            # (compensates for receiver timestamp jitter)
            batch_size = 25
            lines = []

            for _ in range(batch_size):
                if self.sample_index < len(self.current_data):
                    time_ms, voltage, hit, cum_counts = self.current_data[self.sample_index]
                    lines.append(f"{time_ms:.1f},{voltage:.4f},{hit},{cum_counts}\r\n")
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
                                    # No prompt - real firmware doesn't have one
                                else:
                                    command_buffer += char
                                    # No echo - real firmware doesn't echo typed chars

                    except OSError:
                        # Client disconnected
                        pass

                # Stream data if active
                if self.data_streaming:
                    self.stream_data()
                    # 1ms sleep, but sending 25 samples per call = 25kHz effective rate
                    time.sleep(0.001)

                else:
                    # No data streaming, just idle
                    time.sleep(0.01)

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
