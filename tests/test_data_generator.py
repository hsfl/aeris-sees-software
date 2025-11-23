#!/usr/bin/env python3
"""
SEES Test Data Generator

Generates realistic simulated particle detector data for testing.
Simulates SiPM detector output with particle hit events.

Data format: time_ms,voltage_V,hit,cum_counts

Usage:
    python3 test_data_generator.py [--output FILE] [--duration SECONDS]
"""

import random
import math
import csv
from pathlib import Path
import argparse


class ParticleDetectorSimulator:
    """
    Simulates 4-layer scintillator stack for cosmic ray detection.

    The detector has 4 layers (0, 1, 2, 3) stacked vertically.
    Particles enter from the top and penetrate downward through the stack.

    COINCIDENCE DETECTION:
    Because layers are stacked, a particle reaching layer N lights up ALL layers 0 through N.
    This is a coincidence telescope - measuring penetration depth to determine energy.

    Coincidence patterns (what lights up):
    - 1-layer: Layer 0 only (low energy, stopped in first layer)
    - 2-layer: Layers 0 AND 1 (typical cosmic ray, penetrated to layer 1)
    - 3-layer: Layers 0, 1, AND 2 (high energy, penetrated to layer 2)
    - 4-layer: Layers 0, 1, 2, AND 3 (very high energy, penetrated entire stack)

    Data is bucketed into 5-second intervals for telemetry.
    Each bucket contains counts of 1-layer, 2-layer, 3-layer, and 4-layer events.
    """

    def __init__(self, seed=42, num_layers=4):
        """
        Initialize 4-layer detector simulator.

        Args:
            seed: Random seed for reproducibility
            num_layers: Number of scintillator layers (default 4)
        """
        self.seed = seed
        self.rng = random.Random(seed)
        self.num_layers = num_layers

        # Sampling parameters (for ADC simulation)
        self.sample_rate_hz = 10000  # 10 kHz sampling
        self.sample_period_ms = 1000.0 / self.sample_rate_hz  # 0.1 ms

        # Detection parameters
        self.baseline_v = 0.100
        self.noise_level_v = 0.010
        self.pulse_peak_v = 0.500
        self.pulse_width_ms = 0.5
        self.hit_threshold_v = 0.30
        self.hit_ceiling_v = 0.80
        self.refractory_period_ms = 0.3

        # Temporal parameters
        self.coincidence_window_ms = 0.010  # 10 µs coincidence window
        self.bucket_duration_s = 5.0  # 5-second telemetry buckets

        # Layer penetration probabilities (for cosmic rays)
        # Higher energy → more layers penetrated
        self.layer_penetration_probs = {
            1: 0.20,  # 20% single-layer (edge hits, low energy)
            2: 0.45,  # 45% two-layer (typical cosmic rays)
            3: 0.25,  # 25% three-layer (high energy)
            4: 0.10,  # 10% four-layer (very high energy)
        }

    def generate_baseline_noise(self):
        """Generate baseline voltage with Gaussian noise."""
        return self.baseline_v + self.rng.gauss(0, self.noise_level_v)

    def generate_particle_pulse(self, time_in_pulse_ms):
        """
        Generate particle pulse shape (Gaussian-like).

        Args:
            time_in_pulse_ms: Time since pulse start (ms)

        Returns:
            Voltage value for this point in the pulse
        """
        # Gaussian pulse centered at pulse_width/2
        center = self.pulse_width_ms / 2
        sigma = self.pulse_width_ms / 4

        amplitude = self.pulse_peak_v * self.rng.uniform(0.8, 1.2)  # Vary amplitude
        pulse_value = amplitude * ((2.71828 ** (-((time_in_pulse_ms - center) ** 2) / (2 * sigma ** 2))))

        # Add baseline
        return self.baseline_v + pulse_value

    def generate_dataset(self, duration_seconds=10.0, hit_rate_hz=5.0):
        """
        Generate a realistic dataset with particle hits.

        Args:
            duration_seconds: Total duration to simulate
            hit_rate_hz: Average particle hit rate (hits per second)

        Returns:
            List of data points: [(time_ms, voltage_V, hit, cum_counts), ...]
        """
        data = []
        current_time_ms = 0.0
        cumulative_counts = 0

        # Generate random hit times using Poisson process
        hit_times = []
        if hit_rate_hz > 0:  # Only generate hits if rate > 0
            t = 0.0
            while t < duration_seconds * 1000:  # Convert to ms
                # Exponential inter-arrival time (Poisson process)
                u = self.rng.random()
                interval = -1000 * (1.0 / hit_rate_hz) * math.log(u) if u > 0 else float('inf')
                t += interval
                if t < duration_seconds * 1000:
                    hit_times.append(t)

        hit_times.sort()
        hit_index = 0
        current_pulse_start = None
        last_hit_time = -999999  # Initialize far in past

        # Generate samples
        num_samples = int(duration_seconds * self.sample_rate_hz)
        for i in range(num_samples):
            current_time_ms = i * self.sample_period_ms

            # Check if we should start a new pulse
            if (hit_index < len(hit_times) and
                current_time_ms >= hit_times[hit_index] and
                current_pulse_start is None and
                current_time_ms - last_hit_time >= self.refractory_period_ms):

                current_pulse_start = current_time_ms
                hit_index += 1

            # Generate voltage
            if current_pulse_start is not None:
                time_in_pulse = current_time_ms - current_pulse_start

                if time_in_pulse < self.pulse_width_ms:
                    # We're in a pulse
                    voltage = self.generate_particle_pulse(time_in_pulse)
                else:
                    # Pulse ended
                    current_pulse_start = None
                    voltage = self.generate_baseline_noise()
            else:
                # Baseline
                voltage = self.generate_baseline_noise()

            # Detect hit (voltage in detection window)
            hit = 1 if self.hit_threshold_v <= voltage <= self.hit_ceiling_v else 0

            # Update cumulative counts (only count first sample of hit due to refractory period)
            if hit and (not data or data[-1][2] == 0):  # Rising edge
                cumulative_counts += 1
                last_hit_time = current_time_ms

            # Store data point
            data.append((current_time_ms, voltage, hit, cumulative_counts))

        return data

    def generate_quiet_period(self, duration_seconds=5.0):
        """Generate data with no hits (baseline only)."""
        return self.generate_dataset(duration_seconds, hit_rate_hz=0.0)

    def generate_burst(self, duration_seconds=2.0, hit_rate_hz=50.0):
        """Generate data with high hit rate (particle burst)."""
        return self.generate_dataset(duration_seconds, hit_rate_hz=hit_rate_hz)

    def generate_coincidence_event(self, timestamp_s):
        """
        Generate a multi-layer coincidence event.

        Returns number of layers penetrated (1-4) based on energy distribution.
        """
        # Weighted random choice for number of layers
        rand = self.rng.random()
        cumulative = 0.0
        for layers, prob in sorted(self.layer_penetration_probs.items()):
            cumulative += prob
            if rand <= cumulative:
                return layers, timestamp_s
        return 4, timestamp_s  # Fallback to max layers

    def generate_layered_dataset(self, duration_seconds=30.0, hit_rate_hz=100.0):
        """
        Generate cosmic ray detection data with layer coincidence.

        Args:
            duration_seconds: Total duration to simulate
            hit_rate_hz: Average cosmic ray hit rate (hits per second)

        Returns:
            List of events: [(timestamp_s, num_layers), ...]
        """
        events = []

        # Generate random hit times using Poisson process
        if hit_rate_hz > 0:
            t = 0.0
            while t < duration_seconds:
                # Exponential inter-arrival time (Poisson process)
                u = self.rng.random()
                interval = -(1.0 / hit_rate_hz) * math.log(u) if u > 0 else float('inf')
                t += interval
                if t < duration_seconds:
                    num_layers, _ = self.generate_coincidence_event(t)
                    events.append((t, num_layers))

        return events

    def bucket_events(self, events, bucket_duration_s=5.0):
        """
        Bucket events into time intervals and count by layer.

        Args:
            events: List of (timestamp_s, num_layers) tuples
            bucket_duration_s: Bucket size in seconds (default 5.0s)

        Returns:
            List of buckets: [(bucket_start_s, counts_by_layer), ...]
            where counts_by_layer = {1: count, 2: count, 3: count, 4: count}
        """
        if not events:
            return []

        # Find time range
        max_time = max(t for t, _ in events)
        num_buckets = int(math.ceil(max_time / bucket_duration_s))

        # Initialize buckets
        buckets = []
        for i in range(num_buckets):
            bucket_start = i * bucket_duration_s
            counts = {1: 0, 2: 0, 3: 0, 4: 0}
            buckets.append((bucket_start, counts))

        # Fill buckets
        for timestamp, num_layers in events:
            bucket_idx = int(timestamp / bucket_duration_s)
            if bucket_idx < len(buckets):
                buckets[bucket_idx][1][num_layers] += 1

        return buckets

    def extract_snap_window(self, buckets, snap_time_s, window_seconds=2.5):
        """
        Extract ±2.5s window around a snap event from bucketed data.

        This simulates extracting data from a 30-second circular buffer.
        The snap window captures all buckets that overlap with [snap-2.5s, snap+2.5s].

        Args:
            buckets: List of (bucket_start_s, counts_by_layer)
            snap_time_s: Snap timestamp in seconds
            window_seconds: Window size before and after snap (default 2.5s)

        Returns:
            List of buckets in the snap window (buckets that overlap with the time window)
        """
        if not buckets:
            return []

        bucket_duration = buckets[1][0] - buckets[0][0] if len(buckets) > 1 else 5.0

        window_start = snap_time_s - window_seconds
        window_end = snap_time_s + window_seconds

        # Extract buckets that overlap with the snap window
        snap_window = []
        for bucket_start, counts in buckets:
            bucket_end = bucket_start + bucket_duration
            # Include bucket if it overlaps with [window_start, window_end]
            if bucket_end > window_start and bucket_start < window_end:
                snap_window.append((bucket_start, counts))

        return snap_window


