# AERIS / SEEs Software

## Brief Overview
This is the code repository for the SEEs (Solar Energetic Events) Payload firmware for the AERIS mission. The SEEs payload uses a SiPM-based particle detector connected to a Teensy 4.1 microcontroller.

The firmware handles:
- ADC-based data acquisition from SiPM detector
- Windowed particle detection with hysteresis and refractory logic
- Command console interface via USB Serial
- SD card data buffering for trigger captures
- Live CSV streaming to computer

## System Architecture

```
SiPM Detector (Analog)
         ↓
Teensy 4.1 (SEEs Payload)
    ├─ ADC (A0) - 10 kHz sampling
    ├─ SD Card (rolling buffer)
    ├─ USB Serial (command console + data stream)
    └─ Future: UART → Artemis OBC → Radio

Future FPGA version:
    SiPM → FPGA (histograms) → Teensy → OBC
```

**Current Version:** ADC-based prototype with command control

## Quick Start

**👉 See [QUICKSTART.md](QUICKSTART.md) for complete workflow (unit tests → HIL → flatsat)**

### Run Tests (No Hardware)

```bash
cd tests
./run_all_tests.sh
```

### Hardware Testing

```bash
# Build and upload
cd SEEsDriver
pio run --target upload

# Connect to console
./SEEs.sh

# Commands
SEEs> on
SEEs> snap
SEEs> off
```

### Flatsat (Pi 400)

```bash
ssh pi@192.168.4.163  # Password: aeris
sees && git pull && sees-test && sees-console
```

## Build Instructions
1. Download and install VSCode & GitHub Desktop.
   * VSCode: https://code.visualstudio.com/download
   * GitHub Desktop: https://desktop.github.com/download/
2. Install both the C/C++ and PlatformIO extension in VSCode.
   * PlatformIO: https://platformio.org/install/ide?install=vscode
   * C/C++: https://code.visualstudio.com/docs/languages/cpp
3. Clone the repository from GitHub Desktop by clicking "Add" at the top left, "Clone Repository...", "URL," copying the link below into the prompt, and then clicking Clone.
   * Repository URL: https://github.com/hsfl/aeris-sees-software.git
4. Go to VSCode and initialize the PlatformIO extension.
5. In the "QUICK ACCESS" column, click on "Open" and then "Open Project" in the tab that opens. Locate and choose the "SEEsDriver" folder within the "aeris-sees-software" folder.
   * This should have opened the SEEsDriver folder as a PlatformIO project with all the dependencies and configurations it needs.
6. From the explorer column on the left, navigate the SEEsDriver folder to "src", then to "main.cpp".
7. On the bottom left are multiple buttons; click the checkmark to build the code, confirming a successful build when [SUCCESS] appears on the terminal that pops up.
   * That finishes building the software.

To get relevant data, continue to "Getting Data" section.

## Getting Data with Teensy 4.1

### Hardware Connections
1. **SiPM Detector**: Connect fast-out to Teensy pin A0 (0-3.3V)
2. **SD Card**: Insert into Teensy 4.1 built-in SD card slot
3. **USB Serial**: Connect micro-USB to computer for command console
4. **Power**: Provide 5V power to Teensy 4.1

### Detection Setup
The firmware uses windowed detection on the ADC input:
- **Sampling rate**: 10 kHz (100 µs per sample)
- **Detection window**: 0.30V - 0.80V
- **Hysteresis**: Re-arm below 0.30V
- **Refractory period**: 300 µs (prevents double-counting)

### Data Flow
The firmware provides an interactive command console:
1. User sends commands via USB Serial (`on`, `off`, `snap`)
2. System samples ADC at 10 kHz and detects particle hits
3. Data streamed live to computer as CSV
4. Data logged to SD card rolling buffer (30-second FIFO)
5. Snap captures extract ±2.5s windows on command

### Data Output Formats
- **Live CSV stream**: `time_ms,voltage_V,hit,cum_counts`
- **Computer logs**: Timestamped session folders with streaming + snap CSVs
- **SD buffer**: Rolling `buffer.csv` file on Teensy SD card

## Firmware Modules

### Active Firmware (ADC-based)
- **main.cpp**: Entry point and command loop
- **SEEs_ADC.h/.cpp**: ADC-based driver with on/off/snap commands
- **sees_interactive.py**: Python console with circular buffer for snap captures

### Computer Control Scripts
- **SEEs.sh** / **SEEs.bat**: Console launchers (Linux/Mac/Windows)
- **sees_interactive.py**: Interactive Python console with:
  - Character-by-character input forwarding
  - Circular buffer (2.5s pre-trigger)
  - Snap capture (±2.5s window extraction)
  - Automatic session logging

### Hardware Configuration
- **ADC (A0)**: SiPM fast-out connection (0-3.3V input)
- **Serial (USB)**: Command console and CSV data stream at 115200 baud
- **SD Card**: Built-in Teensy 4.1 SD interface (BUILTIN_SDCARD)

## Testing

### Automated Test Suite

The `tests/` directory contains a complete test suite for development without hardware:

- **test_data_generator.py**: Generates realistic particle detector data
- **test_python_scripts.py**: 10+ unit tests for data processing
- **virtual_serial_port.py**: Simulates Teensy firmware for interactive testing
- **run_all_tests.sh**: Automated test runner

Run all tests:

```bash
cd tests
./run_all_tests.sh
```

See [tests/README.md](tests/README.md) for details.

### Test Without Hardware

Simulate the full system locally:

**Terminal 1:**

```bash
cd tests
python3 virtual_serial_port.py
```

**Terminal 2:**

```bash
./SEEs.sh /tmp/tty_sees
```

## Development Roadmap

### Version History
- **Prototype**: ✅ ADC-based detection with command control
- **V1.0**: ✅ On/off/snap command interface
- **V2.0**: 🔄 FPGA integration (4-layer histogram processing)
- **V3.0**: 🔄 Full system (AERIS iOBC) - Merge into AERIS FSW

### Critical Path
- [x] Create Initial Driver
- [x] Implement ADC-based particle detection
- [x] Add windowed detection with hysteresis
- [x] Implement command console interface (on/off/snap)
- [x] Add computer control scripts (Python + bash/bat)
- [x] Circular buffer for snap captures
- [x] SD card rolling buffer
- [ ] FPGA interface implementation (SPI communication)
- [ ] 4-layer scintillator histogram processing
- [ ] Define Payload-to-Bus Software ICD
- [ ] Add remote command handlers for spacecraft bus
- [ ] Interface into flat-sat testing environment
- [ ] Full integration with Artemis spacecraft bus software

---

## Repository

**GitHub**: https://github.com/hsfl/aeris-sees-software

**License**: MIT (see LICENSE file)

---

## Credits

**AERIS Payload Software Team** - Hawaii Space Flight Laboratory

*2025*
