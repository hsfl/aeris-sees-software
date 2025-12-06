#!/usr/bin/env python3
"""
SEES Python Script Unit Tests

Tests for SEES data processing and analysis functions.

Usage:
    python3 -m unittest test_python_scripts.py
"""

import unittest
import csv
import tempfile
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

# Import test data generator
from test_data_generator import ParticleDetectorSimulator


class TestDataGeneration(unittest.TestCase):
    """Test data generation for reproducibility."""

    def test_reproducible_generation(self):
        """Test that same seed produces same data."""
        sim1 = ParticleDetectorSimulator(seed=42)
        sim2 = ParticleDetectorSimulator(seed=42)

        data1 = sim1.generate_dataset(duration_seconds=1.0, hit_rate_hz=5.0)
        data2 = sim2.generate_dataset(duration_seconds=1.0, hit_rate_hz=5.0)

        self.assertEqual(len(data1), len(data2))
        for i in range(min(10, len(data1))):
            self.assertAlmostEqual(data1[i][0], data2[i][0], places=5)  # time_ms
            self.assertAlmostEqual(data1[i][1], data2[i][1], places=5)  # voltage
            self.assertEqual(data1[i][2], data2[i][2])  # hit
            self.assertEqual(data1[i][3], data2[i][3])  # total_hits

    def test_different_seeds_produce_different_data(self):
        """Test that different seeds produce different data."""
        sim1 = ParticleDetectorSimulator(seed=42)
        sim2 = ParticleDetectorSimulator(seed=123)

        data1 = sim1.generate_dataset(duration_seconds=1.0, hit_rate_hz=5.0)
        data2 = sim2.generate_dataset(duration_seconds=1.0, hit_rate_hz=5.0)

        # At least some voltages should be different
        voltages_different = False
        for i in range(min(100, len(data1), len(data2))):
            if abs(data1[i][1] - data2[i][1]) > 0.001:
                voltages_different = True
                break

        self.assertTrue(voltages_different, "Different seeds should produce different data")


