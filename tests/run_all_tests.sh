#!/bin/bash
#
# SEEs Software Test Suite Runner
#
# Usage:
#   ./run_all_tests.sh        # Normal mode (test names + results)
#   ./run_all_tests.sh -v     # Verbose mode (full output)
#   ./run_all_tests.sh -f     # Include firmware build test
#   ./run_all_tests.sh -vf    # Verbose + firmware build
#

# Parse arguments
VERBOSE=0
FIRMWARE=0
for arg in "$@"; do
    case $arg in
        -v|--verbose) VERBOSE=1 ;;
        -f|--firmware) FIRMWARE=1 ;;
        -vf|-fv) VERBOSE=1; FIRMWARE=1 ;;
    esac
done

# UH Colors (Green #024731, Silver #C8C8C8)
UH_GREEN='\033[38;2;2;71;49m'
UH_SILVER='\033[38;2;200;200;200m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BRIGHT_GREEN='\033[38;2;0;255;0m'
BRIGHT_RED='\033[38;2;255;0;0m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Track results
TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${UH_GREEN}═══════════════════════════════════════════════════════════════════"
echo -e "  ${UH_SILVER}SEEs PARTICLE DETECTOR - TEST SUITE${UH_GREEN}"
echo -e "═══════════════════════════════════════════════════════════════════${NC}"
if [ $VERBOSE -eq 0 ]; then
    echo "  (use -v for verbose output)"
fi
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Generate test data
# ─────────────────────────────────────────────────────────────────────────────
if [ $VERBOSE -eq 1 ]; then
    echo -e "${BLUE}[1/6] Generating test data...${NC}"
    python3 test_data_generator.py --duration 5.0 --hit-rate 10.0 --output test_data/sees_test_10hz.csv
    python3 test_data_generator.py --duration 2.0 --hit-rate 50.0 --output test_data/sees_burst_50hz.csv
    python3 test_data_generator.py --duration 5.0 --hit-rate 0.0 --output test_data/sees_quiet.csv
    echo ""
else
    python3 test_data_generator.py --duration 5.0 --hit-rate 10.0 --output test_data/sees_test_10hz.csv > /dev/null 2>&1
    python3 test_data_generator.py --duration 2.0 --hit-rate 50.0 --output test_data/sees_burst_50hz.csv > /dev/null 2>&1
    python3 test_data_generator.py --duration 5.0 --hit-rate 0.0 --output test_data/sees_quiet.csv > /dev/null 2>&1
fi

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Unit tests
# ─────────────────────────────────────────────────────────────────────────────
echo "  Unit Tests:"
if [ $VERBOSE -eq 1 ]; then
    python3 test_python_scripts.py -v
else
    python3 test_python_scripts.py
fi
UNIT_RESULT=$?
echo ""

if [ $UNIT_RESULT -eq 0 ]; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: Circular buffer tests
# ─────────────────────────────────────────────────────────────────────────────
echo "  Circular Buffer Tests:"
if [ $VERBOSE -eq 1 ]; then
    python3 test_circular_buffer.py -v
else
    python3 test_circular_buffer.py
fi
BUFFER_RESULT=$?
echo ""

if [ $BUFFER_RESULT -eq 0 ]; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# ─────────────────────────────────────────────────────────────────────────────
# Stage 4: Multi-layer detection tests
# ─────────────────────────────────────────────────────────────────────────────
echo "  Multi-Layer Detection Tests:"
if [ $VERBOSE -eq 1 ]; then
    python3 test_multilayer_detection.py -v
else
    python3 test_multilayer_detection.py
fi
MULTILAYER_RESULT=$?
echo ""

if [ $MULTILAYER_RESULT -eq 0 ]; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# ─────────────────────────────────────────────────────────────────────────────
# Stage 5: Firmware build check (only with -f flag)
# ─────────────────────────────────────────────────────────────────────────────
BUILD_RESULT=-1
if [ $FIRMWARE -eq 1 ]; then
    echo -n "  Firmware build... "
    if command -v pio &> /dev/null; then
        if [ $VERBOSE -eq 1 ]; then
            echo ""
            cd ../SEEsDriver
            pio run 2>&1 | tail -30
            BUILD_RESULT=$?
            cd "$SCRIPT_DIR"
        else
            cd ../SEEsDriver
            pio run > /dev/null 2>&1
            BUILD_RESULT=$?
            cd "$SCRIPT_DIR"
        fi

        if [ $BUILD_RESULT -eq 0 ]; then
            echo -e "${GREEN}ok${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}FAILED${NC}"
            ((TESTS_FAILED++))
        fi
    else
        echo -e "${YELLOW}skipped${NC} (PlatformIO not found)"
        BUILD_RESULT=-1
    fi
    echo ""
fi

# ─────────────────────────────────────────────────────────────────────────────
# Stage 6: Data format validation
# ─────────────────────────────────────────────────────────────────────────────
if [ $VERBOSE -eq 1 ]; then
    echo -e "${BLUE}[6/6] Validating data formats...${NC}"
fi

FORMAT_PASSED=1
for test_file in test_data/sees_test_10hz.csv test_data/sees_burst_50hz.csv test_data/sees_quiet.csv; do
    if [ -f "$test_file" ]; then
        # Check header exists (strip CR/LF for cross-platform compatibility)
        HEADER=$(head -1 "$test_file" | tr -d '\r\n')
        if [[ "$HEADER" != "time_ms,voltage_V,hit,total_hits" ]]; then
            FORMAT_PASSED=0
            if [ $VERBOSE -eq 1 ]; then
                echo "  ❌ $test_file: wrong header"
            fi
        else
            if [ $VERBOSE -eq 1 ]; then
                echo "  ✓ $test_file"
            fi
        fi
    else
        FORMAT_PASSED=0
        if [ $VERBOSE -eq 1 ]; then
            echo "  ❌ $test_file: not found"
        fi
    fi
done

if [ $FORMAT_PASSED -eq 1 ]; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

if [ $VERBOSE -eq 1 ]; then
    echo ""
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${UH_GREEN}═══════════════════════════════════════════════════════════════════"
echo -e "  ${UH_SILVER}RESULTS${UH_GREEN}"
echo -e "═══════════════════════════════════════════════════════════════════${NC}"

# Unit tests
if [ $UNIT_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Unit tests"
else
    echo -e "  ${RED}✗${NC} Unit tests"
fi

# Circular buffer
if [ $BUFFER_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Circular buffer"
else
    echo -e "  ${RED}✗${NC} Circular buffer"
fi

# Multi-layer detection
if [ $MULTILAYER_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Multi-layer detection"
else
    echo -e "  ${RED}✗${NC} Multi-layer detection"
fi

# Firmware build (only shown if -f flag used)
if [ $FIRMWARE -eq 1 ]; then
    if [ $BUILD_RESULT -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} Firmware build"
    elif [ $BUILD_RESULT -eq -1 ]; then
        echo -e "  ${YELLOW}-${NC} Firmware build (skipped - PlatformIO not found)"
    else
        echo -e "  ${RED}✗${NC} Firmware build"
    fi
fi

# Data formats
if [ $FORMAT_PASSED -eq 1 ]; then
    echo -e "  ${GREEN}✓${NC} Data formats"
else
    echo -e "  ${RED}✗${NC} Data formats"
fi

echo ""

# Final result with ASCII art
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${BRIGHT_GREEN}"
    echo "  ███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗███████╗"
    echo "  ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝"
    echo "  ███████╗██║   ██║██║     ██║     █████╗  ███████╗███████╗"
    echo "  ╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║╚════██║"
    echo "  ███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║███████║"
    echo "  ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝"
    echo -e "${NC}"
    echo "  All $TESTS_PASSED test groups passed"
    echo ""
    exit 0
else
    echo -e "${BRIGHT_RED}"
    echo "  ███████╗ █████╗ ██╗██╗     ███████╗██████╗ "
    echo "  ██╔════╝██╔══██╗██║██║     ██╔════╝██╔══██╗"
    echo "  █████╗  ███████║██║██║     █████╗  ██║  ██║"
    echo "  ██╔══╝  ██╔══██║██║██║     ██╔══╝  ██║  ██║"
    echo "  ██║     ██║  ██║██║███████╗███████╗██████╔╝"
    echo "  ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝ "
    echo -e "${NC}"
    echo "  $TESTS_FAILED failed, $TESTS_PASSED passed"
    if [ $VERBOSE -eq 0 ]; then
        echo ""
        echo "  Run with -v for details"
    fi
    echo ""
    exit 1
fi
