/**
 * @file SEEs_ADC.hpp
 * @brief SEEs ADC-based detector driver with command control
 *
 * Provides snap command interface for SiPM data collection.
 * Body cam mode - always recording to RAM buffer.
 */

#ifndef SEES_ADC_HPP
#define SEES_ADC_HPP

#include <Arduino.h>
#include "SampleBuffer.hpp"

class SEEs_ADC {
public:
    /**
     * @brief Construct SEEs ADC driver
     * @param adcPin ADC pin for SiPM input (default A0)
     * @param ledPin LED pin for status (default 13)
     */
    SEEs_ADC(uint8_t adcPin = A0, uint8_t ledPin = 13);

    /**
     * @brief Initialize hardware and serial communication
     */
    void begin();

    /**
     * @brief Main update loop - call repeatedly from loop()
     */
    void update();

    /**
     * @brief Process a command from serial input
     * @param cmd Command string ("snap")
     */
    void processCommand(const String& cmd);

private:
    // Pin configuration
    uint8_t _adcPin;
    uint8_t _ledPin;

    // Configuration constants
    static constexpr uint32_t SAMPLE_US = 100;       // 10 kS/s
    static constexpr uint32_t BLINK_MS = 500;
    static constexpr int ADC_BITS = 12;
    static constexpr int ADC_AVG_HW = 1;
    static constexpr float ADC_VREF = 3.3f;

    // Detection window (volts)
    static constexpr float LOWER_ENTER_V = 0.30f;
    static constexpr float LOWER_EXIT_V = 0.300f;
    static constexpr float UPPER_LIMIT_V = 0.800f;
    static constexpr uint32_t REFRACT_US = 300;

    // State variables
    bool _armed;
    bool _ledState;

    uint32_t _t0_us;
    uint32_t _next_sample_us;
    uint32_t _lastBlink;
    uint32_t _last_hit_us;
    uint32_t _totalHits;

    float _countsPerVolt;

    // RAM-based sample buffer (no SD required)
    SampleBuffer _sampleBuffer;

    // Private methods
    void updateLED();
    void sampleAndStream();
};

#endif // SEES_ADC_HPP
