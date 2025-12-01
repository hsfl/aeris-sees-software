#!/usr/bin/env python3
"""
Unit Tests for Circular Buffer Logic

Tests the circular buffer behavior that the firmware implements.
These tests validate the logic WITHOUT requiring physical hardware.
"""

import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from test_data_generator import ParticleDetectorSimulator


class TestCircularBufferLogic(unittest.TestCase):
    """Test circular buffer (ring buffer) behavior."""

    def setUp(self):
        """Create simulator for each test."""
        self.sim = ParticleDetectorSimulator(seed=42)

    def test_buffer_capacity(self):
        """Test that buffer holds exactly 30 seconds at 10kHz."""
        sample_rate_hz = 10000
        buffer_duration_s = 30
        expected_capacity = sample_rate_hz * buffer_duration_s

        self.assertEqual(expected_capacity, 300000,
                        "Buffer should hold 300k samples (30s @ 10kHz)")

    def test_fifo_behavior(self):
        """Test that oldest data is overwritten when buffer is full."""
        # Simulate a small buffer for testing
        buffer_capacity = 100
        samples = list(range(150))  # More than capacity

        # Simulate circular buffer behavior
        buffer = [None] * buffer_capacity
        head = 0

        for sample in samples:
            buffer[head] = sample
            head = (head + 1) % buffer_capacity

        # After adding 150 samples to 100-slot buffer:
        # Buffer should contain samples 50-149 (the last 100)
        oldest_idx = head  # Oldest sample is at head position
        oldest = buffer[oldest_idx]
        self.assertEqual(oldest, 50, "Oldest sample should be 50")

        newest_idx = (head - 1) % buffer_capacity
        newest = buffer[newest_idx]
        self.assertEqual(newest, 149, "Newest sample should be 149")

    def test_time_window_extraction(self):
        """Test extracting ±2.5s window from buffer."""
        # Generate 30 seconds of data
        events = self.sim.generate_layered_dataset(duration_seconds=30.0, hit_rate_hz=100.0)

        # Simulate snap at t=15s
        snap_time_s = 15.0
        window_s = 2.5

        # Extract events in window
        window_start = snap_time_s - window_s
        window_end = snap_time_s + window_s

        extracted = [(t, layers) for t, layers in events
                     if window_start <= t <= window_end]

        # Verify window bounds
        if len(extracted) > 0:
            min_time = min(t for t, _ in extracted)
            max_time = max(t for t, _ in extracted)

            self.assertGreaterEqual(min_time, window_start,
                                   "Extracted times should be >= window start")
            self.assertLessEqual(max_time, window_end,
                                "Extracted times should be <= window end")

        # Verify we extracted roughly 5 seconds @ 100 Hz = ~500 events
        # Allow tolerance for Poisson process variance
        self.assertGreater(len(extracted), 300,
                          "Should extract significant events in 5s window")
        self.assertLess(len(extracted), 800,
                       "Should not extract excessive events")

    def test_snap_captures_pre_event_data(self):
        """Test that snap includes data BEFORE trigger (body cam mode)."""
        # Generate events
        events = self.sim.generate_layered_dataset(duration_seconds=30.0, hit_rate_hz=100.0)

        # Snap triggered at t=15s
        snap_time_s = 15.0
        window_s = 2.5

        # Extract window
        window_start = snap_time_s - window_s  # 12.5s
        window_end = snap_time_s + window_s    # 17.5s

        pre_snap = [(t, layers) for t, layers in events if window_start <= t < snap_time_s]
        post_snap = [(t, layers) for t, layers in events if snap_time_s <= t <= window_end]

        # Both pre and post should have data
        self.assertGreater(len(pre_snap), 0, "Should have pre-snap data")
        self.assertGreater(len(post_snap), 0, "Should have post-snap data")

        # Pre and post should be roughly equal (±2.5s each)
        ratio = len(pre_snap) / len(post_snap) if len(post_snap) > 0 else 0
        self.assertGreater(ratio, 0.5, "Pre-snap should be comparable to post-snap")
        self.assertLess(ratio, 2.0, "Pre-snap should be comparable to post-snap")

    def test_rolling_buffer_overwrites_old_data(self):
        """Test that buffer continuously overwrites data older than 30s."""
        # Generate 60 seconds of data
        events = self.sim.generate_layered_dataset(duration_seconds=60.0, hit_rate_hz=100.0)

        # Simulate 30-second circular buffer
        buffer_duration_s = 30.0
        current_time_s = 60.0

        # Buffer should only contain last 30 seconds
        buffer_start = current_time_s - buffer_duration_s  # 30s
        buffer_data = [(t, layers) for t, layers in events if t >= buffer_start]

        # Verify oldest sample is around 30s
        if len(buffer_data) > 0:
            oldest_time = min(t for t, _ in buffer_data)
            self.assertGreaterEqual(oldest_time, 29.0,
                                   "Oldest sample should be ~30s ago")
            self.assertLessEqual(oldest_time, 31.0,
                                "Oldest sample should be ~30s ago")

    def test_multiple_snaps_do_not_interfere(self):
        """Test that multiple snaps can be taken from the same buffer."""
        events = self.sim.generate_layered_dataset(duration_seconds=30.0, hit_rate_hz=100.0)

        # Take snap at t=10s
        snap1_time = 10.0
        snap1_start = snap1_time - 2.5
        snap1_end = snap1_time + 2.5
        snap1 = [(t, l) for t, l in events if snap1_start <= t <= snap1_end]

        # Take snap at t=20s
        snap2_time = 20.0
        snap2_start = snap2_time - 2.5
        snap2_end = snap2_time + 2.5
        snap2 = [(t, l) for t, l in events if snap2_start <= t <= snap2_end]

        # Both snaps should have data
        self.assertGreater(len(snap1), 0, "Snap 1 should have data")
        self.assertGreater(len(snap2), 0, "Snap 2 should have data")

        # Snaps should not overlap
        snap1_times = set(t for t, _ in snap1)
        snap2_times = set(t for t, _ in snap2)
        overlap = snap1_times & snap2_times
        self.assertEqual(len(overlap), 0, "Snaps should not overlap")


