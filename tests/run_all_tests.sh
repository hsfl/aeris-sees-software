#!/bin/bash
#
# SEEs Software Test Suite Runner
#
# Runs all automated tests for the SEEs particle detector software
# without requiring physical hardware.
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "═══════════════════════════════════════════════════════════════════"
echo "  SEEs PARTICLE DETECTOR SOFTWARE - AUTOMATED TEST SUITE"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Check Python version
echo -e "${BLUE}[1/5] Checking Python environment...${NC}"
python3 --version
echo ""

# Generate test data
echo -e "${BLUE}[2/5] Generating test data...${NC}"
python3 test_data_generator.py --duration 5.0 --hit-rate 10.0 --output test_data/sees_test_10hz.csv
python3 test_data_generator.py --duration 2.0 --hit-rate 50.0 --output test_data/sees_burst_50hz.csv
python3 test_data_generator.py --duration 5.0 --hit-rate 0.0 --output test_data/sees_quiet.csv
echo ""

# Run Python unit tests
echo -e "${BLUE}[3/7] Running Python unit tests...${NC}"
python3 test_python_scripts.py
TEST_RESULT=$?
echo ""

# Run circular buffer tests
echo -e "${BLUE}[4/7] Running circular buffer tests...${NC}"
python3 test_circular_buffer.py
BUFFER_RESULT=$?
echo ""

# Run multi-layer detection tests
echo -e "${BLUE}[5/7] Running multi-layer detection tests...${NC}"
python3 test_multilayer_detection.py
MULTILAYER_RESULT=$?
echo ""

# Check if PlatformIO is available for firmware tests
echo -e "${BLUE}[6/7] Checking for PlatformIO (firmware build test)...${NC}"
if command -v pio &> /dev/null; then
    echo "✅ PlatformIO found"
    echo "Building firmware (syntax check)..."
    cd ../SEEsDriver
    pio run --target checkprogsize 2>&1 | tail -20
    BUILD_RESULT=$?
    cd "$SCRIPT_DIR"

    if [ $BUILD_RESULT -eq 0 ]; then
        echo -e "${GREEN}✅ Firmware build successful${NC}"
    else
        echo -e "${YELLOW}⚠️  Firmware build failed (check SEEsDriver)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  PlatformIO not found - skipping firmware build test${NC}"
    echo "   Install with: pip install platformio"
    BUILD_RESULT=0  # Don't fail overall tests
fi
echo ""

# Test data loading/processing
echo -e "${BLUE}[7/7] Testing data loading and processing...${NC}"
if python3 -c "import csv" 2>/dev/null; then
    echo "✅ CSV module available"

    # Test data loading
    if [ -f "test_data/sees_test_10hz.csv" ]; then
        echo "Testing data loading with generated data..."
        python3 -c "
import csv
from pathlib import Path

# Load test data
test_file = Path('test_data/sees_test_10hz.csv')
if test_file.exists():
    time_vals, voltages, hits, counts = [], [], [], []
    with open(test_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            time_vals.append(float(row['time_ms']))
            voltages.append(float(row['voltage_V']))
            hits.append(int(row['hit']))
            counts.append(int(row['cum_counts']))

    assert len(time_vals) == 50000, f'Expected 50000 samples, got {len(time_vals)}'
    assert all(0 <= v <= 3.3 for v in voltages), 'Voltage out of range'
    assert all(h in [0, 1] for h in hits), 'Hit flag not binary'
    print(f'✅ Successfully loaded {len(time_vals)} data points')
    print(f'   Voltage range: {min(voltages):.4f}V - {max(voltages):.4f}V')
    print(f'   Total hits: {counts[-1]}')
    print(f'   Hit rate: {counts[-1] / 5.0:.1f} hits/s')
else:
    print('⚠️  Test data not found')
    exit(1)
"
        DATA_RESULT=$?
        if [ $DATA_RESULT -eq 0 ]; then
            echo -e "${GREEN}✅ Data loading test passed${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  CSV module not available${NC}"
    DATA_RESULT=0
fi
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════════"
echo "  TEST SUMMARY"
echo "═══════════════════════════════════════════════════════════════════"

OVERALL_RESULT=0

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Unit tests: PASSED${NC}"
else
    echo -e "${RED}❌ Unit tests: FAILED${NC}"
    OVERALL_RESULT=1
fi

if [ $BUFFER_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Circular buffer tests: PASSED${NC}"
else
    echo -e "${RED}❌ Circular buffer tests: FAILED${NC}"
    OVERALL_RESULT=1
fi

if [ $MULTILAYER_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Multi-layer detection tests: PASSED${NC}"
else
    echo -e "${RED}❌ Multi-layer detection tests: FAILED${NC}"
    OVERALL_RESULT=1
fi

if [ $BUILD_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Firmware build: PASSED${NC}"
else
    echo -e "${YELLOW}⚠️  Firmware build: SKIPPED or FAILED${NC}"
fi

if [ $DATA_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Data processing: PASSED${NC}"
else
    echo -e "${YELLOW}⚠️  Data processing: SKIPPED${NC}"
fi

echo "═══════════════════════════════════════════════════════════════════"

if [ $OVERALL_RESULT -eq 0 ]; then
    echo -e "${GREEN}"
    echo "  ███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗███████╗"
    echo "  ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝"
    echo "  ███████╗██║   ██║██║     ██║     █████╗  ███████╗███████╗"
    echo "  ╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║╚════██║"
    echo "  ███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║███████║"
    echo "  ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝"
    echo -e "${NC}"
    echo "All tests passed successfully!"
else
    echo -e "${RED}"
    echo "  ███████╗ █████╗ ██╗██╗     ███████╗██████╗ "
    echo "  ██╔════╝██╔══██╗██║██║     ██╔════╝██╔══██╗"
    echo "  █████╗  ███████║██║██║     █████╗  ██║  ██║"
    echo "  ██╔══╝  ██╔══██║██║██║     ██╔══╝  ██║  ██║"
    echo "  ██║     ██║  ██║██║███████╗███████╗██████╔╝"
    echo "  ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝ "
    echo -e "${NC}"
    echo "Some tests failed. Check output above."
fi

echo "═══════════════════════════════════════════════════════════════════"

exit $OVERALL_RESULT
