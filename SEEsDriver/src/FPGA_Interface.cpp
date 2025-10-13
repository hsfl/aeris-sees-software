/**
 * @file FPGA_Interface.cpp
 * @brief Implementation of SPI communication routines for the SEEs FPGA.
 *
 * Manages event retrieval, CRC validation, and command transmission. 
 * Packet framing:
 *  [0xAA][layer_mask][energy_bin][t0][t1][t2][t3][crc]
 */

#include "FPGA_Interface.hpp"

// ============================================================================
// ── CONFIGURATION CONSTANTS ──────────────────────────────────────────────────
// ============================================================================

#define FPGA_FRAME_SYNC 0xAA
#define FPGA_FRAME_LEN  8

// ============================================================================
// ── CLASS IMPLEMENTATION ─────────────────────────────────────────────────────
// ============================================================================

FPGA_Interface::FPGA_Interface(uint8_t csPin, SPIClass &spiBus)
    : _cs(csPin), _spi(&spiBus) {}

/**
 * @brief Initialize the SPI interface and control lines.
 */
void FPGA_Interface::begin() {
    pinMode(_cs, OUTPUT);
    digitalWrite(_cs, HIGH);
    _spi->begin();
}

/**
 * @brief Read one event frame from the FPGA FIFO.
 */
bool FPGA_Interface::getEvent(EventData &evt) {
    uint8_t buf[FPGA_FRAME_LEN];

    digitalWrite(_cs, LOW);
    for (int i = 0; i < FPGA_FRAME_LEN; ++i)
        buf[i] = _spi->transfer(0x00);
    digitalWrite(_cs, HIGH);

    if (buf[0] != FPGA_FRAME_SYNC) {
        evt.valid = false;
        return false;
    }

    uint8_t crc = calcCRC(buf, FPGA_FRAME_LEN - 1);
    if (crc != buf[FPGA_FRAME_LEN - 1]) {
        evt.valid = false;
        return false;
    }

    evt.layer_mask = buf[1];
    evt.energy_bin = buf[2];
    evt.timestamp  = (uint32_t)buf[3] | ((uint32_t)buf[4] << 8)
                   | ((uint32_t)buf[5] << 16) | ((uint32_t)buf[6] << 24);
    evt.valid = true;
    return true;
}

/**
 * @brief Send configuration command to FPGA.
 */
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

/**
 * @brief Calculate simple XOR checksum.
 */
uint8_t FPGA_Interface::calcCRC(const uint8_t *buf, size_t len) {
    uint8_t crc = 0;
    for (size_t i = 0; i < len; ++i)
        crc ^= buf[i];
    return crc;
}