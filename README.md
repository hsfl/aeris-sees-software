# aeris-sees-software
## Brief Overview
This repository contains the software for the **SEEs Payload** (Solar Energetic Events detector).  
The SEEs detector uses a four-layer scintillator stack (3× EJ212 plastic scintillators and 1× BGO crystal) read out by SiPMs. Signals are digitized and processed by an FPGA, which applies thresholds, coincidence logic, and energy binning.  
The Teensy 4.1 microcontroller handles communication with the FPGA, performs telemetry packet assembly, and streams formatted data to the AERIS spacecraft bus.

![SEEs Block Diagram](sees.png)

## Build Instructions
1. Download and install [VSCode](https://code.visualstudio.com/download) & [GitHub Desktop](https://desktop.github.com/download/).
2. Install the required VSCode extensions:
   * [PlatformIO](https://platformio.org/install/ide?install=vscode)
   * [C/C++](https://code.visualstudio.com/docs/languages/cpp)
3. Clone the repository from GitHub Desktop by selecting:
   * **Add** → **Clone Repository...** → **URL** → paste the repository link.
   * Repository URL: `https://github.com/hsfl/aeris-sees-software.git`
4. In VSCode, open the cloned repo as a PlatformIO project.
5. Confirm the environment is set to Teensy 4.1 (`platformio.ini` already configured).
6. Build the code:
   * Bottom-left of VSCode → click the checkmark (✔).
   * A `[SUCCESS]` message in the terminal indicates a successful build.
7. Upload the firmware to the Teensy 4.1:
   * Bottom-left → click the right-arrow (→).
   * Teensy Loader CLI will handle flashing.
8. Open the serial monitor:
   bash
   pio device monitor -b 115200
to view telemetry output.

## Getting Data

The FPGA performs coincidence detection and energy binning, outputting event counts and timing data.
The Teensy receives these FPGA packets, validates them with CRC, attaches sequence numbers and timestamps, and formats telemetry packets (1024B frames).
Data can be:

Streamed over USB serial for integration testing.

Forwarded via UART to the spacecraft OBC for downlink.

Example current output (simulated test packets):

SEEs Integration test starting...
3916 | 30 91 15 72 | Coinc: 1 | Flags: 0
4416 | 41 107 98 91 | Coinc: 1 | Flags: 0
5416 | 94 80 26 96 | Coinc: 1 | Flags: 0
...

### Critical Path
- [x] Teensy development environment set up (PlatformIO, serial monitor working)
- [x] Basic packet struct defined in software
- [x] Teensy can simulate and stream test packets
- [ ] Implement FPGA → Teensy data interface (UART/SPI)
- [ ] Verify CRC handling on real FPGA packets
- [ ] Format telemetry packets to 1024B + CRC
- [ ] Integrate watchdog + heartbeat
- [ ] ...
- [ ] ...
- [ ] ...
- [ ] Validate full OBC handoff in system tests
