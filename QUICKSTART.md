# SEES Particle Detector Quick Start

## Connect to the Pi 400

```bash
ssh aeris@192.168.120.22
```

> **Off-campus?** Connect via Tailscale first.

---

## Run the AERIS Console

```bash
aeris
```

That's it. You'll see the interactive menu:

```
╔════════════════════════════════════════════╗
║          AERIS Control Panel               ║
╚════════════════════════════════════════════╝

┌────────────────────────┐
│ SEES Particle Detector │
├────────────────────────┴─────────────────┐
│ 4) Unit Tests        Python test suite   │
│ 5) Simulation        Virtual serial port │
│ 6) HIL Test          Hardware-in-loop    │
└──────────────────────────────────────────┘
...
```

Pick an option:

- **4** - Run unit tests
- **5** - Run simulation (no hardware needed)
- **6** - Connect to real Teensy hardware

---

## CLI Shortcuts

Skip the menu with direct commands:

```bash
aeris sees test      # Run unit tests
aeris sees sim       # Run simulation
aeris sees sim -v    # Simulation with verbose output
aeris update         # Pull latest code
aeris help           # Show all commands
```

---

## SEES Console Commands

Once in the SEES console:

| Command | What it does |
|---------|--------------|
| `on` | Start data streaming |
| `off` | Stop data streaming |
| `snap` | Capture ±2.5s window |
| `Ctrl+C` | Exit |

---

## Understanding SEES Data

SEES operates in **"body cam" mode** - always recording the last 30 seconds.

When you run `snap`:

1. Captures 2.5 seconds BEFORE the command
2. Plus 2.5 seconds AFTER
3. Total: 5-second window centered on snap time

---

## View Your Data

Data is saved to `~/Aeris/data/sees/YYYYMMDD.HHMM/`:

```bash
ls ~/Aeris/data/sees/
```

---

## Troubleshooting

**Can't connect?** Check you're on network `192.168.120.x` or use Tailscale.

**Permission denied on serial?** Run `sudo usermod -a -G dialout $USER` and re-login.

**Tests failing?** Use `aeris sees test -v` for verbose output.

---

## More Info

- [README.md](README.md) - Full documentation
- [tests/README.md](tests/README.md) - Test details
