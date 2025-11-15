# AERIS SEEs Software - Docker Build Environment
# Mimics Pop!OS 22.04 where everything "just works"
#
# Usage:
#   docker build -t aeris-sees .
#   docker run --rm -v $(pwd):/workspace aeris-sees
#
# This builds the PlatformIO firmware just like on native Pop!OS 22.04

FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (matching Pop!OS 22.04 base)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    udev \
    && rm -rf /var/lib/apt/lists/*

# Install PlatformIO Core
RUN pip3 install --no-cache-dir platformio

# Install Python dependencies for SEEs scripts
COPY SEEsDriver/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Set working directory
WORKDIR /workspace

# Default command: run PlatformIO build for SEEsDriver
CMD ["pio", "run", "-d", "SEEsDriver"]
