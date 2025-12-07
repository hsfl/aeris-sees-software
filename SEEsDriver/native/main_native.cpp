/**
 * @file main_native.cpp
 * @brief Native Linux entry point for SEEs firmware simulation
 *
 * Reads simulated ADC data from a virtual serial port (stdin or file)
 * and runs the real firmware logic. This allows testing the full
 * firmware behavior without Teensy hardware.
 *
 * Usage:
 *   ./sees_native < /tmp/tty_sees
 *   cat test_data.csv | ./sees_native
 *
 * The virtual_serial_port.py creates /tmp/tty_sees with simulated data.
 */

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <queue>
#include <mutex>
#include <thread>
#include <atomic>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <poll.h>
#include <signal.h>

// Include Arduino shim first
#include "Arduino.h"
#include "SD.h"

// Include firmware components
#include "../src/CircularBuffer.hpp"
#include "../src/SnapManager.hpp"

// Global instances required by shims
SerialClass Serial;
SDClass SD;

// Simulation state
static std::queue<std::string> g_inputLines;
static std::mutex g_inputMutex;
static std::atomic<bool> g_running(true);
static std::atomic<float> g_currentVoltage(0.0f);
static int g_dataFd = -1;

// Signal handler for clean shutdown
void signalHandler(int) {
    g_running = false;
}

/**
 * @brief Background thread to read data from virtual serial port
 */
void dataReaderThread(const char* dataPort) {
    // Open data port (virtual serial port with ADC data)
    g_dataFd = open(dataPort, O_RDONLY | O_NONBLOCK);
    if (g_dataFd < 0) {
        fprintf(stderr, "[Native] ERROR: Cannot open data port: %s\n", dataPort);
        g_running = false;
        return;
    }

    fprintf(stderr, "[Native] Data port opened: %s\n", dataPort);

    char buffer[4096];
    std::string lineBuffer;

    while (g_running) {
        struct pollfd pfd = { g_dataFd, POLLIN, 0 };
        int ret = poll(&pfd, 1, 100);  // 100ms timeout

        if (ret > 0 && (pfd.revents & POLLIN)) {
            ssize_t n = read(g_dataFd, buffer, sizeof(buffer) - 1);
            if (n > 0) {
                buffer[n] = '\0';
                lineBuffer += buffer;

                // Process complete lines
                size_t pos;
                while ((pos = lineBuffer.find('\n')) != std::string::npos) {
                    std::string line = lineBuffer.substr(0, pos);
                    lineBuffer = lineBuffer.substr(pos + 1);

                    // Remove CR if present
                    if (!line.empty() && line.back() == '\r') {
                        line.pop_back();
                    }

                    // Parse voltage from CSV: time_ms,voltage_V,hit,total_hits
                    float time_ms, voltage;
                    int hit, total;
                    if (sscanf(line.c_str(), "%f,%f,%d,%d", &time_ms, &voltage, &hit, &total) == 4) {
                        g_currentVoltage = voltage;
                    }
                }
            } else if (n == 0) {
                // EOF - data source closed
                fprintf(stderr, "[Native] Data source closed\n");
                break;
            }
        }
    }

    if (g_dataFd >= 0) {
        close(g_dataFd);
    }
}

/**
 * @brief analogRead implementation - returns voltage as ADC counts
 *
 * Converts the current voltage from the data stream to ADC counts.
 */
int analogRead(uint8_t) {
    // Convert voltage to 12-bit ADC counts (0-4095 for 0-3.3V)
    float voltage = g_currentVoltage;
    int counts = (int)((voltage / 3.3f) * 4095.0f);
    if (counts < 0) counts = 0;
    if (counts > 4095) counts = 4095;
    return counts;
}

// Buffer for accumulating stdin input until newline
static std::string g_inputBuffer;

/**
 * @brief Serial.available() - check if a complete line is ready
 */
bool SerialClass::available() {
    // Read any available data into buffer
    struct pollfd pfd = { STDIN_FILENO, POLLIN, 0 };
    while (poll(&pfd, 1, 0) > 0) {
        char c;
        if (read(STDIN_FILENO, &c, 1) == 1) {
            g_inputBuffer += c;
        } else {
            break;
        }
    }
    // Return true only if we have a complete line
    return g_inputBuffer.find('\n') != std::string::npos;
}

/**
 * @brief Serial.readStringUntil() - read command from buffer
 */
String SerialClass::readStringUntil(char terminator) {
    size_t pos = g_inputBuffer.find(terminator);
    if (pos == std::string::npos) {
        return String("");
    }
    std::string result = g_inputBuffer.substr(0, pos);
    g_inputBuffer.erase(0, pos + 1);
    return String(result.c_str());
}

// ============================================================================
// Include firmware source files directly (simpler than separate compilation)
// ============================================================================
#include "../src/CircularBuffer.cpp"
#include "../src/SnapManager.cpp"

// ============================================================================
// Native version of SEEs_ADC (modified to use simulated data)
// ============================================================================

class SEEs_ADC_Native {
public:
    SEEs_ADC_Native() :
        _isCollecting(false), _sdAvailable(false), _armed(true), _ledState(false),
        _t0_us(0), _next_sample_us(0), _lastBlink(0), _last_hit_us(0),
        _totalHits(0), _countsPerVolt(0) {}

