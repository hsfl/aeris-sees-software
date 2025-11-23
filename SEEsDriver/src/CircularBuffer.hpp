/**
 * @file CircularBuffer.hpp
 * @brief 30-second circular buffer for SEEs cosmic ray detection
 *
 * Implements a rolling FIFO buffer that continuously stores the last 30 seconds
 * of detector data, enabling "snap" extraction of ±2.5s windows around events.
 *
 * POLICE BODY CAM ANALOGY:
 * - Buffer is always recording (started on power-up)
 * - Snap saves ±2.5s around trigger time (includes PRE-EVENT data)
 * - Buffer keeps rolling after snap (continuous operation)
 */

#ifndef CIRCULAR_BUFFER_HPP
#define CIRCULAR_BUFFER_HPP

#include <Arduino.h>
#include <SD.h>

/**
 * @brief Sample data structure stored in circular buffer
 */
struct DetectorSample {
    float time_ms;        ///< Timestamp relative to buffer start (ms)
    float voltage;        ///< ADC voltage reading (V)
    uint8_t hit;          ///< Hit flag (0 or 1)
    uint8_t layers;       ///< Layer penetration count (1-4, future FPGA use)
    uint32_t cum_counts;  ///< Cumulative hit counter
    uint32_t timestamp;   ///< Absolute timestamp (micros())
};

/**
 * @brief Circular buffer for continuous detector data storage
 *
 * Stores the last 30 seconds of detector samples in a ring buffer.
 * When buffer is full, oldest samples are overwritten by newest samples.
 */
class CircularBuffer {
public:
    /**
     * @brief Construct circular buffer
     * @param capacitySeconds Buffer capacity in seconds (default 30s)
     * @param sampleRateHz Sample rate in Hz (default 10000 Hz)
     */
    CircularBuffer(uint32_t capacitySeconds = 30, uint32_t sampleRateHz = 10000);

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
     * @brief Add a sample to the circular buffer
     * @param sample Sample data to store
     */
    void push(const DetectorSample& sample);

    /**
     * @brief Extract samples in a time window around a center point
     * @param centerTimeUs Center time in microseconds (absolute timestamp)
     * @param windowSeconds Window size in seconds (±windowSeconds around center)
     * @param outBuffer Output buffer to store extracted samples
     * @param maxSamples Maximum samples to extract
     * @return Number of samples extracted
     */
    size_t extractWindow(uint32_t centerTimeUs, float windowSeconds,
                         DetectorSample* outBuffer, size_t maxSamples);

    /**
     * @brief Get current number of samples in buffer
     * @return Number of valid samples (0 to capacity)
     */
    size_t size() const;

    /**
     * @brief Get buffer capacity
     * @return Maximum number of samples buffer can hold
     */
    size_t capacity() const { return _capacity; }

    /**
     * @brief Check if buffer is full
     * @return true if buffer has reached capacity
     */
    bool isFull() const { return _size >= _capacity; }

    /**
     * @brief Clear all samples from buffer
     */
    void clear();

    /**
     * @brief Get time span currently stored in buffer
     * @return Time span in seconds (0 if empty)
     */
    float getTimeSpan() const;

private:
    DetectorSample* _buffer;  ///< Dynamic array for samples
    size_t _capacity;         ///< Maximum samples buffer can hold
    size_t _head;             ///< Write position (next sample goes here)
    size_t _size;             ///< Current number of valid samples

    /**
     * @brief Get actual buffer index from logical index
     * @param logicalIndex Logical position (0 = oldest sample)
     * @return Physical index in _buffer array
     */
    size_t physicalIndex(size_t logicalIndex) const;
};

#endif // CIRCULAR_BUFFER_HPP
