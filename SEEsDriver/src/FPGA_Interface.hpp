/**
 * @file FPGA_Interface.hpp
 * @brief Low-level interface for communicating with the SEEs FPGA front-end.
 *
 * Provides SPI communication routines, event frame parsing, CRC verification,
 * and optional command transmission for configuration or diagnostics.
 */

#pragma once
#include <Arduino.h>
#include <SPI.h>

/**
 * @struct EventData
 * @brief Represents a single coincidence event reported by the FPGA.
 */
struct EventData {
    uint32_t timestamp;   ///< Event timestamp (microseconds since boot)
    uint8_t  layer_mask;  ///< Bitmask representing active detector layers
    uint8_t  energy_bin;  ///< Quantized energy classification
    bool     valid;       ///< True if CRC and frame sync are valid
};

/**
 * @class FPGA_Interface
 * @brief SPI-based communication driver for SEEs FPGA logic.
 */
class FPGA_Interface {
public:
    FPGA_Interface(uint8_t csPin, SPIClass &spiBus = SPI);

    /** @brief Initialize SPI and associated control lines. */
    void begin();

    /**
     * @brief Retrieve one event record from the FPGA FIFO buffer.
     * @param evt Reference to an EventData struct to populate.
     * @return True if a valid event was received.
     */
    bool getEvent(EventData &evt);

    /**
     * @brief Send configuration or control command to the FPGA.
     * @param cmd  Command identifier.
     * @param value 16-bit command value.
     */
    void sendCommand(uint8_t cmd, uint16_t value);

private:
    uint8_t _cs;          ///< Chip select pin
    SPIClass *_spi;       ///< SPI bus instance pointer

    /** @brief Simple XOR-based CRC. */
    uint8_t calcCRC(const uint8_t *buf, size_t len);
};