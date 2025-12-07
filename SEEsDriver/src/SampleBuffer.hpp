/**
 * @file SampleBuffer.hpp
 * @brief RAM-based circular sample buffer for SEEs
 *
 * Stores ALL samples in Teensy 4.1's internal RAM using compact format.
 * No SD card required.
 *
 * Memory: 5 bytes/sample × 100,000 samples = 500 KB
 * Duration: 10 seconds at 10 kS/s
 */

#ifndef SAMPLE_BUFFER_HPP
#define SAMPLE_BUFFER_HPP

#include <Arduino.h>

/**
 * @brief Compact sample record - 5 bytes per sample
 *
 * Stores raw ADC value instead of float voltage.
 * Time is reconstructed from sample index and start time.
 */
struct __attribute__((packed)) CompactSample {
    uint16_t adc_raw;     // 2 bytes - raw 12-bit ADC value (0-4095)
    uint16_t time_delta;  // 2 bytes - microseconds since last sample (0-65535)
    uint8_t hit;          // 1 byte  - hit flag (0 or 1)
};  // Total: 5 bytes, no padding due to __attribute__((packed))

class SampleBuffer {
public:
    static constexpr size_t BUFFER_SECONDS = 10;      // 10 second rolling buffer
    static constexpr size_t SAMPLES_PER_SEC = 10000;  // 10 kS/s
    static constexpr size_t TOTAL_SAMPLES = BUFFER_SECONDS * SAMPLES_PER_SEC;  // 100,000 samples
    static constexpr size_t BUFFER_SIZE_BYTES = TOTAL_SAMPLES * sizeof(CompactSample);  // 500 KB

    SampleBuffer() : _buffer(nullptr), _head(0), _size(0), _lastTimeUs(0), _totalHits(0) {}

    ~SampleBuffer() {
        if (_buffer) {
            delete[] _buffer;
            _buffer = nullptr;
        }
    }

    /**
     * @brief Initialize buffer - allocates RAM
     * @return true if allocation succeeded
     */
    bool begin() {
        _buffer = new (std::nothrow) CompactSample[TOTAL_SAMPLES];

        if (!_buffer) {
            Serial.println("[SampleBuffer] ERROR: Failed to allocate RAM");
            Serial.print("[SampleBuffer]   Requested: ");
            Serial.print(BUFFER_SIZE_BYTES / 1024);
            Serial.println(" KB");
            return false;
        }

        _head = 0;
        _size = 0;
        _lastTimeUs = micros();
        _totalHits = 0;

        Serial.println("[SampleBuffer] Initialized (RAM mode)");
        Serial.print("[SampleBuffer]   Capacity: ");
        Serial.print(TOTAL_SAMPLES);
        Serial.print(" samples (");
        Serial.print(BUFFER_SECONDS);
        Serial.println(" seconds)");
        Serial.print("[SampleBuffer]   Memory: ");
        Serial.print(BUFFER_SIZE_BYTES / 1024);
        Serial.println(" KB");

        return true;
    }

    /**
     * @brief Record a sample
     * @param adc_raw Raw ADC value (0-4095)
     * @param hit Whether this sample is a hit (0 or 1)
     */
    void record(uint16_t adc_raw, uint8_t hit) {
        if (!_buffer) return;

        uint32_t nowUs = micros();
        uint32_t delta = nowUs - _lastTimeUs;
        _lastTimeUs = nowUs;

        // Clamp delta to uint16_t max (65535 µs = 65.5 ms)
        if (delta > 65535) delta = 65535;

        _buffer[_head].adc_raw = adc_raw;
        _buffer[_head].time_delta = (uint16_t)delta;
        _buffer[_head].hit = hit;

        if (hit) _totalHits++;

        _head = (_head + 1) % TOTAL_SAMPLES;
        if (_size < TOTAL_SAMPLES) _size++;
    }

    /**
     * @brief Output snap data to Serial
     *
     * Outputs all buffered samples as CSV, reconstructing timestamps.
     */
    void outputSnap() {
        if (!_buffer || _size == 0) {
            Serial.println("[SampleBuffer] No data available");
            return;
        }

        Serial.println("[SNAP_START]");
        Serial.println("time_ms,voltage_V,hit,total_hits");

        // Find start position (oldest sample)
        size_t start = (_size < TOTAL_SAMPLES) ? 0 : _head;

        // Reconstruct timestamps from deltas
        float time_ms = 0.0f;
        uint32_t runningHits = 0;

        for (size_t i = 0; i < _size; i++) {
            size_t idx = (start + i) % TOTAL_SAMPLES;
            CompactSample& s = _buffer[idx];

            // Accumulate time from deltas
            if (i > 0) {
                time_ms += s.time_delta / 1000.0f;
            }

            // Convert ADC to voltage (3.3V reference, 12-bit ADC)
            float voltage_V = (s.adc_raw / 4095.0f) * 3.3f;

            if (s.hit) runningHits++;

            // Output CSV line
            Serial.print(time_ms, 3);
            Serial.print(',');
            Serial.print(voltage_V, 4);
            Serial.print(',');
            Serial.print(s.hit);
            Serial.print(',');
            Serial.println(runningHits);
        }

        Serial.println("[SNAP_END]");

        Serial.print("[SampleBuffer] Output ");
        Serial.print(_size);
        Serial.println(" samples");
    }

    /**
     * @brief Get current sample count
     */
    size_t size() const { return _size; }

    /**
     * @brief Get total hits recorded
     */
    uint32_t totalHits() const { return _totalHits; }

    /**
     * @brief Clear the buffer
     */
    void clear() {
        _head = 0;
        _size = 0;
        _totalHits = 0;
        _lastTimeUs = micros();
    }

private:
    CompactSample* _buffer;
    size_t _head;
    size_t _size;
    uint32_t _lastTimeUs;
    uint32_t _totalHits;
};

#endif // SAMPLE_BUFFER_HPP
