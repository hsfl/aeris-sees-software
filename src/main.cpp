#include <Arduino.h>
#include "SEEs_Interface.hpp"

void setup() {
    pinMode(13, OUTPUT);
    Serial.begin(115200);
    delay(2000);
    Serial.println("SEEs Integration test starting...");
}

void loop() {
    digitalWrite(13, !digitalRead(13));  // blink heartbeat
    delay(500);

    // Fake a packet for test
    SEEsRawPacket pkt{};
    pkt.timestamp = millis();
    pkt.bin_counts[0] = random(0, 100);
    pkt.bin_counts[1] = random(0, 100);
    pkt.bin_counts[2] = random(0, 100);
    pkt.bin_counts[3] = random(0, 100);
    pkt.coincidence   = random(0, 10);
    pkt.flags         = 0;
    pkt.crc = crc16_ccitt((uint8_t*)&pkt, sizeof(pkt) - 2);

    uint8_t *bytes = (uint8_t*)&pkt;
    for (size_t i = 0; i < sizeof(SEEsRawPacket); i++) {
        sees_ingest(bytes[i]);
    }

    if (sees_poll()) {
        TelemetryFrame frame;
        if (sees_next_frame(frame)) {
            auto *decoded = reinterpret_cast<SEEsRawPacket*>(frame.payload);
            Serial.printf("%lu | %u %u %u %u | Coinc: %u | Flags: %u\n",
                          (unsigned long)decoded->timestamp,
                          decoded->bin_counts[0], decoded->bin_counts[1],
                          decoded->bin_counts[2], decoded->bin_counts[3],
                          decoded->coincidence, decoded->flags);
        }
    }
}