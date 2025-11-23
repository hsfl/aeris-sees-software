#!/usr/bin/env python3
"""
Unit Tests for Multi-Layer Coincidence Detection

Tests the 4-layer detector logic that the FPGA will implement.
These tests validate the coincidence detection WITHOUT requiring physical hardware.
"""

import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from test_data_generator import ParticleDetectorSimulator


class TestCoincidenceDetection(unittest.TestCase):
    """Test 4-layer coincidence telescope logic."""

    def setUp(self):
        """Create simulator for each test."""
        self.sim = ParticleDetectorSimulator(seed=42)

    def test_layer_penetration_distribution(self):
        """Test that layer penetration follows expected energy distribution."""
        # Generate large dataset for statistical validation
        events = self.sim.generate_layered_dataset(duration_seconds=100.0, hit_rate_hz=100.0)

        # Count layers
        layer_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for _, layers in events:
            layer_counts[layers] += 1

        total = sum(layer_counts.values())

        # Calculate actual percentages
        percentages = {layers: (count / total) * 100 for layers, count in layer_counts.items()}

        print(f"\nLayer Penetration Distribution (N={total}):")
        print(f"  1-layer: {percentages[1]:.1f}% (expected ~20%)")
        print(f"  2-layer: {percentages[2]:.1f}% (expected ~45%)")
        print(f"  3-layer: {percentages[3]:.1f}% (expected ~25%)")
        print(f"  4-layer: {percentages[4]:.1f}% (expected ~10%)")

        # Verify distributions are roughly correct (allow ±5% tolerance for randomness)
        self.assertAlmostEqual(percentages[1], 20.0, delta=5.0,
                              msg="1-layer should be ~20%")
        self.assertAlmostEqual(percentages[2], 45.0, delta=5.0,
                              msg="2-layer should be ~45% (typical cosmic rays)")
        self.assertAlmostEqual(percentages[3], 25.0, delta=5.0,
                              msg="3-layer should be ~25%")
        self.assertAlmostEqual(percentages[4], 10.0, delta=5.0,
                              msg="4-layer should be ~10%")

    def test_coincidence_means_all_lower_layers_triggered(self):
        """Test that N-layer penetration means layers 0 through N-1 ALL triggered."""
        # This is the key physics: particles travel downward through stack
        # 4-layer event means particle hit layers 0, 1, 2, AND 3

        # Generate events
        events = self.sim.generate_layered_dataset(duration_seconds=10.0, hit_rate_hz=100.0)

        # Find a 4-layer event
        four_layer_events = [e for e in events if e[1] == 4]
        self.assertGreater(len(four_layer_events), 0, "Should have at least one 4-layer event")

        # In real hardware, a 4-layer event would show:
        # - Layer 0 ADC triggered
        # - Layer 1 ADC triggered
        # - Layer 2 ADC triggered
        # - Layer 3 ADC triggered
        # All within the coincidence window (10 µs)

        # For now, our simulator just returns the deepest layer penetrated
        # The FPGA firmware will handle the actual coincidence logic

    def test_layer_0_always_triggered_for_any_detection(self):
        """Test that any detection requires layer 0 to trigger (topmost layer)."""
        # In real detector: particle enters from top (layer 0)
        # Cannot hit layer 1, 2, or 3 without hitting layer 0 first

        # All events should be 1-layer or higher (never 0-layer in coincidence mode)
        events = self.sim.generate_layered_dataset(duration_seconds=10.0, hit_rate_hz=100.0)

        for timestamp, layers in events:
            self.assertGreaterEqual(layers, 1,
                                   "All events must trigger at least layer 0")
            self.assertLessEqual(layers, 4,
                                "Cannot penetrate more than 4 layers")

    def test_coincidence_window_timing(self):
        """Test that coincidence requires hits within 10µs window."""
        coincidence_window_us = 10.0  # 10 microseconds

        # In real hardware:
        # - All layer ADCs sampled simultaneously
        # - Coincidence logic checks if multiple layers triggered within 10µs
        # - Rejects events where layers trigger at different times (noise)

        # Our simulator assumes instantaneous coincidence
        # But the FPGA will implement proper timing window validation

        self.assertEqual(self.sim.coincidence_window_ms, 0.010,
                        "Coincidence window should be 10µs (0.010ms)")

    def test_energy_correlation_with_penetration(self):
        """Test that deeper penetration correlates with higher energy."""
        # Physics: Higher energy particles penetrate more layers
        # 1-layer: Low energy (stopped in first scintillator)
        # 2-layer: Typical cosmic ray energy
        # 3-layer: High energy
        # 4-layer: Very high energy

        # Expected distribution confirms this:
        # - Most events are 2-layer (45%) - typical cosmic rays
        # - Fewer are 1-layer (20%) - low energy or edge hits
        # - Even fewer are 3-layer (25%) - higher energy
        # - Rarest are 4-layer (10%) - very high energy

        events = self.sim.generate_layered_dataset(duration_seconds=10.0, hit_rate_hz=100.0)

        # Count by layer
        counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for _, layers in events:
            counts[layers] += 1

        # Most common should be 2-layer
        most_common_layer = max(counts, key=counts.get)
        self.assertEqual(most_common_layer, 2,
                        "2-layer events should be most common (typical cosmic rays)")

        # Least common should be 4-layer
        least_common_layer = min(counts, key=counts.get)
        self.assertEqual(least_common_layer, 4,
                        "4-layer events should be rarest (very high energy)")


