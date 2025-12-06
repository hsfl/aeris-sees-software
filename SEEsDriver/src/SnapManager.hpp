/**
 * @file SnapManager.hpp
 * @brief Manages snapshot capture from hits-only circular buffer
 *
 * Handles extraction of ±2.5s hit windows from the circular buffer and
 * saves them to timestamped CSV files on SD card.
 */

#ifndef SNAP_MANAGER_HPP
#define SNAP_MANAGER_HPP

#include <Arduino.h>
#include <SD.h>
#include "CircularBuffer.hpp"

/**
 * @brief Manages snapshot capture and file writing
 *
 * Extracts hit time windows from the circular buffer and saves them
 * to discrete, timestamped CSV files on SD card.
 */
class SnapManager {
public:
    /**
     * @brief Construct SnapManager
     * @param windowSeconds Window size in seconds (default ±2.5s)
     * @param outputDir Output directory for snap files (default "snaps/")
     */
    SnapManager(float windowSeconds = 2.5f, const char* outputDir = "snaps/");

    /**
     * @brief Initialize snap manager (call from setup())
     * @param sdAvailable Whether SD card is available
     * @return true if successful
     */
    bool begin(bool sdAvailable);

    /**
     * @brief Capture a snapshot from circular buffer
     * @param buffer Circular buffer to extract from
     * @param triggerTimeUs Trigger timestamp in microseconds
     * @return true if snap was saved successfully, false otherwise
     */
    bool captureSnap(CircularBuffer& buffer, uint32_t triggerTimeUs);

    /**
     * @brief Get number of snaps captured this session
     * @return Snap count
     */
    uint32_t getSnapCount() const { return _snapCount; }

private:
    float _windowSeconds;      ///< Window size (±this many seconds)
    String _outputDir;         ///< Output directory path
    uint32_t _snapCount;       ///< Number of snaps captured
    bool _sdAvailable;         ///< SD card availability flag

    /**
     * @brief Generate filename for snap
     * @param triggerTimeUs Trigger timestamp
     * @return Filename string (e.g., "snap_00001_1234567890.csv")
     */
    String generateFilename(uint32_t triggerTimeUs);

    /**
     * @brief Write hits to CSV file
     * @param filename Output filename
     * @param hits Array of hit records
     * @param count Number of hits
     * @param triggerTimeUs Trigger timestamp for metadata
     * @return true if write successful
     */
    bool writeSnapFile(const String& filename, HitRecord* hits,
                       size_t count, uint32_t triggerTimeUs);
};

#endif // SNAP_MANAGER_HPP
