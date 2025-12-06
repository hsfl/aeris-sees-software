/**
 * @file SnapManager.cpp
 * @brief Implementation of snapshot capture manager (hits-only)
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
    Serial.print("[SnapManager]   Window: +/-");
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
    // Max ~5000 hits in a 5s window during extreme burst (1000 hits/s)
    const size_t maxHits = 5000;
    HitRecord* hits = new (std::nothrow) HitRecord[maxHits];

    if (!hits) {
        Serial.println("[SnapManager] ERROR: Failed to allocate extraction buffer");
        return false;
    }

    // Extract window from circular buffer
    Serial.print("[SnapManager] Extracting +/-");
    Serial.print(_windowSeconds, 1);
    Serial.println("s window...");

    size_t count = buffer.extractWindow(triggerTimeUs, _windowSeconds, hits, maxHits);

    Serial.print("[SnapManager]   Extracted ");
    Serial.print(count);
    Serial.println(" hits");

    // Send snap data over Serial (always - for RPi to capture)
    Serial.println("[SNAP_START]");
    Serial.print("# Trigger: ");
    Serial.println(triggerTimeUs);
    Serial.print("# Window: ");
    Serial.println(_windowSeconds, 1);
    Serial.print("# Hits: ");
    Serial.println(count);
    Serial.println("timestamp_us,layers");
    for (size_t i = 0; i < count; i++) {
        Serial.print(hits[i].timestamp_us);
        Serial.print(',');
        Serial.println(hits[i].layers);
    }
    Serial.println("[SNAP_END]");

    // Write to SD if available
    bool success = false;
    if (_sdAvailable) {
        String filename = generateFilename(triggerTimeUs);
        success = writeSnapFile(filename, hits, count, triggerTimeUs);
        if (success) {
            Serial.print("[SnapManager] SD saved: ");
            Serial.println(filename);
        }
    }

    delete[] hits;
    _snapCount++;

    return true;  // Snap was sent over serial even if SD failed
}

String SnapManager::generateFilename(uint32_t triggerTimeUs) {
    char filename[64];

    // Format: snap_NNNNN_TTTTTTTTTT.csv
    snprintf(filename, sizeof(filename), "%ssnap_%05lu_%010lu.csv",
             _outputDir.c_str(), _snapCount, triggerTimeUs);

    return String(filename);
}

bool SnapManager::writeSnapFile(const String& filename, HitRecord* hits,
                                 size_t count, uint32_t triggerTimeUs) {
    File snapFile = SD.open(filename.c_str(), FILE_WRITE);

    if (!snapFile) {
        Serial.print("[SnapManager] ERROR: Failed to open file: ");
        Serial.println(filename);
        return false;
    }

    // Write header with metadata
    snapFile.print("# SEEs Snap - Trigger: ");
    snapFile.print(triggerTimeUs / 1000000.0, 6);
    snapFile.println(" seconds");

    snapFile.print("# Window: +/-");
    snapFile.print(_windowSeconds, 1);
    snapFile.print(" seconds (");
    snapFile.print(_windowSeconds * 2.0, 1);
    snapFile.println(" seconds total)");

    snapFile.print("# Hits: ");
    snapFile.println(count);

    // Write CSV header
    snapFile.println("timestamp_us,layers");

    // Write all hits
    for (size_t i = 0; i < count; i++) {
        const HitRecord& h = hits[i];
        snapFile.print(h.timestamp_us);
        snapFile.print(',');
        snapFile.println(h.layers);
    }

    snapFile.flush();
    snapFile.close();

    return true;
}