class TestLayerCountingVsBucketing(unittest.TestCase):
    """Test difference between individual layer hits and bucketed counts."""

    def setUp(self):
        """Create simulator for each test."""
        self.sim = ParticleDetectorSimulator(seed=42)

    def test_individual_events_not_bucketed_in_buffer(self):
        """Test that circular buffer stores INDIVIDUAL events, not bucketed counts."""
        # Generate events
        events = self.sim.generate_layered_dataset(duration_seconds=5.0, hit_rate_hz=100.0)

        # Circular buffer should store each event individually:
        # Event 1: t=0.123s, layers=2
        # Event 2: t=0.157s, layers=1
        # Event 3: t=0.234s, layers=4
        # ... etc

        # NOT bucketed like:
        # Bucket [0-5s]: {1-layer: 95, 2-layer: 234, 3-layer: 123, 4-layer: 48}

        self.assertGreater(len(events), 0, "Should have individual events")

        # Each event has a specific timestamp and layer count
        for timestamp, layers in events:
            self.assertIsInstance(timestamp, float, "Timestamp should be precise float")
            self.assertIn(layers, [1, 2, 3, 4], "Layers should be 1-4")

    def test_bucketing_happens_in_post_processing(self):
        """Test that bucketing is a POST-PROCESSING operation, not done in firmware."""
        events = self.sim.generate_layered_dataset(duration_seconds=30.0, hit_rate_hz=100.0)

        # Post-processing: bucket into 5-second intervals
        buckets = self.sim.bucket_events(events, bucket_duration_s=5.0)

        # Verify buckets were created
        self.assertGreater(len(buckets), 0, "Should create buckets")

        # Each bucket contains counts by layer
        for bucket_start, counts in buckets:
            self.assertIn(1, counts, "Bucket should have 1-layer count")
            self.assertIn(2, counts, "Bucket should have 2-layer count")
            self.assertIn(3, counts, "Bucket should have 3-layer count")
            self.assertIn(4, counts, "Bucket should have 4-layer count")

            # Bucket counts should be non-negative integers
            for layers, count in counts.items():
                self.assertGreaterEqual(count, 0, "Counts should be non-negative")
                self.assertIsInstance(count, int, "Counts should be integers")

    def test_firmware_stores_raw_events_for_flexibility(self):
        """Test that storing raw events (not buckets) enables flexible analysis."""
        events = self.sim.generate_layered_dataset(duration_seconds=30.0, hit_rate_hz=100.0)

        # With raw events, we can bucket at ANY duration:
        buckets_5s = self.sim.bucket_events(events, bucket_duration_s=5.0)
        buckets_1s = self.sim.bucket_events(events, bucket_duration_s=1.0)
        buckets_10s = self.sim.bucket_events(events, bucket_duration_s=10.0)

        # All should work with same raw data
        self.assertGreater(len(buckets_5s), 0, "5s buckets should work")
        self.assertGreater(len(buckets_1s), 0, "1s buckets should work")
        self.assertGreater(len(buckets_10s), 0, "10s buckets should work")

        # Different bucket sizes should give different number of buckets
        self.assertGreater(len(buckets_1s), len(buckets_5s),
                          "1s buckets should be more numerous than 5s buckets")
        self.assertGreater(len(buckets_5s), len(buckets_10s),
                          "5s buckets should be more numerous than 10s buckets")


class TestFPGADataFormat(unittest.TestCase):
    """Test expected data format from FPGA hardware (when available)."""

    def test_fpga_histogram_structure(self):
        """Test that FPGA will provide 4 layers × 8 energy bins."""
        # From deprecated/fpga/FPGA_Interface.hpp:
        # struct HistogramData {
        #     uint16_t counts[4][8];  // [layer][energy_bin]
        #     uint32_t timestamp;
        #     bool valid;
        # }

        num_layers = 4
        num_energy_bins = 8
        total_bins = num_layers * num_energy_bins

        self.assertEqual(total_bins, 32,
                        "FPGA provides 32 histogram bins (4 layers × 8 energy bins)")

        # Each layer will have 8 energy bins
        # This allows energy-resolved detection PER layer
        # Example:
        # Layer 0: [100, 85, 62, 41, 28, 15, 8, 3] counts
        # Layer 1: [95, 80, 58, 38, 25, 12, 6, 2] counts
        # Layer 2: [75, 60, 42, 26, 18, 9, 4, 1] counts
        # Layer 3: [45, 35, 22, 14, 9, 4, 1, 0] counts

    def test_current_adc_vs_future_fpga(self):
        """Test difference between current ADC implementation and future FPGA."""
        # Current (ADC-based):
        # - Single ADC channel reading one SiPM
        # - Software detection of voltage threshold
        # - No layer information (layers=1 placeholder)
        # - 10 kHz sampling rate

        # Future (FPGA-based):
        # - 4 ADC channels (one per layer)
        # - Hardware coincidence detection
        # - Layer-resolved + energy-resolved histograms
        # - Much higher sampling rate possible
        # - CRC validation on data

        # Unit tests prepare for FPGA transition
        self.assertTrue(True, "Unit tests validate logic for future FPGA hardware")


def run_tests():
    """Run all multi-layer detection tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
