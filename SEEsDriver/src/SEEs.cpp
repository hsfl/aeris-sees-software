/**
 * @file SEEs.cpp
 * @brief Implementation of SEEs payload logic for FPGA-based event acquisition.
 *
 * Handles FPGA communication, telemetry packet construction, and UART transmission.
 * Adheres to AERIS flight software communication conventions and VIA documentation style.
 */

#include "SEEs.hpp"

// ============================================================================
// ── INITIALIZATION ───────────────────────────────────────────────────────────
// ============================================================================

/**
 * @brief Construct the SEEs payload driver.
 * @param csPin Chip-select line connected to the FPGA SPI interface.
 */
SEEs::SEEs(uint8_t csPin)
    : fpga(csPin) {}

/**
 * @brief Initialize serial link and FPGA communication.
 */
void SEEs::begin() {
    Serial.begin(115200);       // UART → Dock/OBC
    fpga.begin();               // Initialize SPI bus and FPGA
    delay(250);

    Serial.println("[SEEs] ✅ FPGA interface initialized.");
}

// ============================================================================
// ── MAIN LOOP HANDLER ────────────────────────────────────────────────────────
// ============================================================================

/**
 * @brief Poll FPGA for events and forward valid detections as telemetry.
 *
 * The FPGA performs real-time coincidence logic between detector layers.
 * When an event is detected, it is stored in an internal FIFO. This routine
 * reads from that FIFO, builds a minimal telemetry packet, and transmits it
 * to the Dock/OBC.
 */
void SEEs::update() {
    if (fpga.getEvent(currentEvent) && currentEvent.valid) {
        buildTelemetry();
        sendTelemetry();
    }
}

// ============================================================================
// ── TELEMETRY CONSTRUCTION ───────────────────────────────────────────────────
// ============================================================================

/**
 * @brief Construct a small telemetry packet from the current event.
 *
 * The packet uses a lightweight binary framing format:
 *  [0xBE][layer_mask][energy_bin][timestamp (4 bytes)][0xEF]
 */
void SEEs::buildTelemetry() {
    memset(packet, 0, sizeof(packet));
    packet[0] = 0xBE;
    packet[1] = currentEvent.layer_mask;
    packet[2] = currentEvent.energy_bin;
    memcpy(&packet[3], &currentEvent.timestamp, sizeof(uint32_t));
    packet[7] = 0xEF;
}

/**
 * @brief Send the telemetry packet via UART.
 */
void SEEs::sendTelemetry() {
    Serial.write(packet, 8);
}