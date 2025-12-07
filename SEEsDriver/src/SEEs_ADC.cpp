/**
 * @file SEEs_ADC.cpp
 * @brief Implementation of SEEs ADC-based detector driver
 *
 * Body cam mode - always recording to RAM buffer.
 * No SD card required.
 */

#include "SEEs_ADC.hpp"

SEEs_ADC::SEEs_ADC(uint8_t adcPin, uint8_t ledPin)
    : _adcPin(adcPin), _ledPin(ledPin),
      _armed(true), _ledState(false),
      _t0_us(0), _next_sample_us(0), _lastBlink(0), _last_hit_us(0),
      _totalHits(0), _countsPerVolt(0) {}

void SEEs_ADC::begin() {
    pinMode(_ledPin, OUTPUT);
    digitalWrite(_ledPin, HIGH);  // Solid ON during init

    Serial.begin(115200);
    delay(500);

    Serial.println("[SEEs] ====================================");
    Serial.println("[SEEs] SEEs Particle Detector - Starting");
    Serial.println("[SEEs] ====================================");

    // Initialize RAM-based sample buffer
    Serial.println("[SEEs] Initializing sample buffer...");
    if (!_sampleBuffer.begin()) {
        Serial.println("[SEEs] ERROR: Failed to allocate buffer!");
        Serial.println("[SEEs] System cannot continue - halting");
        while (1) {
            digitalWrite(_ledPin, millis() % 200 < 100);  // Fast blink = error
            delay(10);
        }
    }

    Serial.println("[SEEs] Body cam mode: ALWAYS streaming");
    Serial.println("[SEEs] Commands: snap");
    Serial.println("[SEEs] Data format: time_ms,voltage_V,hit,total_hits");

    // Configure ADC
    analogReadResolution(ADC_BITS);
    analogReadAveraging(ADC_AVG_HW);
    (void)analogRead(_adcPin);  // Warm-up read

    // Initialize timing
    _next_sample_us = micros();
    _lastBlink = millis();
    _t0_us = micros();

    _countsPerVolt = ADC_VREF / ((1UL << ADC_BITS) - 1UL);

    Serial.println("[SEEs] ====================================");
    Serial.println("[SEEs] Ready - buffer recording started");
    Serial.println("[SEEs] ====================================");
}

void SEEs_ADC::update() {
    // Check for serial commands
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        processCommand(cmd);
    }

    // Update LED state
    updateLED();

    // ALWAYS sample into buffer (body cam mode)
    sampleAndStream();
}

void SEEs_ADC::processCommand(const String& cmd) {
    String cmdLower = cmd;
    cmdLower.trim();
    cmdLower.toLowerCase();

    if (cmdLower == "snap") {
        Serial.println("[SEEs] SNAP command received");
        Serial.println("[SEEs] Waiting 2.5s for post-trigger data...");

        // Continue sampling for exactly 2.5s post-trigger
        uint32_t endTime = millis() + 2500;
        while (millis() < endTime) {
            sampleAndStream();
        }

        // Output all buffered samples
        _sampleBuffer.outputSnap();
        Serial.println("[SEEs] Snap complete");
    }
    else if (cmdLower.length() > 0) {
        Serial.print("[SEEs] Unknown command: ");
        Serial.println(cmd);
    }
}

void SEEs_ADC::updateLED() {
    // Always blink - body cam mode is always active
    uint32_t now = millis();
    if (now - _lastBlink >= BLINK_MS) {
        _ledState = !_ledState;
        digitalWrite(_ledPin, _ledState);
        _lastBlink = now;
    }
}

void SEEs_ADC::sampleAndStream() {
    // Timing check
    uint32_t now_us = micros();
    if ((int32_t)(now_us - _next_sample_us) < 0) return;
    _next_sample_us += SAMPLE_US;

    // Read ADC
    uint16_t raw = analogRead(_adcPin);
    float v = raw * _countsPerVolt;

    // Windowed detection with hysteresis + refractory
    uint8_t hit = 0;
    if (_armed) {
        if (v >= LOWER_ENTER_V && v <= UPPER_LIMIT_V &&
            (now_us - _last_hit_us) >= REFRACT_US) {
            hit = 1;
            ++_totalHits;
            _last_hit_us = now_us;
            _armed = false;  // Disarm until voltage drops
        }
    } else {
        if (v < LOWER_EXIT_V) {
            _armed = true;  // Re-arm
        }
    }

    // Record to RAM buffer (compact format)
    _sampleBuffer.record(raw, hit);

    // Stream to Serial (body cam mode)
    float t_ms = (now_us - _t0_us) / 1000.0f;
    Serial.print(t_ms, 3); Serial.print(',');
    Serial.print(v, 4);    Serial.print(',');
    Serial.print(hit);     Serial.print(',');
    Serial.println(_totalHits);
}
