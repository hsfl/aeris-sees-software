#include <Arduino.h>
#include "SEEs.hpp"

// ============================================================================
//  Entry Point
//  ---------------------------------------------------------------------------
//  The main.cpp file exists only to bootstrap hardware and delegate control
//  to the SEEs subsystem defined in SEEs.cpp.
// ============================================================================

void setup() {
    SEEs::initialize();    // Initialize SEEs driver and serial interface
}

void loop() {
    SEEs::run_cycle();     // Execute one telemetry test cycle
}