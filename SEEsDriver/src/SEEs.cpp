#include "SEEs.hpp"

// ============================================================================
//  SEEs INTEGRATION DRIVER
//  ---------------------------------------------------------------------------
//  Purpose:
//      Runs a self-contained test of the SEEs packet ingestion pipeline.
//      Generates synthetic SEEsRawPackets, pushes them into the parser,
//      and prints decoded telemetry results to the serial console.
//
//  Behavior Summary:
//      - The onboard LED (pin 13) blinks to indicate system liveness.
//      - Each loop cycle fabricates a fake SEEsRawPacket with randomized data.
//      - The packet is byte-streamed into sees_ingest() as if arriving from
//        an external detector.
//      - Once a complete frame is parsed, the decoded results are displayed.
//
//  Notes:
//      This harness operates without actual sensor hardware. It is designed
//      for interface and logic verification during early development phases.
// ============================================================================

namespace SEEs {

// ──────────────────────────────────────────────────────────────
//  initialize()
//  ---------------------------------------------------------------------------
//  Hardware setup and test start banner.
// ──────────────────────────────────────────────────────────────
void initialize() {
    pinMode(13, OUTPUT);          // Onboard LED as heartbeat
    Serial.begin(115200);         // USB serial for debug
    delay(2000);                  // Allow host to connect
    Serial.println("SEEs Integration Test starting...");
}

// ──────────────────────────────────────────────────────────────
//  run_cycle()
//  ---------------------------------------------------------------------------
//  Executes one test cycle:
//      1. Toggles LED (visual heartbeat)
//      2. Generates a synthetic SEEsRawPacket
//      3. Streams bytes through the ingestion interface
//      4. Polls for parsed telemetry frames
//      5. Prints decoded packet contents
// ──────────────────────────────────────────────────────────────
void run_cycle() {
    // 1. Toggle LED for heartbeat
    digitalWrite(13, !digitalRead(13));
    delay(500);

    // 2. Construct synthetic SEEsRawPacket
    SEEsRawPacket pkt{};               // Zero-initialize structure
    pkt.timestamp = millis();          // Timestamp since boot (ms)
    for (int i = 0; i < 4; ++i)
        pkt.bin_counts[i] = random(0, 100);  // Simulated detector bins

    pkt.coincidence = random(0, 10);   // Coincidence count
    pkt.flags = 0;                     // No flags set

    // Compute 16-bit CRC over packet (excluding CRC field itself)
    pkt.crc = crc16_ccitt(reinterpret_cast<uint8_t*>(&pkt), sizeof(pkt) - 2);

    // 3. Stream bytes into ingestion logic
    uint8_t *bytes = reinterpret_cast<uint8_t*>(&pkt);
    for (size_t i = 0; i < sizeof(SEEsRawPacket); i++)
        sees_ingest(bytes[i]);

    // 4. Poll parser for completed telemetry frames
    if (sees_poll()) {
        TelemetryFrame frame;
        if (sees_next_frame(frame)) {
            // Interpret payload as SEEsRawPacket
            auto *decoded = reinterpret_cast<SEEsRawPacket*>(frame.payload);

            // 5. Display decoded data
            Serial.printf("%lu | %u %u %u %u | Coinc: %u | Flags: %u\n",
                          (unsigned long)decoded->timestamp,
                          decoded->bin_counts[0], decoded->bin_counts[1],
                          decoded->bin_counts[2], decoded->bin_counts[3],
                          decoded->coincidence, decoded->flags);
        }
    }
}

}  // namespace SEEs