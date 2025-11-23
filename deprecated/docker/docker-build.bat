@echo off
REM Docker-based build script for AERIS SEEs Software
REM
REM This script builds the firmware using Docker, so you don't need to install
REM PlatformIO or any dependencies on your host system. Just install Docker!
REM
REM Works on: Windows, Mac, Linux - anywhere Docker runs

echo Building AERIS SEEs firmware using Docker...
echo.

REM Build the Docker image (only needs to happen once, or when dependencies change)
echo Step 1: Building Docker image...
docker build -t aeris-sees .

echo.
echo Step 2: Running PlatformIO build inside container...
REM Run the build, mounting current directory as /workspace
docker run --rm -v "%cd%:/workspace" aeris-sees

echo.
echo Build complete! Firmware available at:
echo   SEEsDriver\.pio\build\teensy41\firmware.hex
