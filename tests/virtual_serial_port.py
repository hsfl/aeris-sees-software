#!/usr/bin/env python3
"""
Virtual Serial Port for SEES Testing

Pumps simulated ADC data to a virtual serial port.
This is a DATA SOURCE ONLY - it does NOT simulate firmware behavior.

The data from this port should be fed INTO the firmware (native build or Teensy).
The firmware handles all logic (circular buffer, snap, etc).

Usage:
    python3 virtual_serial_port.py

This creates /tmp/tty_sees virtual serial port that streams ADC-like data.
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
    """Virtual serial port that pumps simulated ADC data."""

    def __init__(self, port_path='/tmp/tty_sees'):
        """
        Initialize virtual data source.

        Args:
            port_path: Path where virtual serial port will be created
        """
        self.port_path = port_path
        self.master_fd = None
        self.slave_fd = None
        self.running = False
        self.simulator = ParticleDetectorSimulator(seed=42)

        # Data streaming state
        self.sample_index = 0
        self.current_data = []

    def create_virtual_port(self):
        """Create a virtual serial port using pty."""
        try:
            self.master_fd, self.slave_fd = pty.openpty()
        except Exception as e:
            print(f"❌ Failed to create pty: {e}", file=sys.stderr)
            raise

        try:
            # Disable echo on the slave side to prevent feedback loop
            attrs = termios.tcgetattr(self.slave_fd)
            attrs[3] = attrs[3] & ~termios.ECHO  # Disable ECHO flag
            termios.tcsetattr(self.slave_fd, termios.TCSANOW, attrs)
        except Exception as e:
            print(f"⚠️ Warning: Could not configure termios: {e}", file=sys.stderr)

        # Create symlink to make it accessible
        try:
            # Use islink to catch broken symlinks (exists returns False for broken links)
            if os.path.islink(self.port_path) or os.path.exists(self.port_path):
                os.remove(self.port_path)

            slave_name = os.ttyname(self.slave_fd)
            os.symlink(slave_name, self.port_path)
        except Exception as e:
            print(f"❌ Failed to create symlink {self.port_path}: {e}", file=sys.stderr)
            raise

        # Verify symlink was created
        if not os.path.exists(self.port_path):
            print(f"❌ Symlink not created: {self.port_path}", file=sys.stderr)
            raise RuntimeError(f"Failed to create symlink: {self.port_path}")

        print(f"✅ Virtual data source created: {self.port_path}")
        print(f"   (Real device: {slave_name})")
        print()
        print("This is a DATA SOURCE - feed into firmware for processing")
        print("Press Ctrl+C to stop")
        print()

    def send_data(self, data):
        """Send data to the port."""
        if self.master_fd:
            os.write(self.master_fd, data.encode())

    def stream_data(self):
        """Stream ADC data samples continuously.

        Sends batches of 25 samples per call to achieve effective 10kHz rate
        when called every 1ms.
        """
        if self.current_data:
            batch_size = 25
            lines = []

            for _ in range(batch_size):
                if self.sample_index < len(self.current_data):
                    time_ms, voltage, hit, total_hits = self.current_data[self.sample_index]
                    lines.append(f"{time_ms:.1f},{voltage:.4f},{hit},{total_hits}\r\n")
                    self.sample_index += 1
                else:
                    # Generate more data when we run out
                    self.current_data, _ = self.simulator.generate_dataset(
                        duration_seconds=60.0,
                        hit_rate_hz=5.0
                    )
                    self.sample_index = 0
                    print("🔄 Generated new data batch")
                    break

            if lines:
                self.send_data(''.join(lines))

    def run(self):
        """Main loop - just pump data."""
        self.create_virtual_port()
        self.running = True

        # Generate initial dataset
        print("📊 Generating initial data...")
        self.current_data, _ = self.simulator.generate_dataset(
            duration_seconds=60.0,
            hit_rate_hz=5.0
        )
        self.sample_index = 0

        # Wait for connection to stabilize
        time.sleep(0.2)

        try:
            while self.running:
                # Just pump data - nothing else
                self.stream_data()
                time.sleep(0.001)

        except KeyboardInterrupt:
            print("\n⏹️  Stopping data source...")

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

        print("✅ Data source closed")


def main():
    """Create and run virtual data source."""
    port = VirtualSEEsPort()
    port.run()


if __name__ == "__main__":
    main()
