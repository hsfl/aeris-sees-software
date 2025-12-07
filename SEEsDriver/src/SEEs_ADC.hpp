/**
 * @file SEEs_ADC.hpp
 * @brief SEEs ADC-based detector driver with command control
 *
 * Provides on/off/snap command interface for SiPM data collection.
 * Based on SEEs_Prototype_Code.cpp but refactored into proper OOP structure.
 */

#ifndef SEES_ADC_HPP
#define SEES_ADC_HPP

#include <Arduino.h>
#include <SD.h>
#include "CircularBuffer.hpp"
#include "SnapManager.hpp"
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
     * @param cmd Command string ("on", "off", "snap")
     */
    void processCommand(const String& cmd);

    /**
     * @brief Check if currently collecting data
     * @return true if collecting, false if idle
     */
    bool isCollecting() const { return _isCollecting; }

private:
    // Pin configuration
    uint8_t _adcPin;
    uint8_t _ledPin;

    // Configuration constants
    static constexpr uint32_t SAMPLE_US = 100;       // 10 kS/s
    static constexpr uint32_t BLINK_MS = 500;
    static constexpr uint32_t FLUSH_EVERY = 100;
    static constexpr int ADC_BITS = 12;
    static constexpr int ADC_AVG_HW = 1;
    static constexpr float ADC_VREF = 3.3f;

    // Detection window (volts)
    static constexpr float LOWER_ENTER_V = 0.30f;
    static constexpr float LOWER_EXIT_V = 0.300f;
    static constexpr float UPPER_LIMIT_V = 0.800f;
    static constexpr uint32_t REFRACT_US = 300;

    // State variables
    bool _isCollecting;
    bool _sdAvailable;
    bool _armed;
    bool _ledState;

    uint32_t _t0_us;
    uint32_t _next_sample_us;
    uint32_t _lastBlink;
    uint32_t _last_hit_us;
    uint32_t _totalHits;
    uint32_t _lines_since_flush;

    float _countsPerVolt;

    File _bufferFile;
    String _bufferFilename;

    // Circular buffer and snap management
    CircularBuffer _circularBuffer;
    SnapManager _snapManager;
    SampleBuffer _sampleBuffer;

    // Private methods
    void updateLED();
    void sampleAndStream();
    String formatCSVLine(float t_ms, float v, uint8_t hit, uint32_t counts);
};

#endif // SEES_ADC_HPP
