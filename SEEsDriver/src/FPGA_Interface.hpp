/**
 * @file FPGA_Interface.hpp
 * @brief SPI interface for SEEs FPGA histogram data acquisition.
 *
 * The FPGA accumulates per-layer, per-energy counts over a fixed time window
 * and transmits the full histogram once per integration cycle.
 */

#pragma once
#include <Arduino.h>
#include <SPI.h>

/**
 * @struct HistogramData
 * @brief Represents one complete histogram frame from the FPGA.
 */
struct HistogramData {
    uint16_t counts[4][8];  ///< [layer][energy_bin] counts
    uint32_t timestamp;     ///< End-of-window timestamp (µs since boot)
    bool     valid;         ///< True if CRC and sync word verified
};

/**
 * @class FPGA_Interface
 * @brief Handles SPI communication with SEEs FPGA histogram logic.
 */
class FPGA_Interface {
public:
    FPGA_Interface(uint8_t csPin, SPIClass &spiBus = SPI);

    /** @brief Initialize SPI and control lines. */
    void begin();

    /**
     * @brief Retrieve a full histogram frame from the FPGA.
     * @param hist Reference to a HistogramData struct to populate.
     * @return True if valid data received.
     */
    bool getHistogram(HistogramData &hist);

    /**
     * @brief Send configuration command (e.g., integration period).
     */
    void sendCommand(uint8_t cmd, uint16_t value);

private:
    uint8_t  _cs;
    SPIClass *_spi;
    uint8_t  calcCRC(const uint8_t *buf, size_t len);
};