def write_csv(data, output_file):
    """Write data to CSV file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['time_ms', 'voltage_V', 'hit', 'cum_counts'])

        for time_ms, voltage, hit, cum_counts in data:
            writer.writerow([f"{time_ms:.1f}", f"{voltage:.4f}", hit, cum_counts])

    print(f"✅ Generated {len(data)} samples → {output_file}")


def main():
    """Generate test datasets."""
    parser = argparse.ArgumentParser(description='Generate SEES test data')
    parser.add_argument('--output', '-o', default='test_data/sees_test.csv',
                        help='Output CSV file (default: test_data/sees_test.csv)')
    parser.add_argument('--duration', '-d', type=float, default=10.0,
                        help='Duration in seconds (default: 10.0)')
    parser.add_argument('--hit-rate', '-r', type=float, default=5.0,
                        help='Hit rate in Hz (default: 5.0)')
    parser.add_argument('--seed', '-s', type=int, default=42,
                        help='Random seed (default: 42)')

    args = parser.parse_args()

    # Create simulator
    sim = ParticleDetectorSimulator(seed=args.seed)

    # Generate data
    print(f"Generating {args.duration}s of data at {args.hit_rate} hits/s...")
    data = sim.generate_dataset(args.duration, args.hit_rate)

    # Write to file
    write_csv(data, args.output)

    # Print statistics
    total_hits = data[-1][3] if data else 0
    print(f"📊 Statistics:")
    print(f"   Duration: {args.duration}s")
    print(f"   Samples: {len(data)}")
    print(f"   Total hits: {total_hits}")
    print(f"   Actual rate: {total_hits / args.duration:.1f} hits/s")


if __name__ == "__main__":
    main()

