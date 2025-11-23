# SEES Quick Start

Complete workflow from unit tests to flatsat integration.

---

## Local Development & Testing

### 1. Run Unit Tests

Test without hardware:

```bash
cd tests
./run_all_tests.sh
```

Expected: All tests pass (~15-40 seconds)

**What it tests:**
- Data generation
- Python unit tests (10+ tests)
- Firmware build (if PlatformIO installed)
- Virtual serial port

### 2. Interactive Simulation (Optional)

Test console commands without hardware:

**Terminal 1:**
```bash
cd tests
python3 virtual_serial_port.py
```

**Terminal 2:**
```bash
./SEEs.sh /tmp/tty_sees
```

Try commands: `on`, `snap`, `off`

---

## Hardware-in-Loop (HIL) Testing

### 3. Connect Hardware

1. Plug Teensy 4.1 into computer via USB
2. Verify connection: `ls /dev/ttyACM*`

### 4. Upload Firmware

```bash
cd SEEsDriver
pio run --target upload
```

### 5. Test with Real Hardware

```bash
./SEEs.sh
```

In console:
```
SEEs> on
SEEs> snap
SEEs> off
```

Data saves to session folder displayed at startup.

---

## Flatsat Integration

### 6. Connect to Testing Pi

```bash
ssh pi@192.168.4.163
# Password: aeris
```

### 7. Update and Test

```bash
sees             # Go to SEES directory
git pull         # Get updates
sees-test        # Run tests
```

### 8. Connect Flatsat Hardware

1. Plug Teensy 4.1 into Pi via USB
2. Verify: `ports` should show `/dev/ttyACM0`

### 9. Launch Console

```bash
sees-console
```

### 10. Collect Data

```
SEEs> on
SEEs> snap       # Capture ±2.5s window
SEEs> off        # Stop collection
```

Data saves to `~/Aeris/data/sees/`

---

## Command Reference

| Command | What it does |
|---------|--------------|
| `on` | Start data collection |
| `off` | Stop data collection |
| `snap` | Capture ±2.5s window |
| `Ctrl+C` | Exit console |

---

## Pi Shortcuts

| Command | What it does |
|---------|--------------|
| `sees` | Go to SEES directory |
| `sees-test` | Run all tests |
| `sees-console` | Launch console |
| `aeris-status` | Check system health |
| `ports` | List serial ports |

---

## Data Locations

**Local development:**
```
tests/test_data/           # Generated test data
```

**HIL testing:**
```
Session folder shown at startup
```

**Flatsat:**
```bash
~/Aeris/data/sees/YYYYMMDD.HHMM/
├── SEEs.YYYYMMDD.HHMM.log         # Session log
├── SEEs.YYYYMMDD.HHMM.stream.csv  # Streaming data
├── SEEs.YYYYMMDD.HHMMSS.csv       # Snapshots
```

---

## Troubleshooting

**Tests fail?**
```bash
cd tests
python3 test_python_scripts.py  # Run tests individually
```

**No Teensy found?**
- Replug USB cable
- Check: `ls /dev/ttyACM*` (local) or `ports` (Pi)

**Permission denied?**
- Add user to dialout group: `sudo usermod -a -G dialout $USER`
- Logout and login again

**Can't connect to Pi?**
- Check IP: `192.168.4.163`
- Password: `aeris`

---

## Typical Workflows

### Development Cycle
```bash
# 1. Local testing
cd tests && ./run_all_tests.sh

# 2. Upload to hardware
cd SEEsDriver && pio run --target upload

# 3. Test with hardware
./SEEs.sh
```

### Flatsat Session
```bash
# Connect
ssh pi@192.168.4.163

# Update and test
sees && git pull && sees-test

# Run flatsat
sees-console

# In console:
SEEs> on
SEEs> snap
SEEs> off
SEEs> Ctrl+C
```

---

## Reference Card

```
┌──────────────────────────────────────────────┐
│ SEES TESTING WORKFLOW                        │
├──────────────────────────────────────────────┤
│ LOCAL                                        │
│   tests/run_all_tests.sh                     │
│   pio run --target upload                    │
│   ./SEEs.sh                                  │
│                                              │
│ FLATSAT (Pi 400)                             │
│   ssh pi@192.168.4.163  (pwd: aeris)        │
│   sees → git pull → sees-test → sees-console│
│                                              │
│ CONSOLE COMMANDS                             │
│   on         Start collection                │
│   snap       Capture ±2.5s                   │
│   off        Stop collection                 │
│   Ctrl+C     Exit                            │
│                                              │
│ DATA                                         │
│   Local: Session folder at startup           │
│   Flatsat: ~/Aeris/data/sees/YYYYMMDD.HHMM/ │
└──────────────────────────────────────────────┘
```

---

## More Information

- **Tests:** `tests/README.md`
- **Full docs:** `README.md`
- **Firmware:** `SEEsDriver/README.md`
