# DEPRECATED Code

This folder contains code that is not currently used but kept for reference.

## Contents

### FPGA-Based Implementation (Future Hardware)
- **SEEs.hpp/cpp** - Main payload driver for FPGA interface
- **FPGA_Interface.hpp/cpp** - SPI communication with FPGA histogram processor

**Status:** Waiting for FPGA hardware to be built. This code is designed for the final flight hardware with 4-layer detector + FPGA front-end.

### Old Scintillator Counter
- **DEPRETIATED_Scintillator_Counter/** - Original ADC-based approach

**Status:** Replaced by SEEs_Prototype_Code.cpp which is more sophisticated.

---

## Current Active Code

See `src/` folder:
- **main.cpp** - Entry point (Arduino setup/loop)
- **SEEs_Prototype_Code.cpp** - Current working implementation using Teensy ADC directly

The prototype code reads SiPM output directly via ADC and outputs CSV format for computer control and analysis.
