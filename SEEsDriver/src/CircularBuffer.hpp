/**
 * @file CircularBuffer.hpp
 * @brief Hits-only circular buffer for SEEs cosmic ray detection
 *
 * Stores only HIT events (not every sample) - fits in Teensy 4.1's 1MB RAM.
 *
 * BUFFER SIZING:
 * - Time-based: Always keeps exactly BUFFER_DURATION_SEC (30 seconds) of data
 * - Count limit: Max 30,000 hits to cap memory at 240 KB
 * - Whichever limit is hit first triggers eviction
 *
 * POLICE BODY CAM ANALOGY:
 * - Buffer always recording hits (started on power-up)
 * - Snap saves ±2.5s of hits around trigger time (includes PRE-EVENT data)
 * - Buffer keeps rolling after snap (continuous operation)
 */

#ifndef CIRCULAR_BUFFER_HPP
#define CIRCULAR_BUFFER_HPP

#include <Arduino.h>

/**
 * @brief Hit record - only stored when a particle is detected
 *
 * Compact 8-byte structure for memory efficiency.
 * At 1000 hits/sec, 30 seconds = 240 KB (fits in 1MB RAM easily)
 */
struct HitRecord {
    uint32_t timestamp_us;  ///< Absolute timestamp in microseconds
    uint8_t layers;         ///< Layer penetration count (1-4)
    uint8_t reserved[3];    ///< Padding for alignment / future use
};

/**
 * @brief Circular buffer for hit events only
 *
 * Stores hits (not every sample) for memory efficiency.
 * Designed to fit in Teensy 4.1's 1MB internal RAM without PSRAM.
 */
class CircularBuffer {
public:
    /**
     * @brief Construct circular buffer
     * @param maxHits Maximum number of hits to buffer (default 30000)
     */
    CircularBuffer(uint32_t maxHits = 30000);

    /**
     * @brief Destructor - cleanup allocated memory
     */
    ~CircularBuffer();

    /**
     * @brief Initialize the buffer (call from setup())
     * @return true if successful, false on allocation failure
     */
    bool begin();

    /**
     * @brief Record a hit event
     * @param timestamp_us Timestamp in microseconds (from micros())
     * @param layers Layer penetration count (1-4)
     */
    void recordHit(uint32_t timestamp_us, uint8_t layers);

    /**
     * @brief Extract hits in a time window around a center point
     * @param centerTimeUs Center time in microseconds
     * @param windowSeconds Window size in seconds (±windowSeconds around center)
     * @param outBuffer Output buffer to store extracted hits
     * @param maxHits Maximum hits to extract
     * @return Number of hits extracted
     */
    size_t extractWindow(uint32_t centerTimeUs, float windowSeconds,
                         HitRecord* outBuffer, size_t maxHits);

    /**
     * @brief Get current number of hits in buffer
     */
    size_t size() const { return _size; }

    /**
     * @brief Get buffer capacity
     */
    size_t capacity() const { return _capacity; }

    /**
     * @brief Check if buffer is full
     */
    bool isFull() const { return _size >= _capacity; }

    /**
     * @brief Clear all hits from buffer
     */
    void clear();

private:
    HitRecord* _buffer;   ///< Dynamic array for hits
    size_t _capacity;     ///< Maximum hits buffer can hold
    size_t _head;         ///< Write position
    size_t _size;         ///< Current number of valid hits

    /**
     * @brief Get physical index from logical index
     */
    size_t physicalIndex(size_t logicalIndex) const;
};

#endif // CIRCULAR_BUFFER_HPP
