# SEEs Detector Quick Start Guide - DOCKER EDITION

**SEEs** - Solar Energetic Events Payload for AERIS Mission

Interactive command console for the SiPM particle detector.

**THIS GUIDE USES DOCKER - WORKS ON WINDOWS, MAC, AND LINUX!**

---

## Table of Contents
1. [Quick Reference Card](#quick-reference-card) ⭐ START HERE!
2. [What is Docker and Why Use It?](#what-is-docker-and-why-use-it)
3. [Software Installation](#software-installation)
4. [Download the Code](#download-the-code)
5. [Building Firmware with Docker](#building-firmware-with-docker)
6. [Uploading Firmware](#uploading-firmware)
7. [Connecting to the Device](#connecting-to-the-device)
8. [Collecting Data](#taking-measurements)
9. [Troubleshooting](#troubleshooting)
10. [One-Page Cheat Sheet](#one-page-cheat-sheet-print-this) 📄 PRINT THIS!

---

## Quick Reference Card

**⭐ COMPLETE BEGINNER? Read this entire section first, then follow the detailed steps below!**

### What You're Going to Do (The Big Picture)

1. **Install Docker** on your computer (ONE program instead of many!)
2. **Download the code** from the internet
3. **Build the firmware** using Docker (Docker handles all the complicated stuff)
4. **Upload the firmware** to the Teensy
5. **Connect and collect data** (same as regular method)

### What Makes Docker Different?

**Traditional way:**
- Install Python ❌
- Install Visual Studio Code ❌
- Install PlatformIO ❌
- Install Git ❌
- Install libraries ❌
- Hope everything works together ❌

**Docker way:**
- Install Docker ✅
- Download code ✅
- Run one command ✅
- Everything just works! ✅

### What is what?

- **Docker**: A program that runs software in "containers" (like virtual mini-computers)
- **Container**: A pre-configured envirdata point with all the tools already installed
- **Docker Image**: The blueprint for a container (we build this once)
- **Teensy 4.1**: A small circuit board (microcontroller) that controls the detector
- **Spectrometer**: The scientific instrument that detects particle events
- **USB Cable**: Connects the Teensy to your computer (you need a micro-USB cable)
- **Firmware**: The program that runs on the Teensy

### The Absolute Minimum You Need to Know

**To install everything (ONE TIME ONLY):**
1. Install Docker Desktop
2. Download the code (using git or the GitHub website)
3. Build the Docker image (happens automatically on first build)

**To build firmware for the Teensy:**
1. Open terminal/command prompt
2. Navigate to the project folder
3. Run `./docker-build.sh` (Mac/Linux) or `docker-build.bat` (Windows)
4. Wait for success!

**To upload and use (same as normal method):**
1. Open the project in VS Code (or use command line tools)
2. Upload the firmware to Teensy
3. Connect and collect data using SEEs.bat or SEEs.sh

---

## What is Docker and Why Use It?

### The Problem Without Docker

When you develop software, you need to install many tools on your computer:
- Python (specific version)
- PlatformIO (build system)
- Libraries and dependencies
- Git
- And hope they all work together!

**Different computers = different problems:**
- "It works on my machine!" 🤷
- Windows vs Mac vs Linux compatibility issues
- Version conflicts
- Missing dependencies

### The Solution With Docker

Docker creates a **virtual envirdata point** that:
- ✅ Has ALL tools pre-installed
- ✅ Uses the EXACT same setup on every computer
- ✅ Works identically on Windows, Mac, and Linux
- ✅ Doesn't mess with your computer's other software
- ✅ Can be deleted cleanly when you're done

**Think of it like this:**
- Normal way = Build a workshop in your garage (install everything on your computer)
- Docker way = Rent a fully-equipped workshop that arrives in a truck (container)

### What You Still Need on Your Computer

**For building firmware (Docker handles everything else):**
- Docker Desktop ← Only this!

**For uploading firmware and using the device:**
- Teensy Loader (comes with Teensyduino) OR Visual Studio Code + PlatformIO extension
- Python (for the SEEs console scripts)
- USB drivers (usually automatic)

---

## Software Installation

### Step 1: Install Docker Desktop

**Part A: Download Docker Desktop**

**FOR WINDOWS:**

1. **Open your web browser**
2. **Type in address bar**: `https://www.docker.com/products/docker-desktop`
3. **Press Enter**
4. **Click** the big button that says **"Download for Windows"**
5. **Wait** for download to complete (about 500 MB, takes 2-10 minutes)

**FOR MAC:**

1. **Open your web browser**
2. **Type in address bar**: `https://www.docker.com/products/docker-desktop`
3. **Press Enter**
4. **Click** the button for your Mac type:
   - **Apple Silicon** (M1, M2, M3 chips - newer Macs)
   - **Intel Chip** (older Macs)
   - Not sure? Click the Apple menu → About This Mac → look at "Chip" or "Processor"
5. **Wait** for download to complete

**FOR LINUX:**

1. **Open your web browser**
2. **Type in address bar**: `https://docs.docker.com/desktop/install/linux-install/`
3. **Choose your Linux distribution** (Ubuntu, Fedora, etc.)
4. **Follow** the specific instructions for your system

**Part B: Install Docker Desktop**

**WINDOWS:**

1. **Look at the bottom** of your browser - find the downloaded file
   - Named something like `Docker Desktop Installer.exe`
2. **Double-click** the downloaded file
3. A window asks **"Do you want to allow this app to make changes?"** - Click **"Yes"**
4. Docker Desktop installer opens
5. **Check** the box that says **"Use WSL 2 instead of Hyper-V"** (recommended)
6. **Click** "OK" or "Install"
7. **WAIT PATIENTLY** - installation takes 3-10 minutes
   - You'll see a progress bar
   - Your computer might seem slow - this is normal
8. When installation completes, you'll see **"Installation succeeded"**
9. **Click** "Close and restart" (your computer will restart)
10. **Wait** for your computer to restart (1-2 minutes)

**After restart:**

11. **Docker Desktop will open automatically** (wait 30-60 seconds)
12. You might see a tutorial - you can **skip it** (click "Skip tutorial")
13. **Look for** the Docker whale icon in your system tray (bottom-right on Windows)
   - If the whale is animated (moving), Docker is still starting - wait
   - If the whale is still, Docker is ready!

**MAC:**

1. **Open Finder**
2. **Go to Downloads** folder
3. **Find** the file `Docker.dmg`
4. **Double-click** `Docker.dmg`
5. **A window opens** showing a Docker icon and Applications folder
6. **Drag** the Docker icon to the Applications folder
7. **Wait** for it to copy (10-30 seconds)
8. **Open Launchpad** (rocket icon in Dock)
9. **Find and click** "Docker" icon
10. **A security warning appears** - Click "Open"
11. **Enter your Mac password** when prompted
12. **Docker Desktop starts** - this takes 30-60 seconds
13. **Complete the setup wizard** (click through defaults)
14. **Look for** the Docker whale icon in your menu bar (top-right)
    - When it offs animating, Docker is ready!

**LINUX (Ubuntu/Debian example):**

Most Linux users are comfortable with the terminal. Here's the quick version:

```bash
# Update package list
sudo apt-get update

# Install Docker
sudo apt-get install docker.io

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
```

For other distros or Docker Desktop on Linux, follow: https://docs.docker.com/desktop/install/linux-install/

**Part C: Verify Docker Works**

**WINDOWS & MAC:**

1. **Open Terminal/Command Prompt:**
   - **Windows**: Press `Windows Key + R`, type `cmd`, press Enter
   - **Mac**: Press `Cmd + Space`, type `terminal`, press Enter
2. **A black/white window appears**
3. **Type exactly**: `docker --version`
4. **Press Enter**
5. **You should see**: `Docker version 24.x.x` (numbers may vary)
   - If you see this, **SUCCESS!** Docker is installed!
   - If you see "command not found" - Docker isn't installed correctly, try reinstalling

**LINUX:**

```bash
docker --version
```

Should show Docker version. If you get "permission denied", make sure you logged out and back in after adding yourself to the docker group.

---

## Download the Code

You have two options: Use Git (recommended) or download a ZIP file.

### Option 1: Using Git (Recommended)

**Part A: Install Git (if you don't have it)**

**WINDOWS:**
1. Go to: `https://git-scm.com/download/win`
2. Download will start automatically
3. Run the installer
4. Click "Next" through all the screens (defaults are fine)
5. Click "Install" and wait
6. Click "Finish"

**MAC:**
1. Open Terminal (`Cmd + Space`, type `terminal`, press Enter)
2. Type: `git --version`
3. If Git isn't installed, macOS will prompt you to install it automatically - click "Install"

**LINUX:**
```bash
sudo apt-get install git  # Ubuntu/Debian
sudo yum install git       # Fedora/CentOS
```

**Part B: Clone the Repository**

**WINDOWS:**
1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. **Navigate to where you want the code**:
   ```
   cd Desktop
   ```
   (You can also use `cd Documents` or any other location)
4. **Type exactly**:
   ```
   git clone https://github.com/hsfl/aeris-sees-software.git
   ```
5. Press Enter
6. **Wait** while the code downloads (30-60 seconds)
7. You'll see messages about "Cloning into..."
8. When done, you'll see the command prompt again
9. **SUCCESS!** Code is downloaded to Desktop\aeris-sees-software

**MAC & LINUX:**
1. Open Terminal
2. Navigate to where you want the code:
   ```bash
   cd ~/Desktop
   ```
   (Or `cd ~/Documents` or wherever you prefer)
3. Clone the repository:
   ```bash
   git clone https://github.com/hsfl/aeris-sees-software.git
   ```
4. Wait for download to complete
5. **SUCCESS!** Code is in ~/Desktop/aeris-sees-software

### Option 2: Download ZIP (Easier but not recommended for updates)

1. **Open web browser**
2. **Go to**: `https://github.com/hsfl/aeris-sees-software`
3. **Click** the green **"Code"** button
4. **Click** "Download ZIP"
5. **Wait** for download
6. **Find** the downloaded ZIP file in your Downloads folder
7. **Right-click** the ZIP file
8. **Click** "Extract All..." (Windows) or "Open" (Mac)
9. **Choose** where to extract (Desktop or Documents)
10. **Click** "Extract" (Windows) or the files will extract automatically (Mac)

---

## Building Firmware with Docker

This is where Docker shines - ONE COMMAND builds everything!

### Step 1: Open Terminal in Project Folder

**WINDOWS:**

**Method A - Using File Explorer (EASIEST):**
1. **Open File Explorer** (Windows Key + E)
2. **Navigate** to where you downloaded the code
   - Example: `Desktop\aeris-sees-software`
3. **You should see** files like: `Dockerfile`, `README.md`, `SEEs.sh`, etc.
4. **Click** in the **address bar** at the top (where the path shows)
5. **Type**: `cmd`
6. **Press Enter**
7. **A black command window opens** - you're in the right place!

**Method B - Using Command Prompt:**
1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. Type: `cd Desktop\aeris-sees-software` (or wherever you saved it)
4. Press Enter

**MAC & LINUX:**

1. **Open Terminal**
   - **Mac**: Cmd + Space, type "terminal", press Enter
   - **Linux**: Ctrl + Alt + T
2. **Navigate to project folder**:
   ```bash
   cd ~/Desktop/aeris-sees-software
   ```
   (Change path to wherever you saved it)
3. **Verify you're in the right place**:
   ```bash
   ls
   ```
   You should see: `Dockerfile`, `README.md`, `SEEsDriver`, etc.

### Step 2: Build the Firmware

**WINDOWS:**

1. **In the Command Prompt window**, type exactly:
   ```
   docker-build.bat
   ```
2. **Press Enter**
3. **WAIT AND WATCH** - this is a multi-stage process!

**First time you run this (takes 5-15 minutes):**
- Docker downloads Ubuntu 22.04 image (~80 MB)
- Installs Python, PlatformIO, and all dependencies
- Builds the firmware
- Shows LOTS of text scrolling by - this is normal!

**Future builds (takes 1-2 minutes):**
- Docker uses cached image (already has everything installed)
- Just builds the firmware
- Much faster!

4. **WATCH FOR**:
   - "Step 1: Building Docker image..." (first time only - takes several minutes)
   - "Step 2: Running PlatformIO build inside container..."
   - Lots of text about compiling, linking, etc.
   - **Final line**: `Build complete! Firmware available at:`
   - **If you see this**: `SEEsDriver/.pio/build/teensy41/firmware.hex`
   - **SUCCESS!**

**MAC & LINUX:**

1. **Make the script executable** (first time only):
   ```bash
   chmod +x docker-build.sh
   ```
2. **Run the build script**:
   ```bash
   ./docker-build.sh
   ```
3. **Wait and watch** (same as Windows above)
4. **Look for success message**

### Step 3: Verify the Build

**ALL PLATFORMS:**

After the build completes, verify the firmware file exists:

**WINDOWS:**
```
dir SEEsDriver\.pio\build\teensy41\firmware.hex
```

**MAC & LINUX:**
```bash
ls -lh SEEsDriver/.pio/build/teensy41/firmware.hex
```

**You should see**:
- A file named `firmware.hex`
- Size around 200-500 KB
- Recent timestamp (just now)

If you see this file, **PERFECT!** The build worked!

### What Just Happened?

Docker just:
1. ✅ Created a virtual Linux envirdata point (Ubuntu 22.04)
2. ✅ Installed Python 3.x
3. ✅ Installed PlatformIO build system
4. ✅ Installed all required libraries
5. ✅ Compiled your code
6. ✅ Generated firmware.hex file
7. ✅ Copied it back to your computer

**And you didn't have to install ANY of that on your computer!**

The Docker container is like a temporary workshop that appears, builds your firmware, and disappears - leaving only the finished product.

---

## Uploading Firmware

**IMPORTANT**: Docker built the firmware, but it **CANNOT** upload to the Teensy directly. This is because Docker containers don't have direct access to USB devices on Windows/Mac.

You have two options for uploading:

### Option 1: Using Visual Studio Code + PlatformIO (Recommended)

This is the same as the regular method. Follow the **"Building and Uploading Firmware"** section in the main [QUICKSTART.md](QUICKSTART.md) document, but **SKIP the build step** (Docker already did that!).

Quick summary:
1. Install Visual Studio Code
2. Install PlatformIO extension
3. Open the `SEEsDriver` folder in VS Code
4. Plug in Teensy sees USB
5. Click the Upload button (→ arrow) at the bottom
6. Wait for success!

### Option 2: Using Teensy Loader (Command Line)

**This is advanced - only if you're comfortable with command-line tools.**

1. Install Teensyduino from: `https://www.pjrc.com/teensy/td_download.html`
2. Plug in Teensy sees USB
3. Open Teensy Loader application
4. File → Open HEX File → Select `SEEsDriver/.pio/build/teensy41/firmware.hex`
5. Press the button on the Teensy
6. Teensy Loader uploads automatically
7. Done!

---

## Connecting to the Device

**This section is IDENTICAL to the regular method.**

Please follow the **"Connecting to the Device"** section in [QUICKSTART.md](QUICKSTART.md).

Quick summary:
- **Windows**: Run `SEEs.bat` in the SEEsDriver folder
- **Mac/Linux**: Run `./SEEs.sh` in the project root
- Find your COM/serial port
- Connect and start collecting data!

---

## Collecting Data

**This section is IDENTICAL to the regular method.**

Please follow the **"Collecting Data" section in [QUICKSTART.md](QUICKSTART.md).

Quick commands:
- `help` - Show available commands
- `off` - Stop data collection
- `on` - Take a single data point
- `snap` - Take measurements every 60 seconds
- `off` - Stop automatic measurements

---

## Troubleshooting

### Docker-Specific Issues

#### Problem: "Docker is not recognized" or "command not found"

**Docker isn't installed or isn't running.**

**Solution:**
1. Make sure Docker Desktop is installed
2. **Look for the Docker whale icon**:
   - **Windows**: System tray (bottom-right, might be hidden - click the up arrow)
   - **Mac**: Menu bar (top-right)
   - **Linux**: Check if Docker service is running: `sudo systemctl off docker`
3. If you don't see the whale icon, **open Docker Desktop**:
   - **Windows**: Start menu → Docker Desktop
   - **Mac**: Launchpad → Docker
4. **Wait** for Docker to start (30-60 seconds)
5. Try the build command again

#### Problem: "Cannot connect to Docker daemon"

**Docker Desktop isn't running.**

**Solution:**
1. **Open Docker Desktop application**
2. **Wait** for it to fully start (watch for the whale icon to off animating)
3. Try again

#### Problem: Docker build is VERY slow or hangs

**First build is always slow - be patient!**

**Solution:**
1. **First build takes 5-15 minutes** - this is normal!
   - Docker downloads Ubuntu image
   - Installs Python and PlatformIO
   - Downloads libraries
2. **Make sure you have internet connection**
3. **Make sure you have disk space** (need ~2-3 GB free)
4. **Check Docker Desktop** settings:
   - Windows: Make sure WSL 2 is enabled (Settings → General)
   - Mac: Increase resources (Settings → Resources)
5. **If it truly hangs** (no output for 10+ minutes):
   - Press Ctrl+C to cancel
   - Run: `docker system prune` to clean up
   - Try building again

#### Problem: "permission denied" (Linux only)

**Your user isn't in the docker group.**

**Solution:**
```bash
# Add yourself to docker group
sudo usermod -aG docker $USER

# Log out and log back in
# Or run:
newgrp docker

# Try again
./docker-build.sh
```

#### Problem: Build succeeds but firmware.hex is missing

**The build might have failed silently.**

**Solution:**
1. Read the build output carefully - look for errors
2. Try running the build again with verbose output:
   ```bash
   docker run --rm -v "$(pwd):/workspace" aeris-sees -v
   ```
3. Check if the `.pio` directory was created:
   - Windows: `dir SEEsDriver\.pio`
   - Mac/Linux: `ls -la SEEsDriver/.pio`

#### Problem: "Error response from daemon: invalid mount config"

**Path issues with Windows.**

**Solution (Windows):**
1. Make sure you're running from Command Prompt (cmd), not PowerShell
2. Or try with full path:
   ```
   docker run --rm -v "%cd%:/workspace" aeris-sees
   ```

#### Problem: Want to rebuild from scratch

**Clear Docker cache and rebuild.**

**Solution:**
```bash
# Remove the Docker image
docker rmi aeris-sees

# Clean Docker cache (optional - frees disk space)
docker system prune

# Build again
./docker-build.sh  # Mac/Linux
docker-build.bat   # Windows
```

### General Issues

**For all other problems** (uploading, connecting, collecting data, etc.), please see the **Troubleshooting** section in [QUICKSTART.md](QUICKSTART.md).

Common issues:
- Can't find COM port
- Upload failed
- No output in console
- Commands don't work
- Can't find CSV files

All of these are covered in detail in the main quick start guide.

---

## One-Page Cheat Sheet (Print This!)

### Docker Quick Start - Daily Use

**1. Build Firmware (when you need to update):**
```bash
# Windows
cd Desktop\aeris-sees-software
docker-build.bat

# Mac/Linux
cd ~/Desktop/aeris-sees-software
./docker-build.sh
```

**2. Upload Firmware:**
- Open VS Code
- Open `SEEsDriver` folder
- Click Upload button (→)
- OR use Teensy Loader

**3. Collect Data:**
```bash
# Windows (from repo root)
.\SEEs.bat

# Mac/Linux (from repo root)
./SEEs.sh
```

**4. Commands:**
- `on` - Start data collection
- `snap` - Capture ±2.5s window
- `off` - Stop data collection

### Docker Commands Reference

| Command | What It Does |
|---------|-------------|
| `docker --version` | Check if Docker is installed |
| `docker images` | List downloaded images |
| `docker ps` | List running containers |
| `docker system prune` | Clean up old containers/images |
| `docker rmi aeris-sees` | Delete the build image (to rebuild from scratch) |

### File Locations

**Firmware output:**
- `SEEsDriver/.pio/build/teensy41/firmware.hex`

**Collected data:**
- Windows: `C:\Users\YourName\sees_outputlogs\YYYYMMDD.HHMM\`
- Mac/Linux: `~/sees_outputlogs/YYYYMMDD.HHMM/`

### Advantages of Docker Method

✅ Same build environment on all computers
✅ No version conflicts
✅ No "it works on my machine" problems
✅ Easy to clean up (just delete the Docker image)
✅ Doesn't pollute your system with build tools
✅ Perfect for teams (everyone uses same setup)

### When to Use Docker vs. Regular Method

**Use Docker if:**
- You work on multiple computers
- You don't want to install lots of development tools
- You're part of a team and need consistent builds
- You're on a shared/managed computer

**Use Regular Method if:**
- You're actively developing/debugging code
- You need to build frequently (regular is faster after initial setup)
- You want to use VS Code's full debugging features
- You're already familiar with PlatformIO

### Common Problems Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Docker not recognized | Open Docker Desktop, wait for it to start |
| Build very slow | First build takes 5-15 min - be patient! |
| Permission denied (Linux) | Add self to docker group: `sudo usermod -aG docker $USER` |
| Build fails | Read error messages, check internet connection |
| Can't upload | Docker can't upload - use VS Code or Teensy Loader |

### Important Links

- **Docker Desktop**: `https://www.docker.com/products/docker-desktop`
- **Main Documentation**: See [QUICKSTART.md](QUICKSTART.md) for detailed instructions
- **Repository**: `https://github.com/hsfl/aeris-sees-software`
- **Teensy Info**: `https://www.pjrc.com/teensy/`

---

**AERIS SEEs Payload Team** - 2025
