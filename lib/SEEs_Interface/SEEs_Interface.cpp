#include "SEEs_Interface.hpp"
#include <cstring>

// -------------------------
// CRC16 CCITT (X.25 variant)
// -------------------------
uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000)
                crc = (crc << 1) ^ 0x1021;
            else
                crc <<= 1;
        }
    }
    return crc;
}

// -------------------------
// Internal ring buffer
// -------------------------
static constexpr size_t RBUF_SIZE = 512;
static uint8_t ringbuf[RBUF_SIZE];
static size_t head = 0;
static size_t tail = 0;

static inline bool rbuf_empty() { return head == tail; }
static inline bool rbuf_full()  { return ((head + 1) % RBUF_SIZE) == tail; }

static void rbuf_push(uint8_t b) {
    if (!rbuf_full()) {
        ringbuf[head] = b;
        head = (head + 1) % RBUF_SIZE;
    }
}

static bool rbuf_pop(uint8_t &b) {
    if (rbuf_empty()) return false;
    b = ringbuf[tail];
    tail = (tail + 1) % RBUF_SIZE;
    return true;
}

// -------------------------
// SEEs Interface state
// -------------------------
static SEEsRawPacket pkt_accum;
static size_t pkt_index = 0;
static bool packet_ready = false;

void sees_ingest(uint8_t byte) {
    rbuf_push(byte);
}

bool sees_poll() {
    // Try to assemble a packet from buffer
    while (!rbuf_empty() && !packet_ready) {
        uint8_t b;
        rbuf_pop(b);

        reinterpret_cast<uint8_t*>(&pkt_accum)[pkt_index++] = b;

        if (pkt_index >= sizeof(SEEsRawPacket)) {
            // Full packet received
            uint16_t crc_calc = crc16_ccitt(reinterpret_cast<uint8_t*>(&pkt_accum),
                                            sizeof(SEEsRawPacket) - 2);

            if (crc_calc == pkt_accum.crc) {
                packet_ready = true;
            }
            pkt_index = 0;  // reset regardless
        }
    }
    return packet_ready;
}

bool sees_next_frame(TelemetryFrame &out) {
    if (!packet_ready) return false;

    static uint16_t seq_counter = 0;

    // Build telemetry frame
    out.header.source_id = 1;
    out.header.mode_flags = 0;
    out.header.timestamp = pkt_accum.timestamp;
    out.header.seq = seq_counter++;
    memset(out.header.reserved, 0, sizeof(out.header.reserved));

    memcpy(out.payload, &pkt_accum, sizeof(SEEsRawPacket));

    out.crc = crc16_ccitt(reinterpret_cast<uint8_t*>(&out),
                          sizeof(TelemetryHeader) + sizeof(SEEsRawPacket));

    packet_ready = false;
    return true;
}