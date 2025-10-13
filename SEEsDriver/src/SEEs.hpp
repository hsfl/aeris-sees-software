/**
 * @file SEEs.hpp
 * @brief Science payload firmware driver for the Solar Energetic Events (SEEs) instrument.
 *
 * This module defines the SEEs payload class used to interface with the FPGA-based
 * event coincidence logic and transmit formatted telemetry to the Dock/OBC.
 *
 * The SEEs system measures coincident scintillation events across multiple detector layers
 * using a custom FPGA front-end. The Teensy acts as the supervisory controller:
 *  - Initializes communication with the FPGA
 *  - Retrieves event data packets
 *  - Packages them into mission telemetry frames
 *  - Forwards them upstream to the AERIS OBC
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
 * @brief High-level interface to the SEEs detector and FPGA logic.
 *
 * Provides initialization, event acquisition, telemetry packetization, and UART
 * transmission. Mirrors the structure of the VIA (AvaSpec) firmware for consistency
 * across AERIS payloads.
 */
class SEEs {
public:
    explicit SEEs(uint8_t csPin);

    /** @brief Initialize UART and FPGA communication. */
    void begin();

    /** @brief Poll FPGA for new events and handle telemetry dispatch. */
    void update();

private:
    FPGA_Interface fpga;       ///< Interface driver for the FPGA co-processor
    EventData currentEvent;    ///< Container for current event information

    /** @brief Build minimal telemetry payload for uplink. */
    void buildTelemetry();

    /** @brief Send prepared payload over UART to Dock/OBC. */
    void sendTelemetry();

    uint8_t packet[64];        ///< Telemetry packet buffer
};