class TestCSVDataLoading(unittest.TestCase):
    """Test CSV data loading and parsing."""

    def setUp(self):
        """Generate test data for each test."""
        self.sim = ParticleDetectorSimulator(seed=42)
        self.test_data = self.sim.generate_dataset(duration_seconds=2.0, hit_rate_hz=5.0)

    def test_csv_format(self):
        """Test that generated data has correct CSV format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            writer = csv.writer(f)
            writer.writerow(['time_ms', 'voltage_V', 'hit', 'total_hits'])

            for time_ms, voltage, hit, total_hits in self.test_data[:10]:
                writer.writerow([f"{time_ms:.1f}", f"{voltage:.4f}", hit, total_hits])

        # Read it back
        with open(temp_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 10)
        self.assertIn('time_ms', rows[0])
        self.assertIn('voltage_V', rows[0])
        self.assertIn('hit', rows[0])
        self.assertIn('total_hits', rows[0])

        Path(temp_path).unlink()


class TestDataValidation(unittest.TestCase):
    """Test data validation and range checking."""

    def setUp(self):
        """Generate test data for each test."""
        self.sim = ParticleDetectorSimulator(seed=42)

    def test_voltage_in_valid_range(self):
        """Test that voltages are in valid ADC range (0-3.3V)."""
        data = self.sim.generate_dataset(duration_seconds=1.0, hit_rate_hz=10.0)

        for time_ms, voltage, hit, total_hits in data:
            self.assertGreaterEqual(voltage, 0.0, f"Voltage {voltage} below 0V at {time_ms}ms")
            self.assertLessEqual(voltage, 3.3, f"Voltage {voltage} above 3.3V at {time_ms}ms")

    def test_hit_is_binary(self):
        """Test that hit flag is always 0 or 1."""
        data = self.sim.generate_dataset(duration_seconds=1.0, hit_rate_hz=5.0)

        for time_ms, voltage, hit, total_hits in data:
            self.assertIn(hit, [0, 1], f"Hit flag {hit} not binary at {time_ms}ms")

    def test_cumulative_counts_monotonic(self):
        """Test that cumulative counts never decrease."""
        data = self.sim.generate_dataset(duration_seconds=2.0, hit_rate_hz=10.0)

        prev_count = 0
        for time_ms, voltage, hit, total_hits in data:
            self.assertGreaterEqual(total_hits, prev_count,
                                    f"Counts decreased at {time_ms}ms: {prev_count} → {total_hits}")
            prev_count = total_hits

    def test_time_monotonic(self):
        """Test that timestamps are monotonically increasing."""
        data = self.sim.generate_dataset(duration_seconds=1.0, hit_rate_hz=5.0)

        prev_time = -1
        for time_ms, voltage, hit, total_hits in data:
            self.assertGreater(time_ms, prev_time,
                               f"Time not increasing: {prev_time} → {time_ms}")
            prev_time = time_ms


class TestHitDetection(unittest.TestCase):
    """Test particle hit detection logic."""

    def setUp(self):
        """Generate test data for each test."""
        self.sim = ParticleDetectorSimulator(seed=42)

    def test_quiet_period_has_no_hits(self):
        """Test that quiet period generates no particle hits."""
        data = self.sim.generate_quiet_period(duration_seconds=1.0)

        total_hits = data[-1][3] if data else 0
        self.assertEqual(total_hits, 0, "Quiet period should have zero hits")

    def test_burst_has_many_hits(self):
        """Test that burst period generates multiple hits."""
        data = self.sim.generate_burst(duration_seconds=1.0, hit_rate_hz=50.0)

        total_hits = data[-1][3] if data else 0
        self.assertGreater(total_hits, 10, "Burst period should have many hits")

    def test_hit_rate_approximately_correct(self):
        """Test that average hit rate matches specified rate."""
        target_rate = 10.0  # hits/s
        duration = 10.0  # seconds
        data = self.sim.generate_dataset(duration_seconds=duration, hit_rate_hz=target_rate)

        actual_hits = data[-1][3] if data else 0
        actual_rate = actual_hits / duration

        # Allow 30% tolerance (Poisson process has variance)
        tolerance = 0.3 * target_rate
        self.assertAlmostEqual(actual_rate, target_rate, delta=tolerance,
                               msg=f"Hit rate {actual_rate:.1f} not within {tolerance:.1f} of target {target_rate:.1f}")


class TestSamplingRate(unittest.TestCase):
    """Test sampling rate and timing."""

    def setUp(self):
        """Generate test data for each test."""
        self.sim = ParticleDetectorSimulator(seed=42)

    def test_sampling_interval(self):
        """Test that samples are spaced correctly (100 µs = 0.1 ms)."""
        data = self.sim.generate_dataset(duration_seconds=1.0, hit_rate_hz=5.0)

        expected_interval = 0.1  # ms
        for i in range(1, min(100, len(data))):
            actual_interval = data[i][0] - data[i - 1][0]
            self.assertAlmostEqual(actual_interval, expected_interval, places=5,
                                   msg=f"Sample interval incorrect at index {i}")

    def test_total_duration(self):
        """Test that generated data has correct total duration."""
        duration = 5.0  # seconds
        data = self.sim.generate_dataset(duration_seconds=duration, hit_rate_hz=5.0)

        expected_samples = int(duration * 10000)  # 10 kHz sampling
        actual_samples = len(data)

        self.assertEqual(actual_samples, expected_samples,
                         f"Expected {expected_samples} samples, got {actual_samples}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Generate test data for each test."""
        self.sim = ParticleDetectorSimulator(seed=42)

    def test_very_short_duration(self):
        """Test generation with very short duration."""
        data = self.sim.generate_dataset(duration_seconds=0.1, hit_rate_hz=5.0)

        expected_samples = 1000  # 0.1s * 10kHz
        self.assertEqual(len(data), expected_samples)

    def test_zero_hit_rate(self):
        """Test generation with zero hit rate."""
        data = self.sim.generate_dataset(duration_seconds=1.0, hit_rate_hz=0.0)

        total_hits = data[-1][3] if data else 0
        self.assertEqual(total_hits, 0, "Zero hit rate should produce zero hits")

    def test_very_high_hit_rate(self):
        """Test generation with very high hit rate."""
        data = self.sim.generate_dataset(duration_seconds=1.0, hit_rate_hz=100.0)

        # Should still generate data without errors
        self.assertGreater(len(data), 0)
        self.assertGreater(data[-1][3], 0)


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
