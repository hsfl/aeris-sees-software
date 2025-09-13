#pragma once
#include <cstddef>
#include <cstdint>

// Raw packet structure coming from FPGA
struct SEEsRawPacket {
    uint32_t timestamp;
    uint16_t bin_counts[4];
    uint16_t coincidence;
    uint16_t flags;
    uint16_t crc;
} __attribute__((packed));

// Telemetry header for framing (expand later if needed)
struct TelemetryHeader {
    uint8_t  source_id;
    uint8_t  mode_flags;
    uint64_t timestamp;
    uint16_t seq;
    uint8_t  reserved[5];
} __attribute__((packed));

// Full telemetry frame
struct TelemetryFrame {
    TelemetryHeader header;
    uint8_t payload[1000];  // contains SEEsRawPacket (for now)
    uint16_t crc;
} __attribute__((packed));

// ---- API ----
uint16_t crc16_ccitt(const uint8_t *data, size_t len);

void sees_ingest(uint8_t byte);
bool sees_poll();
bool sees_next_frame(TelemetryFrame &out);