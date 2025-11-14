/**
 * @file SEEs.hpp
 * @brief Science payload firmware driver for the Solar Energetic Events (SEEs) instrument.
 *
 * The SEEs system uses an FPGA front-end to accumulate histograms of particle detections
 * across multiple scintillator layers and energy bins over fixed integration periods.
 * The Teensy serves as the supervisory controller responsible for:
 *  - Initializing communication with the FPGA
 *  - Retrieving histogram frames each integration cycle
 *  - Packaging the data into AERIS-compliant telemetry frames
 *  - Forwarding them to the Dock/OBC via UART
 *
 * This code mirrors the structural and commenting conventions of the VIA (AvaSpec)
 * payload firmware to maintain consistency across all AERIS instruments.
 *
 * @author  
 *  Alexander “Ander” Shultis  
 *  Hawai‘i Space Flight Laboratory (HSFL)  
 *  University of Hawai‘i at Mānoa
 *
 * @date 2025
 */

#pragma once
#include <Arduino.h>
#include "FPGA_Interface.hpp"

/**
 * @class SEEs
 * @brief High-level interface to the SEEs FPGA histogram system.
 *
 * Provides initialization, histogram retrieval, telemetry packetization, and UART
 * transmission functions. The class interfaces with the FPGA_Interface driver,
 * ensuring clean modular separation between hardware and control logic.
 */
class SEEs {
public:
    explicit SEEs(uint8_t csPin);

    /** @brief Initialize UART and FPGA communication. */
    void begin();

    /** @brief Poll FPGA once per integration cycle and handle telemetry dispatch. */
    void update();

private:
    FPGA_Interface fpga;          ///< SPI interface to FPGA front-end
    HistogramData  currentFrame;  ///< Latest histogram frame

    /** @brief Build telemetry packet from histogram data. */
    void buildTelemetry();

    /** @brief Send constructed telemetry over UART to Dock/OBC. */
    void sendTelemetry();

    uint8_t packet[128];          ///< Telemetry packet buffer
};