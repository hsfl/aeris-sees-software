/**
 * @file SEEs.cpp
 * @brief Implementation of SEEs payload logic for histogram-based FPGA data acquisition.
 *
 * Handles SPI communication, telemetry packet construction, and UART transmission.
 * Each histogram frame represents one integration window containing particle counts
 * binned by energy and detector layer.
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
    Serial.begin(115200);     // UART → Dock/OBC
    fpga.begin();             // Initialize SPI bus and FPGA
    delay(250);

    Serial.println("[SEEs] ✅ Histogram FPGA interface initialized.");
}

// ============================================================================
// ── MAIN LOOP HANDLER ────────────────────────────────────────────────────────
// ============================================================================

/**
 * @brief Poll FPGA for histogram frames and forward valid data as telemetry.
 *
 * Each call retrieves one histogram from the FPGA, which represents the accumulated
 * counts for all detector layers and energy bins during the last integration window.
 * The histogram is formatted into a compact telemetry packet and transmitted to
 * the Dock/OBC over UART.
 */
void SEEs::update() {
    if (fpga.getHistogram(currentFrame) && currentFrame.valid) {
        buildTelemetry();
        sendTelemetry();
    }
}

// ============================================================================
// ── TELEMETRY CONSTRUCTION ───────────────────────────────────────────────────
// ============================================================================

/**
 * @brief Construct a telemetry packet from the histogram data.
 *
 * The packet uses a simplified binary framing structure:
 *  [0xBE]                 → Start byte
 *  [Layer × Bin counts]   → 4×8×2B = 64 bytes
 *  [timestamp (4B)]       → Integration window end
 *  [0xEF]                 → End byte
 *
 * The resulting packet (~70 bytes) is compatible with AERIS telemetry standards.
 */
void SEEs::buildTelemetry() {
    memset(packet, 0, sizeof(packet));
    int idx = 0;

    packet[idx++] = 0xBE;  // Start marker

    // Flatten 2D histogram into linear stream
    for (int layer = 0; layer < 4; ++layer) {
        for (int bin = 0; bin < 8; ++bin) {
            uint16_t count = currentFrame.counts[layer][bin];
            packet[idx++] = count & 0xFF;
            packet[idx++] = (count >> 8) & 0xFF;
        }
    }

    // Timestamp (little-endian)
    memcpy(&packet[idx], &currentFrame.timestamp, sizeof(uint32_t));
    idx += sizeof(uint32_t);

    packet[idx++] = 0xEF;  // End marker
}

/**
 * @brief Send the telemetry packet via UART.
 */
void SEEs::sendTelemetry() {
    Serial.write(packet, 70);
    Serial.flush();
}