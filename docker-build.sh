#!/bin/bash
# Docker-based build script for AERIS SEEs Software
#
# This script builds the firmware using Docker, so you don't need to install
# PlatformIO or any dependencies on your host system. Just install Docker!
#
# Works on: Windows, Mac, Linux - anywhere Docker runs

set -e

echo "Building AERIS SEEs firmware using Docker..."
echo

# Build the Docker image (only needs to happen once, or when dependencies change)
echo "Step 1: Building Docker image..."
docker build -t aeris-sees .

echo
echo "Step 2: Running PlatformIO build inside container..."
# Run the build, mounting current directory as /workspace
docker run --rm -v "$(pwd):/workspace" aeris-sees

echo
echo "Build complete! Firmware available at:"
echo "  SEEsDriver/.pio/build/teensy41/firmware.hex"
