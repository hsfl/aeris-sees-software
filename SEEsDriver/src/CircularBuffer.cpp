/**
 * @file CircularBuffer.cpp
 * @brief Implementation of circular buffer for SEEs detector
 */

#include "CircularBuffer.hpp"

CircularBuffer::CircularBuffer(uint32_t capacitySeconds, uint32_t sampleRateHz)
    : _buffer(nullptr), _capacity(0), _head(0), _size(0) {
    // Calculate required capacity
    _capacity = capacitySeconds * sampleRateHz;
}

CircularBuffer::~CircularBuffer() {
    if (_buffer) {
        delete[] _buffer;
        _buffer = nullptr;
    }
}

bool CircularBuffer::begin() {
    // Allocate buffer memory
    _buffer = new (std::nothrow) DetectorSample[_capacity];

    if (!_buffer) {
        Serial.println("[CircularBuffer] ERROR: Failed to allocate memory");
        Serial.print("[CircularBuffer]   Requested: ");
        Serial.print(_capacity * sizeof(DetectorSample));
        Serial.println(" bytes");
        return false;
    }

    Serial.println("[CircularBuffer] Initialized");
    Serial.print("[CircularBuffer]   Capacity: ");
    Serial.print(_capacity);
    Serial.println(" samples");
    Serial.print("[CircularBuffer]   Memory: ");
    Serial.print((_capacity * sizeof(DetectorSample)) / 1024);
    Serial.println(" KB");

    clear();
    return true;
}

void CircularBuffer::push(const DetectorSample& sample) {
    if (!_buffer) return;

    // Write sample at head position
    _buffer[_head] = sample;

    // Advance head (circular wrap)
    _head = (_head + 1) % _capacity;

    // Update size (saturate at capacity)
    if (_size < _capacity) {
        _size++;
    }
}

size_t CircularBuffer::extractWindow(uint32_t centerTimeUs, float windowSeconds,
                                     DetectorSample* outBuffer, size_t maxSamples) {
    if (!_buffer || !outBuffer || _size == 0) return 0;

    // Calculate time window bounds
    uint32_t windowUs = (uint32_t)(windowSeconds * 1000000.0f);
    uint32_t startTimeUs = centerTimeUs - windowUs;
    uint32_t endTimeUs = centerTimeUs + windowUs;

    size_t extracted = 0;

    // Iterate through all valid samples in buffer
    for (size_t i = 0; i < _size && extracted < maxSamples; i++) {
        size_t idx = physicalIndex(i);
        const DetectorSample& sample = _buffer[idx];

        // Check if sample falls within time window
        if (sample.timestamp >= startTimeUs && sample.timestamp <= endTimeUs) {
            outBuffer[extracted++] = sample;
        }
    }

    return extracted;
}

size_t CircularBuffer::size() const {
    return _size;
}

void CircularBuffer::clear() {
    _head = 0;
    _size = 0;
}

float CircularBuffer::getTimeSpan() const {
    if (_size < 2) return 0.0f;

    // Get oldest and newest samples
    size_t oldestIdx = physicalIndex(0);
    size_t newestIdx = physicalIndex(_size - 1);

    float span_us = (float)(_buffer[newestIdx].timestamp - _buffer[oldestIdx].timestamp);
    return span_us / 1000000.0f;  // Convert to seconds
}

size_t CircularBuffer::physicalIndex(size_t logicalIndex) const {
    if (_size < _capacity) {
        // Buffer not full yet - linear indexing
        return logicalIndex;
    } else {
        // Buffer is full - circular indexing
        // Oldest sample is at _head position
        return (_head + logicalIndex) % _capacity;
    }
}
