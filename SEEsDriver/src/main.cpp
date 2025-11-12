/**
 * @file main.cpp
 * @brief Entry point for SEEs payload firmware.
 *
 * Uses SEEs_ADC class for ADC-based detection with command control.
 * For original prototype code, see SEEs_Prototype_Code.cpp (reference).
 *
 * When FPGA hardware is ready, restore the FPGA-based implementation from
 * the DEPRECATED/ folder.
 */

#include "SEEs_ADC.hpp"

// Global SEEs driver instance
SEEs_ADC sees;

void setup() {
    sees.begin();
}

void loop() {
    sees.update();
}