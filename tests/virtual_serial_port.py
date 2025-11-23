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

    def create_virtual_port(self):
        """Create a virtual serial port using pty."""
        self.master_fd, self.slave_fd = pty.openpty()

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

    def handle_command(self, command):
        """
        Handle incoming command from client.

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
                self.send_message("[SEEs] Data collection started\r\n")
                print("📊 Data streaming: ON")
            else:
                self.send_message("[SEEs] Already collecting data\r\n")

        elif cmd == 'off':
            if self.data_streaming:
                self.data_streaming = False
                self.send_message("[SEEs] Data collection stopped\r\n")
                print("⏸️  Data streaming: OFF")
            else:
                self.send_message("[SEEs] Not currently collecting\r\n")

        elif cmd == 'snap':
            if self.data_streaming:
                self.send_message("[SEEs] SNAP command received\r\n")
                print("📸 SNAP triggered")
            else:
                self.send_message("[SEEs] Start collection with 'on' first\r\n")

        elif cmd == 'help' or cmd == '?':
            help_text = (
                "[SEEs] Available commands:\r\n"
                "  on   - Start data collection\r\n"
                "  off  - Stop data collection\r\n"
                "  snap - Capture snapshot\r\n"
                "  help - Show this help\r\n"
            )
            self.send_message(help_text)

        elif cmd:
            self.send_message(f"[SEEs] Unknown command: {cmd}\r\n")

    def stream_data(self):
        """Stream data samples when collection is active."""
        if self.data_streaming and self.current_data:
            if self.sample_index < len(self.current_data):
                time_ms, voltage, hit, cum_counts = self.current_data[self.sample_index]

                # Format: time_ms,voltage_V,hit,cum_counts
                data_line = f"{time_ms:.1f},{voltage:.4f},{hit},{cum_counts}\r\n"
                self.send_message(data_line)

                self.sample_index += 1

                # Loop back if we run out of data
                if self.sample_index >= len(self.current_data):
                    # Generate more data
                    self.current_data = self.simulator.generate_dataset(
                        duration_seconds=60.0,
                        hit_rate_hz=5.0
                    )
                    self.sample_index = 0
                    print("🔄 Generated new data batch")

    def run(self):
        """Main loop for virtual serial port."""
        self.create_virtual_port()
        self.running = True

        # Send startup message
        time.sleep(0.1)
        startup_msg = (
            "\r\n"
            "═══════════════════════════════════════════\r\n"
            "  SEEs Payload Firmware (Virtual)\r\n"
            "═══════════════════════════════════════════\r\n"
            "  ADC-based particle detector\r\n"
            "  Sampling: 10 kHz\r\n"
            "  Window: 0.30V - 0.80V\r\n"
            "═══════════════════════════════════════════\r\n"
            "\r\n"
            "Type 'help' for commands\r\n"
            "\r\n"
            "SEEs> "
        )
        self.send_message(startup_msg)

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
                                        # Echo prompt
                                        if not self.data_streaming:
                                            self.send_message("SEEs> ")
                                else:
                                    command_buffer += char
                                    # Echo character
                                    os.write(self.master_fd, char.encode())

                    except OSError:
                        # Client disconnected
                        pass

                # Stream data if active
                if self.data_streaming:
                    self.stream_data()
                    # Simulate 10 kHz sampling rate (0.1 ms period)
                    # For testing, we can speed this up
                    time.sleep(0.001)  # 1 ms (10x faster than real time)

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
