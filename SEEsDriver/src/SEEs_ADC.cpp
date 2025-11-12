/**
 * @file SEEs_ADC.cpp
 * @brief Implementation of SEEs ADC-based detector driver
 */

#include "SEEs_ADC.hpp"

SEEs_ADC::SEEs_ADC(uint8_t adcPin, uint8_t ledPin)
    : _adcPin(adcPin), _ledPin(ledPin),
      _isCollecting(false), _sdAvailable(false), _armed(true), _ledState(false),
      _t0_us(0), _next_sample_us(0), _lastBlink(0), _last_hit_us(0),
      _cum_counts(0), _lines_since_flush(0), _countsPerVolt(0),
      _bufferFilename("buffer.csv") {}

void SEEs_ADC::begin() {
    pinMode(_ledPin, OUTPUT);
    digitalWrite(_ledPin, HIGH);  // Solid ON when idle

    Serial.begin(115200);
    delay(500);

    // Try to initialize SD card
    _sdAvailable = SD.begin(BUILTIN_SDCARD);
    if (_sdAvailable) {
        Serial.println("[SEEs] SD card ready");
    } else {
        Serial.println("[SEEs] Warning: SD card not found");
    }

    Serial.println("[SEEs] Command-based streaming mode");
    Serial.println("[SEEs] Commands: on, off, snap");
    Serial.println("[SEEs] Data format: time_ms,voltage_V,hit,cum_counts");

    // Configure ADC
    analogReadResolution(ADC_BITS);
    analogReadAveraging(ADC_AVG_HW);
    (void)analogRead(_adcPin);  // Warm-up read

    // Initialize timing
    _next_sample_us = micros();
    _lastBlink = millis();

    _countsPerVolt = ADC_VREF / ((1UL << ADC_BITS) - 1UL);

    Serial.println("[SEEs] Ready - waiting for commands");
}

void SEEs_ADC::update() {
    // Check for serial commands
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        processCommand(cmd);
    }

    // Update LED state
    updateLED();

    // Only sample if collecting
    if (_isCollecting) {
        sampleAndStream();
    }
}

void SEEs_ADC::processCommand(const String& cmd) {
    String cmdLower = cmd;
    cmdLower.trim();
    cmdLower.toLowerCase();

    if (cmdLower == "on") {
        if (!_isCollecting) {
            _isCollecting = true;
            _t0_us = micros();   // Reset time origin
            _cum_counts = 0;      // Reset counter
            _armed = true;        // Reset detection state
            Serial.println("[SEEs] Collection ON");

            // Open rolling buffer file on SD
            if (_sdAvailable) {
                if (_bufferFile) _bufferFile.close();
                if (SD.exists(_bufferFilename.c_str())) {
                    SD.remove(_bufferFilename.c_str());
                }
                _bufferFile = SD.open(_bufferFilename.c_str(), FILE_WRITE);
                if (_bufferFile) {
                    _bufferFile.println("time_ms,voltage_V,hit,cum_counts");
                }
            }
        }
    }
    else if (cmdLower == "off") {
        if (_isCollecting) {
            _isCollecting = false;
            Serial.println("[SEEs] Collection OFF");
            if (_bufferFile) {
                _bufferFile.flush();
                _bufferFile.close();
            }
        }
    }
    else if (cmdLower == "snap") {
        Serial.println("[SEEs] SNAP command received");
        // Python script will handle extracting from circular buffer
    }
    else if (cmdLower.length() > 0) {
        Serial.print("[SEEs] Unknown command: ");
        Serial.println(cmd);
    }
}

void SEEs_ADC::updateLED() {
    if (_isCollecting) {
        // Blink while collecting
        uint32_t now = millis();
        if (now - _lastBlink >= BLINK_MS) {
            _ledState = !_ledState;
            digitalWrite(_ledPin, _ledState);
            _lastBlink = now;
        }
    } else {
        // Solid ON when idle
        digitalWrite(_ledPin, HIGH);
    }
}

void SEEs_ADC::sampleAndStream() {
    // Timing check
    uint32_t now_us = micros();
    if ((int32_t)(now_us - _next_sample_us) < 0) return;
    _next_sample_us += SAMPLE_US;

    // Read ADC and convert to voltage
    int raw = analogRead(_adcPin);
    float v = raw * _countsPerVolt;

    // Windowed detection with hysteresis + refractory
    uint8_t hit = 0;
    if (_armed) {
        if (v >= LOWER_ENTER_V && v <= UPPER_LIMIT_V &&
            (now_us - _last_hit_us) >= REFRACT_US) {
            hit = 1;
            ++_cum_counts;
            _last_hit_us = now_us;
            _armed = false;  // Disarm until voltage drops
        }
    } else {
        if (v < LOWER_EXIT_V) {
            _armed = true;  // Re-arm
        }
    }

    // Timestamp since collection started
    float t_ms = (now_us - _t0_us) / 1000.0f;

    // Stream to Serial
    Serial.print(t_ms, 3); Serial.print(',');
    Serial.print(v, 4);    Serial.print(',');
    Serial.print(hit);     Serial.print(',');
    Serial.println(_cum_counts);

    // Write to SD buffer
    if (_sdAvailable && _bufferFile) {
        _bufferFile.print(t_ms, 3); _bufferFile.print(',');
        _bufferFile.print(v, 4);    _bufferFile.print(',');
        _bufferFile.print(hit);     _bufferFile.print(',');
        _bufferFile.println(_cum_counts);

        if (++_lines_since_flush >= FLUSH_EVERY) {
            _bufferFile.flush();
            _lines_since_flush = 0;
        }
    }
}
