/**
 * @file SampleBuffer.hpp
 * @brief SD-card based circular sample buffer for SEEs
 *
 * Stores ALL samples (not just hits) to SD card in a rolling buffer.
 * On snap, reads back the ±2.5s window and outputs to Serial.
 *
 * Storage: ~50KB/sec at 10kS/s with ~50 bytes/line
 * 6 seconds = ~300KB on SD card
 */

#ifndef SAMPLE_BUFFER_HPP
#define SAMPLE_BUFFER_HPP

#include <Arduino.h>
#include "SD.h"

class SampleBuffer {
public:
    static constexpr size_t BUFFER_SECONDS = 5;      // Exactly 5 seconds (±2.5s window)
    static constexpr size_t SAMPLES_PER_SEC = 10000; // 10 kS/s
    static constexpr size_t TOTAL_SAMPLES = BUFFER_SECONDS * SAMPLES_PER_SEC;  // 50000 samples
    static constexpr size_t BYTES_PER_LINE = 40;     // Approximate CSV line length
    static constexpr size_t BUFFER_SIZE = TOTAL_SAMPLES * BYTES_PER_LINE;      // ~2MB on SD

    SampleBuffer() : _file(), _writePos(0), _wrapped(false), _sdAvailable(false) {}

    bool begin(bool sdAvailable) {
        _sdAvailable = sdAvailable;
        if (!_sdAvailable) {
            Serial.println("[SampleBuffer] No SD card - buffer disabled");
            return false;
        }

        // Remove old buffer file
        if (SD.exists("/buffer.csv")) {
            SD.remove("/buffer.csv");
        }

        _file = SD.open("/buffer.csv", FILE_WRITE);
        if (!_file) {
            Serial.println("[SampleBuffer] Failed to create buffer file");
            return false;
        }

        _writePos = 0;
        _wrapped = false;

        Serial.println("[SampleBuffer] Initialized");
        Serial.print("[SampleBuffer]   Size: ");
        Serial.print(BUFFER_SIZE / 1024);
        Serial.println(" KB");

        return true;
    }

    void record(float time_ms, float voltage_V, uint8_t hit, uint32_t total_hits) {
        if (!_sdAvailable || !_file) return;

        // Format the line
        char line[64];
        int len = snprintf(line, sizeof(line), "%.3f,%.4f,%d,%lu\n",
                          time_ms, voltage_V, hit, (unsigned long)total_hits);

        // Write at current position
        _file.seek(_writePos);
        _file.write(line, len);

        _writePos += len;

        // Wrap around if we exceed buffer size
        if (_writePos >= BUFFER_SIZE) {
            _writePos = 0;
            _wrapped = true;
        }

        // Flush periodically (every ~100 samples)
        static int flushCounter = 0;
        if (++flushCounter >= 100) {
            _file.flush();
            flushCounter = 0;
        }
    }

    void outputSnap() {
        if (!_sdAvailable || !_file) {
            Serial.println("[SampleBuffer] No buffer available");
            return;
        }

        _file.flush();

        Serial.println("[SNAP_START]");
        Serial.println("time_ms,voltage_V,hit,total_hits");

        // Calculate how much data we have
        size_t totalBytes = _wrapped ? BUFFER_SIZE : _writePos;
        size_t startPos = _wrapped ? _writePos : 0;

        // Read and output all data in order
        _file.seek(startPos);

        char buf[128];
        size_t bytesRead = 0;
        size_t lineCount = 0;

        while (bytesRead < totalBytes) {
            // Handle wrap-around
            if (_file.position() >= BUFFER_SIZE) {
                _file.seek(0);
            }

            // Read a chunk
            size_t toRead = min(sizeof(buf) - 1, totalBytes - bytesRead);
            if (_file.position() + toRead > BUFFER_SIZE) {
                toRead = BUFFER_SIZE - _file.position();
            }

            size_t n = _file.read(buf, toRead);
            if (n == 0) break;

            buf[n] = '\0';

            // Output character by character, counting lines
            for (size_t i = 0; i < n; i++) {
                Serial.print(buf[i]);
                if (buf[i] == '\n') lineCount++;
            }

            bytesRead += n;
        }

        Serial.println("[SNAP_END]");

        Serial.print("[SampleBuffer] Output ");
        Serial.print(lineCount);
        Serial.println(" samples");
    }

    void close() {
        if (_file) {
            _file.close();
        }
    }

private:
    File _file;
    size_t _writePos;
    bool _wrapped;
    bool _sdAvailable;
};

#endif // SAMPLE_BUFFER_HPP
