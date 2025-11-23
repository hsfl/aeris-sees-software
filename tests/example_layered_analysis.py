#!/usr/bin/env python3
"""
Example: 4-Layer Cosmic Ray Analysis

This script demonstrates what SEEs layer-coincidence analysis should look like.
This is NOT the actual firmware - just an example of the data processing pipeline.

The real implementation will be in the SEEs firmware (C++) and data processing scripts.
"""

from test_data_generator import ParticleDetectorSimulator
import json

def main():
    """Demonstrate layer analysis pipeline."""
    print("=" * 70)
    print("  SEEs 4-LAYER COINCIDENCE DETECTION - EXAMPLE ANALYSIS")
    print("=" * 70)
    print()

    # Create simulator
    sim = ParticleDetectorSimulator(seed=42)

    # Generate 30 seconds of cosmic ray data at 100 Hz
    print("Generating 30s of cosmic ray data at 100 hits/s...")
    events = sim.generate_layered_dataset(duration_seconds=30.0, hit_rate_hz=100.0)
    print(f"✅ Generated {len(events)} cosmic ray events")
    print()

    # Bucket into 5-second intervals
    print("Bucketing into 5-second telemetry intervals...")
    buckets = sim.bucket_events(events, bucket_duration_s=5.0)
    print(f"✅ Created {len(buckets)} buckets")
    print()

    # Display bucket statistics
    print("TELEMETRY BUCKETS:")
    print("-" * 70)
    print(f"{'Time (s)':>10} | {'1-Layer':>8} | {'2-Layer':>8} | {'3-Layer':>8} | {'4-Layer':>8} | {'Total':>8}")
    print("-" * 70)

    for bucket_start, counts in buckets:
        total = sum(counts.values())
        print(f"{bucket_start:>10.1f} | {counts[1]:>8} | {counts[2]:>8} | {counts[3]:>8} | {counts[4]:>8} | {total:>8}")

    print("-" * 70)
    print()

    # Simulate a "snap" at 15 seconds
    snap_time = 15.0
    print(f"SNAP EVENT at t={snap_time}s")
    print("Extracting ±2.5s window (5 seconds total around snap)")
    print()

    snap_window = sim.extract_snap_window(buckets, snap_time, window_seconds=2.5)

    print("SNAP WINDOW DATA:")
    print("-" * 70)
    print(f"{'Time (s)':>10} | {'1-Layer':>8} | {'2-Layer':>8} | {'3-Layer':>8} | {'4-Layer':>8} | {'Total':>8}")
    print("-" * 70)

    for bucket_start, counts in snap_window:
        total = sum(counts.values())
        marker = " ← SNAP" if bucket_start <= snap_time < bucket_start + 5.0 else ""
        print(f"{bucket_start:>10.1f} | {counts[1]:>8} | {counts[2]:>8} | {counts[3]:>8} | {counts[4]:>8} | {total:>8}{marker}")

    print("-" * 70)
    print()

    # Summary statistics
    total_1layer = sum(c[1] for _, c in buckets)
    total_2layer = sum(c[2] for _, c in buckets)
    total_3layer = sum(c[3] for _, c in buckets)
    total_4layer = sum(c[4] for _, c in buckets)
    total_all = total_1layer + total_2layer + total_3layer + total_4layer

    print("MISSION SUMMARY (30s):")
    print(f"  1-layer events: {total_1layer:>4} ({100*total_1layer/total_all:.1f}%)")
    print(f"  2-layer events: {total_2layer:>4} ({100*total_2layer/total_all:.1f}%) ← Typical cosmic rays")
    print(f"  3-layer events: {total_3layer:>4} ({100*total_3layer/total_all:.1f}%) ← High energy")
    print(f"  4-layer events: {total_4layer:>4} ({100*total_4layer/total_all:.1f}%) ← Very high energy")
    print(f"  Total events:   {total_all:>4}")
    print()
    print("=" * 70)
    print()
    print("This demonstrates the data format SEEs firmware should produce:")
    print("  • 5-second telemetry buckets with coincidence-resolved counts")
    print("  • 1-layer = layer 0 only (low energy)")
    print("  • 2-layer = layers 0+1 (typical cosmic ray)")
    print("  • 3-layer = layers 0+1+2 (high energy)")
    print("  • 4-layer = layers 0+1+2+3 (very high energy)")
    print("  • Snap windows: ±2.5s from 30s circular buffer")
    print("  • Integration with VIA's GPIO snap trigger for correlated science")
    print()

if __name__ == "__main__":
    main()
