/**
 * @file main.cpp
 * @brief Entry point for SEEs payload firmware.
 *
 * Initializes the SEEs histogram driver and continuously polls the FPGA
 * for new histogram data. Mirrors VIA (AvaSpec) firmware control flow.
 */

#include "SEEs.hpp"

// ============================================================================
// ── CONFIGURATION ────────────────────────────────────────────────────────────
// ============================================================================

#define FPGA_CS_PIN 10   ///< SPI chip select pin for FPGA interface

// ============================================================================
// ── GLOBAL OBJECTS ───────────────────────────────────────────────────────────
// ============================================================================

SEEs sees(FPGA_CS_PIN);

// ============================================================================
// ── ARDUINO ENTRY POINTS ─────────────────────────────────────────────────────
// ============================================================================

/**
 * @brief System setup. Initializes serial link and FPGA communication.
 */
void setup() {
    sees.begin();
}

/**
 * @brief Main execution loop. Polls FPGA and transmits histograms each cycle.
 */
void loop() {
    sees.update();
}