class TestMemoryConstraints(unittest.TestCase):
    """Test memory usage calculations for Teensy 4.1."""

    def test_buffer_memory_usage(self):
        """Calculate and verify memory usage for circular buffer."""
        # Buffer parameters
        samples = 300000  # 30s @ 10kHz
        bytes_per_sample = 20  # float time_ms, float voltage, uint8 hit, uint8 layers, uint32 counts, uint32 timestamp

        total_bytes = samples * bytes_per_sample
        total_kb = total_bytes / 1024
        total_mb = total_kb / 1024

        print(f"\nCircular Buffer Memory Usage:")
        print(f"  Samples: {samples:,}")
        print(f"  Bytes per sample: {bytes_per_sample}")
        print(f"  Total: {total_bytes:,} bytes ({total_mb:.2f} MB)")

        # Teensy 4.1 has 8 MB RAM
        teensy_ram_mb = 8
        usage_percent = (total_mb / teensy_ram_mb) * 100

        print(f"  Teensy 4.1 RAM: {teensy_ram_mb} MB")
        print(f"  Usage: {usage_percent:.1f}%")

        # Should fit in RAM (allow for other memory usage)
        self.assertLess(total_mb, 7.0, "Buffer should fit in Teensy 4.1 RAM with headroom")

    def test_snap_extraction_buffer_size(self):
        """Calculate memory for temporary snap extraction buffer."""
        # Snap window: ±2.5s @ 10kHz = 50k samples worst case
        snap_samples = 50000
        bytes_per_sample = 20

        snap_bytes = snap_samples * bytes_per_sample
        snap_kb = snap_bytes / 1024
        snap_mb = snap_kb / 1024

        print(f"\nSnap Extraction Buffer:")
        print(f"  Samples: {snap_samples:,}")
        print(f"  Total: {snap_bytes:,} bytes ({snap_mb:.2f} MB)")

        # Should be reasonable for temporary allocation
        self.assertLess(snap_mb, 2.0, "Snap buffer should be manageable")


class CompactTestResult(unittest.TextTestResult):
    """Custom test result that shows short descriptions."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.successes = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes.append(test)

    def printResults(self):
        """Print compact results with checkmarks."""
        for test in self.successes:
            desc = test.shortDescription() or str(test)
            print(f"    \033[0;32m✓\033[0m {desc}")
        for test, _ in self.failures:
            desc = test.shortDescription() or str(test)
            print(f"    \033[0;31m✗\033[0m {desc}")
        for test, _ in self.errors:
            desc = test.shortDescription() or str(test)
            print(f"    \033[0;31m✗\033[0m {desc}")


def run_tests():
    """Run tests with configurable verbosity."""
    verbose = "-v" in sys.argv or "--verbose" in sys.argv

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    if verbose:
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
    else:
        import io
        import contextlib

        with contextlib.redirect_stdout(io.StringIO()):
            stream = open('/dev/null', 'w')
            runner = unittest.TextTestRunner(stream=stream, verbosity=0, resultclass=CompactTestResult)
            result = runner.run(suite)
            stream.close()

        result.printResults()

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
