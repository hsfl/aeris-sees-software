#!/bin/bash
#
# SEES Automated Test Suite
#
# Runs all tests for SEES software:
# - Python unit tests
# - Data generation tests
# - Firmware build check (if PlatformIO available)
# - Virtual serial port test
#
# Usage: ./run_all_tests.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DRIVER_DIR="$PROJECT_ROOT/SEEsDriver"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════════"
echo "  SEES SOFTWARE - AUTOMATED TEST SUITE"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -e "${BLUE}Running: ${test_name}${NC}"
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# 1. Check Python environment
echo "[1/5] Checking Python environment..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python $PYTHON_VERSION"
echo ""

# 2. Generate test data
echo "[2/5] Generating test data..."
cd "$SCRIPT_DIR"
python3 test_data_generator.py --output test_data/sees_test.csv --duration 5.0 --hit-rate 10.0
echo -e "${GREEN}✅ Test data generated${NC}"
echo ""

# 3. Run Python unit tests
echo "[3/5] Running Python unit tests..."
cd "$SCRIPT_DIR"
if python3 test_python_scripts.py 2>&1 | tee test_output.log; then
    # Count passed tests
    UNIT_TESTS_PASSED=$(grep -c "ok" test_output.log || echo "0")
    echo -e "${GREEN}✅ All $UNIT_TESTS_PASSED tests passed${NC}"
    rm test_output.log
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Unit tests failed${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# 4. Check for PlatformIO and build firmware
echo "[4/5] Checking for PlatformIO..."
if command -v pio &> /dev/null; then
    echo -e "${GREEN}✅ PlatformIO found${NC}"
    echo "Building firmware..."
    cd "$DRIVER_DIR"

    if pio run 2>&1 | tee build_output.log; then
        echo -e "${GREEN}✅ Firmware build successful${NC}"
        rm build_output.log
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ Firmware build failed${NC}"
        echo "See build_output.log for details"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${YELLOW}⚠️  PlatformIO not found - skipping firmware build${NC}"
    echo "   Install with: pip install platformio"
fi
echo ""

# 5. Test virtual serial port (quick sanity check)
echo "[5/5] Testing virtual serial port creation..."
cd "$SCRIPT_DIR"

# Start virtual port in background
python3 virtual_serial_port.py &
VIRTUAL_PORT_PID=$!

# Give it time to start
sleep 2

# Check if it created the port
if [ -e /tmp/tty_sees ]; then
    echo -e "${GREEN}✅ Virtual port created successfully${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Virtual port creation failed${NC}"
    ((TESTS_FAILED++))
fi

# Kill virtual port
kill $VIRTUAL_PORT_PID 2>/dev/null || true
sleep 1

# Clean up
rm -f /tmp/tty_sees

echo ""

# Print summary
echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════════"
echo "  TEST SUMMARY"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Unit tests: PASSED${NC}"
    echo -e "${GREEN}✅ Data generation: PASSED${NC}"

    if command -v pio &> /dev/null; then
        echo -e "${GREEN}✅ Firmware build: PASSED${NC}"
    else
        echo -e "${YELLOW}⚠️  Firmware build: SKIPPED (PlatformIO not installed)${NC}"
    fi

    echo -e "${GREEN}✅ Virtual port: PASSED${NC}"
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}All tests passed successfully!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo -e "   Passed: ${TESTS_PASSED}"
    echo -e "   Failed: ${TESTS_FAILED}"
    echo ""
    exit 1
fi