    void begin() {
        Serial.println("[SEEs] ====================================");
        Serial.println("[SEEs] SEEs Particle Detector - NATIVE SIM");
        Serial.println("[SEEs] ====================================");

        _sdAvailable = SD.begin(0);
        if (_sdAvailable) {
            Serial.println("[SEEs] SD simulation ready (local files)");
        }

        Serial.println("[SEEs] Initializing circular buffer...");
        if (!_circularBuffer.begin()) {
            Serial.println("[SEEs] ERROR: Failed to initialize circular buffer!");
            exit(1);
        }

        _snapManager.begin(_sdAvailable);

        Serial.println("[SEEs] Body cam mode: ALWAYS streaming");
        Serial.println("[SEEs] Commands: snap");
        Serial.println("[SEEs] Data format: time_ms,voltage_V,hit,total_hits");

        _next_sample_us = micros();
        _lastBlink = millis();
        _t0_us = micros();
        _countsPerVolt = 3.3f / 4095.0f;

        Serial.println("[SEEs] ====================================");
        Serial.println("[SEEs] Ready - buffer recording started");
        Serial.println("[SEEs] ====================================");
    }

    void update() {
        // Check for serial commands
        if (Serial.available()) {
            String cmd = Serial.readStringUntil('\n');
            processCommand(cmd);
        }

        // ALWAYS sample (body cam mode)
        sampleAndStream();
    }

    void processCommand(const String& cmd) {
        String cmdLower = cmd;
        cmdLower.trim();
        cmdLower.toLowerCase();

        if (cmdLower == "snap") {
            Serial.println("[SEEs] SNAP command received");
            Serial.println("[SEEs] Waiting 2.5s for post-trigger data...");
            uint32_t snapTime = micros();

            delay(2500);

            if (_snapManager.captureSnap(_circularBuffer, snapTime)) {
                Serial.print("[SEEs] Snap captured! Total snaps: ");
                Serial.println(_snapManager.getSnapCount());
            } else {
                Serial.println("[SEEs] ERROR: Failed to capture snap");
            }
        }
        else if (cmdLower.length() > 0) {
            Serial.print("[SEEs] Unknown command: ");
            Serial.println(cmd);
        }
    }

private:
    static constexpr uint32_t SAMPLE_US = 100;       // 10 kS/s
    static constexpr float LOWER_ENTER_V = 0.30f;
    static constexpr float LOWER_EXIT_V = 0.300f;
    static constexpr float UPPER_LIMIT_V = 0.800f;
    static constexpr uint32_t REFRACT_US = 300;

    bool _isCollecting;
    bool _sdAvailable;
    bool _armed;
    bool _ledState;

    uint32_t _t0_us;
    uint32_t _next_sample_us;
    uint32_t _lastBlink;
    uint32_t _last_hit_us;
    uint32_t _totalHits;
    float _countsPerVolt;

    CircularBuffer _circularBuffer;
    SnapManager _snapManager;

    void sampleAndStream() {
        uint32_t now_us = micros();
        if ((int32_t)(now_us - _next_sample_us) < 0) return;
        _next_sample_us += SAMPLE_US;

        // Read "ADC" (actually from data stream)
        int raw = analogRead(0);
        float v = raw * _countsPerVolt;

        // Windowed detection with hysteresis + refractory
        uint8_t hit = 0;
        if (_armed) {
            if (v >= LOWER_ENTER_V && v <= UPPER_LIMIT_V &&
                (now_us - _last_hit_us) >= REFRACT_US) {
                hit = 1;
                ++_totalHits;
                _last_hit_us = now_us;
                _armed = false;
            }
        } else {
            if (v < LOWER_EXIT_V) {
                _armed = true;
            }
        }

        float t_ms = (now_us - _t0_us) / 1000.0f;

        // Record hit to circular buffer
        if (hit) {
            _circularBuffer.recordHit(now_us, 1);
        }

        // Stream to "Serial" (stdout)
        Serial.print(t_ms, 3); Serial.print(',');
        Serial.print(v, 4);    Serial.print(',');
        Serial.print(hit);     Serial.print(',');
        Serial.println(_totalHits);
    }
};

// ============================================================================
// Main
// ============================================================================

void printUsage(const char* prog) {
    fprintf(stderr, "SEEs Native Firmware Simulation\n");
    fprintf(stderr, "\n");
    fprintf(stderr, "Usage: %s <data_port>\n", prog);
    fprintf(stderr, "\n");
    fprintf(stderr, "  data_port: Virtual serial port with ADC data (e.g., /tmp/tty_sees)\n");
    fprintf(stderr, "\n");
    fprintf(stderr, "Commands are read from stdin (type 'snap' + Enter)\n");
    fprintf(stderr, "Output goes to stdout (pipe to sees_interactive.py)\n");
    fprintf(stderr, "\n");
    fprintf(stderr, "Example:\n");
    fprintf(stderr, "  # Terminal 1: Start data source\n");
    fprintf(stderr, "  python3 virtual_serial_port.py\n");
    fprintf(stderr, "\n");
    fprintf(stderr, "  # Terminal 2: Run native firmware\n");
    fprintf(stderr, "  %s /tmp/tty_sees\n", prog);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printUsage(argv[0]);
        return 1;
    }

    const char* dataPort = argv[1];

    // Set up signal handlers
    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);

    // Make stdin non-blocking for command input
    int flags = fcntl(STDIN_FILENO, F_GETFL, 0);
    fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK);

    // Start data reader thread
    std::thread readerThread(dataReaderThread, dataPort);

    // Wait a moment for data port to open
    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    if (!g_running) {
        fprintf(stderr, "[Native] Failed to start - data port error\n");
        readerThread.join();
        return 1;
    }

    // Run firmware
    SEEs_ADC_Native sees;
    sees.begin();

    while (g_running) {
        sees.update();
        // Small sleep to prevent busy-waiting
        std::this_thread::sleep_for(std::chrono::microseconds(50));
    }

    fprintf(stderr, "\n[Native] Shutting down...\n");
    readerThread.join();

    return 0;
}
