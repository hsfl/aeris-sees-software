/**
 * @file main.cpp
 * @brief Entry point for SEEs payload firmware.
 *
 * Initializes the SEEs payload driver and continuously polls the FPGA
 * for new events. Follows the same control flow and style conventions as
 * the VIA (AvaSpec) firmware.
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
 * @brief System setup. Initializes all peripherals.
 */
void setup() {
    sees.begin();
}

/**
 * @brief Main execution loop. Polls FPGA and transmits events.
 */
void loop() {
    sees.update();
}