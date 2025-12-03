/**
 * @file FPGA_Interface.cpp
 * @brief Implementation of SPI routines for SEEs FPGA histogram frames.
 *
 * Frame format:
 *  [0xAB]
 *  [64 bytes of 16-bit counts (layer × bin)]
 *  [t0][t1][t2][t3]
 *  [crc]
 */

#include "FPGA_Interface.hpp"

// ============================================================================
// ── CONFIGURATION CONSTANTS ──────────────────────────────────────────────────
// ============================================================================

#define FPGA_HIST_SYNC 0xAB
#define FPGA_HIST_LEN  70  // total bytes per frame

// ============================================================================
// ── IMPLEMENTATION ───────────────────────────────────────────────────────────
// ============================================================================

FPGA_Interface::FPGA_Interface(uint8_t csPin, SPIClass &spiBus)
    : _cs(csPin), _spi(&spiBus) {}

void FPGA_Interface::begin() {
    pinMode(_cs, OUTPUT);
    digitalWrite(_cs, HIGH);
    _spi->begin();
}

/**
 * @brief Read one histogram frame from the FPGA.
 */
bool FPGA_Interface::getHistogram(HistogramData &hist) {
    uint8_t buf[FPGA_HIST_LEN];

    digitalWrite(_cs, LOW);
    for (int i = 0; i < FPGA_HIST_LEN; ++i)
        buf[i] = _spi->transfer(0x00);
    digitalWrite(_cs, HIGH);

    if (buf[0] != FPGA_HIST_SYNC) {
        hist.valid = false;
        return false;
    }

    uint8_t crc = calcCRC(buf, FPGA_HIST_LEN - 1);
    if (crc != buf[FPGA_HIST_LEN - 1]) {
        hist.valid = false;
        return false;
    }

    // Unpack 64 bytes of counts (little-endian 16-bit)
    int idx = 1;
    for (int layer = 0; layer < 4; ++layer) {
        for (int bin = 0; bin < 8; ++bin) {
            hist.counts[layer][bin] =
                (uint16_t)buf[idx] | ((uint16_t)buf[idx + 1] << 8);
            idx += 2;
        }
    }

    // Timestamp
    hist.timestamp = (uint32_t)buf[idx] |
                     ((uint32_t)buf[idx + 1] << 8) |
                     ((uint32_t)buf[idx + 2] << 16) |
                     ((uint32_t)buf[idx + 3] << 24);

    hist.valid = true;
    return true;
}

void FPGA_Interface::sendCommand(uint8_t cmd, uint16_t value) {
    uint8_t packet[4];
    packet[0] = 0x55;
    packet[1] = cmd;
    packet[2] = value & 0xFF;
    packet[3] = (value >> 8) & 0xFF;

    digitalWrite(_cs, LOW);
    for (auto b : packet) _spi->transfer(b);
    digitalWrite(_cs, HIGH);
}

uint8_t FPGA_Interface::calcCRC(const uint8_t *buf, size_t len) {
    uint8_t crc = 0;
    for (size_t i = 0; i < len; ++i)
        crc ^= buf[i];
    return crc;
}