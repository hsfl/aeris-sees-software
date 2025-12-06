# SEES Test Suite

Comprehensive testing for SEES particle detector software.

## Quick Start

Run all tests:
```bash
cd tests
./run_all_tests.sh
```

## Test Components

### 1. Unit Tests (`test_python_scripts.py`)

Tests for Python data processing:
- Data generation reproducibility
- CSV format validation
- Data range checking
- Hit detection logic
- Sampling rate verification

Run manually:
```bash
python3 test_python_scripts.py
```

### 2. Test Data Generator (`test_data_generator.py`)

Generates realistic simulated particle detector data:
- 10 kHz sampling rate
- Particle pulse simulation (Gaussian pulses)
- Configurable hit rates
- Poisson process for hit timing

Generate test data:
```bash
# Default: 10s at 5 hits/s
python3 test_data_generator.py

# Custom parameters
python3 test_data_generator.py --duration 30 --hit-rate 20 --output custom_test.csv
```

### 3. Virtual Serial Port (`virtual_serial_port.py`)

Simulates Teensy 4.1 SEES firmware for testing without hardware:
- Creates `/tmp/tty_sees` virtual serial port
- Responds to `snap` command (body cam mode - always streaming)
- Streams realistic particle detector data
- Full console simulation

Run virtual port:
```bash
python3 virtual_serial_port.py
```

Then in another terminal:
```bash
cd ../scripts
python3 sees_interactive.py /tmp/tty_sees
```

### 4. Automated Test Runner (`run_all_tests.sh`)

Runs complete test suite:
1. Python environment check
2. Test data generation
3. Python unit tests (10+ tests)
4. Firmware build check (if PlatformIO installed)
5. Virtual serial port test

```bash
./run_all_tests.sh
```

## Test Data Format

Generated CSV data matches SEES firmware output:
```csv
time_ms,voltage_V,hit,total_hits
0.0,0.0982,0,0
0.1,0.1015,0,0
0.2,0.5234,1,1
0.3,0.4891,1,1
0.4,0.1123,0,1
```

Where:
- `time_ms`: Timestamp in milliseconds
- `voltage_V`: ADC voltage (0-3.3V)
- `hit`: Binary flag (1 if in detection window 0.30-0.80V)
- `total_hits`: Cumulative particle count

## Testing Workflow

### Without Hardware

Use virtual serial port for full system testing:

```bash
# Terminal 1: Start virtual Teensy
cd tests
python3 virtual_serial_port.py

# Terminal 2: Run interactive console
cd scripts
python3 sees_interactive.py /tmp/tty_sees

# Use normally:
SEEs> on
SEEs> snap
SEEs> off
```

### With Hardware

Run tests, then test with real hardware:

```bash
# 1. Run automated tests
cd tests
./run_all_tests.sh

# 2. Connect Teensy and test
cd ../scripts
python3 sees_interactive.py /dev/ttyACM0
```

## Test Coverage

- ✅ Data generation (reproducibility, ranges)
- ✅ CSV format validation
- ✅ Hit detection logic
- ✅ Sampling rate (10 kHz)
- ✅ Cumulative counting
- ✅ Edge cases (zero hits, bursts, etc.)
- ✅ Virtual hardware simulation
- ✅ Firmware build verification

## Requirements

Python packages (automatically installed with SEES):
- `pyserial` (for serial communication)
- No additional packages needed

PlatformIO (optional, for firmware build tests):
```bash
pip install platformio
```

## Continuous Testing

Run tests before committing changes:

```bash
# Quick test
cd tests && python3 test_python_scripts.py

# Full test suite
cd tests && ./run_all_tests.sh
```

## Troubleshooting

**Virtual port fails to create:**
- Check `/tmp/` is writable
- Ensure no other process using `/tmp/tty_sees`
- Try: `rm -f /tmp/tty_sees` then retry

**Unit tests fail:**
- Check Python version (3.7+ required)
- Ensure in `tests/` directory
- Clean test data: `rm -rf test_data/`

**PlatformIO not found:**
- Install: `pip install platformio`
- Or skip firmware tests (tests still pass)

## Adding New Tests

Add tests to `test_python_scripts.py`:

```python
class TestMyFeature(unittest.TestCase):
    def test_my_feature(self):
        # Your test code here
        self.assertEqual(result, expected)
```

Then run:
```bash
python3 test_python_scripts.py
```

---

**For more info:** See main [README.md](../README.md)
