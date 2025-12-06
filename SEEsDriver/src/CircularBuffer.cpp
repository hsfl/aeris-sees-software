/**
 * @file CircularBuffer.cpp
 * @brief Implementation of hits-only circular buffer
 */

#include "CircularBuffer.hpp"

CircularBuffer::CircularBuffer(uint32_t maxHits)
    : _buffer(nullptr), _capacity(maxHits), _head(0), _size(0) {
}

CircularBuffer::~CircularBuffer() {
    if (_buffer) {
        delete[] _buffer;
        _buffer = nullptr;
    }
}

bool CircularBuffer::begin() {
    _buffer = new (std::nothrow) HitRecord[_capacity];

    if (!_buffer) {
        Serial.println("[CircularBuffer] ERROR: Failed to allocate memory");
        Serial.print("[CircularBuffer]   Requested: ");
        Serial.print(_capacity * sizeof(HitRecord));
        Serial.println(" bytes");
        return false;
    }

    Serial.println("[CircularBuffer] Initialized (hits-only mode)");
    Serial.print("[CircularBuffer]   Capacity: ");
    Serial.print(_capacity);
    Serial.println(" hits");
    Serial.print("[CircularBuffer]   Memory: ");
    Serial.print((_capacity * sizeof(HitRecord)) / 1024);
    Serial.println(" KB");

    clear();
    return true;
}

void CircularBuffer::recordHit(uint32_t timestamp_us, uint8_t layers) {
    if (!_buffer) return;

    // Write hit at head position
    _buffer[_head].timestamp_us = timestamp_us;
    _buffer[_head].layers = layers;

    // Advance head (circular wrap)
    _head = (_head + 1) % _capacity;

    // Update size (saturate at capacity)
    if (_size < _capacity) {
        _size++;
    }
}

size_t CircularBuffer::extractWindow(uint32_t centerTimeUs, float windowSeconds,
                                     HitRecord* outBuffer, size_t maxHits) {
    if (!_buffer || !outBuffer || _size == 0) return 0;

    // Calculate time window bounds
    uint32_t windowUs = (uint32_t)(windowSeconds * 1000000.0f);
    uint32_t startTimeUs = (centerTimeUs > windowUs) ? (centerTimeUs - windowUs) : 0;
    uint32_t endTimeUs = centerTimeUs + windowUs;

    size_t extracted = 0;

    // Iterate through all valid hits in buffer
    for (size_t i = 0; i < _size && extracted < maxHits; i++) {
        size_t idx = physicalIndex(i);
        const HitRecord& hit = _buffer[idx];

        // Check if hit falls within time window
        if (hit.timestamp_us >= startTimeUs && hit.timestamp_us <= endTimeUs) {
            outBuffer[extracted++] = hit;
        }
    }

    return extracted;
}

void CircularBuffer::clear() {
    _head = 0;
    _size = 0;
}

size_t CircularBuffer::physicalIndex(size_t logicalIndex) const {
    if (_size < _capacity) {
        return logicalIndex;
    } else {
        return (_head + logicalIndex) % _capacity;
    }
}
