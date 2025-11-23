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
import csv
from pathlib import Path
import argparse


class ParticleDetectorSimulator:
    """
    Simulates SiPM particle detector data with realistic hit patterns.

    Detection parameters:
    - Sampling rate: 10 kHz (100 µs per sample)
    - Detection window: 0.30V - 0.80V
    - Baseline: ~0.1V with noise
    - Particle pulses: ~0.5V peak, 300 µs width
    """

    def __init__(self, seed=42):
        """
        Initialize detector simulator.

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        self.rng = random.Random(seed)

        # ADC parameters
        self.sample_rate_hz = 10000  # 10 kHz
        self.sample_period_ms = 1000.0 / self.sample_rate_hz  # 0.1 ms

        # Detection parameters
        self.baseline_v = 0.1  # Baseline voltage
        self.noise_level_v = 0.02  # Noise amplitude
        self.hit_threshold_v = 0.30  # Hit detection threshold
        self.hit_ceiling_v = 0.80  # Hit upper threshold
        self.refractory_period_ms = 0.3  # 300 µs refractory period

        # Particle pulse parameters
        self.pulse_peak_v = 0.5  # Typical pulse peak
        self.pulse_width_ms = 0.3  # 300 µs pulse width

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
        t = 0.0
        while t < duration_seconds * 1000:  # Convert to ms
            # Exponential inter-arrival time
            interval = -1000 * (1.0 / hit_rate_hz) * self.rng.log(self.rng.random())
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
