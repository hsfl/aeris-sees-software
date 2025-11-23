/**
 * @file SnapManager.cpp
 * @brief Implementation of snapshot capture manager
 */

#include "SnapManager.hpp"

SnapManager::SnapManager(float windowSeconds, const char* outputDir)
    : _windowSeconds(windowSeconds), _outputDir(outputDir),
      _snapCount(0), _sdAvailable(false) {}

bool SnapManager::begin(bool sdAvailable) {
    _sdAvailable = sdAvailable;

    if (!_sdAvailable) {
        Serial.println("[SnapManager] WARNING: SD card not available - snaps will fail");
        return false;
    }

    // Create output directory if it doesn't exist
    if (!SD.exists(_outputDir.c_str())) {
        if (SD.mkdir(_outputDir.c_str())) {
            Serial.print("[SnapManager] Created directory: ");
            Serial.println(_outputDir);
        } else {
            Serial.print("[SnapManager] WARNING: Failed to create directory: ");
            Serial.println(_outputDir);
            return false;
        }
    }

    Serial.println("[SnapManager] Initialized");
    Serial.print("[SnapManager]   Window: ±");
    Serial.print(_windowSeconds, 1);
    Serial.println(" seconds");
    Serial.print("[SnapManager]   Output: ");
    Serial.println(_outputDir);

    return true;
}

bool SnapManager::captureSnap(CircularBuffer& buffer, uint32_t triggerTimeUs) {
    if (!_sdAvailable) {
        Serial.println("[SnapManager] ERROR: SD card not available");
        return false;
    }

    if (buffer.size() == 0) {
        Serial.println("[SnapManager] ERROR: Buffer is empty");
        return false;
    }

    // Allocate temporary extraction buffer
    // Worst case: ±2.5s @ 10kHz = 50,000 samples
    const size_t maxSamples = (size_t)(_windowSeconds * 2.0f * 10000.0f);
    DetectorSample* samples = new (std::nothrow) DetectorSample[maxSamples];

    if (!samples) {
        Serial.println("[SnapManager] ERROR: Failed to allocate extraction buffer");
        return false;
    }

    // Extract window from circular buffer
    Serial.print("[SnapManager] Extracting ±");
    Serial.print(_windowSeconds, 1);
    Serial.println("s window...");

    size_t count = buffer.extractWindow(triggerTimeUs, _windowSeconds, samples, maxSamples);

    if (count == 0) {
        Serial.println("[SnapManager] WARNING: No samples in time window");
        delete[] samples;
        return false;
    }

    Serial.print("[SnapManager]   Extracted ");
    Serial.print(count);
    Serial.println(" samples");

    // Generate filename and write to SD
    String filename = generateFilename(triggerTimeUs);
    bool success = writeSnapFile(filename, samples, count, triggerTimeUs);

    delete[] samples;

    if (success) {
        _snapCount++;
        Serial.print("[SnapManager] ✓ Snap saved: ");
        Serial.println(filename);
    }

    return success;
}

String SnapManager::generateFilename(uint32_t triggerTimeUs) {
    char filename[64];

    // Format: snap_NNNNN_TTTTTTTTTT.csv
    // NNNNN = snap counter (5 digits)
    // TTTTTTTTTT = trigger timestamp in microseconds (10 digits)
    snprintf(filename, sizeof(filename), "%ssnap_%05lu_%010lu.csv",
             _outputDir.c_str(), _snapCount, triggerTimeUs);

    return String(filename);
}

bool SnapManager::writeSnapFile(const String& filename, DetectorSample* samples,
                                 size_t count, uint32_t triggerTimeUs) {
    File snapFile = SD.open(filename.c_str(), FILE_WRITE);

    if (!snapFile) {
        Serial.print("[SnapManager] ERROR: Failed to open file: ");
        Serial.println(filename);
        return false;
    }

    // Write header with metadata
    snapFile.print("# SEEs Snapshot - Captured at: ");
    snapFile.print(triggerTimeUs / 1000000.0, 6);
    snapFile.println(" seconds");

    snapFile.print("# Window: ±");
    snapFile.print(_windowSeconds, 1);
    snapFile.print(" seconds (");
    snapFile.print(_windowSeconds * 2.0, 1);
    snapFile.println(" seconds total)");

    snapFile.print("# Samples: ");
    snapFile.println(count);

    snapFile.println("# Format: time_ms,voltage_V,hit,layers,cum_counts,timestamp_us");

    // Write CSV header
    snapFile.println("time_ms,voltage_V,hit,layers,cum_counts,timestamp_us");

    // Write all samples
    for (size_t i = 0; i < count; i++) {
        const DetectorSample& s = samples[i];

        snapFile.print(s.time_ms, 3);
        snapFile.print(',');
        snapFile.print(s.voltage, 4);
        snapFile.print(',');
        snapFile.print(s.hit);
        snapFile.print(',');
        snapFile.print(s.layers);
        snapFile.print(',');
        snapFile.print(s.cum_counts);
        snapFile.print(',');
        snapFile.println(s.timestamp);
    }

    snapFile.flush();
    snapFile.close();

    return true;
}
