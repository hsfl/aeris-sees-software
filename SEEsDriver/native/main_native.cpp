/**
 * @file main_native.cpp
 * @brief Native Linux entry point for SEEs firmware simulation
 *
 * Provides Arduino-compatible shims and a main() that runs the ACTUAL
 * SEEs_ADC firmware code. The only difference from Teensy is:
 * - analogRead() returns simulated data from virtual serial port
 * - Serial output goes to stdout
 * - Serial input comes from stdin
 *
 * This ensures the simulation tests the EXACT SAME firmware code
 * that runs on the Teensy hardware.
 */

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>
#include <atomic>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <signal.h>

// Include Arduino shim first (provides Serial, millis, micros, etc.)
#include "Arduino.h"

// Global instances required by shims
SerialClass Serial;

// Simulation state
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
        int ret = poll(&pfd, 1, 100);

        if (ret > 0 && (pfd.revents & POLLIN)) {
            ssize_t n = read(g_dataFd, buffer, sizeof(buffer) - 1);
            if (n > 0) {
                buffer[n] = '\0';
                lineBuffer += buffer;

                size_t pos;
                while ((pos = lineBuffer.find('\n')) != std::string::npos) {
                    std::string line = lineBuffer.substr(0, pos);
                    lineBuffer = lineBuffer.substr(pos + 1);

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
 * @brief analogRead() - returns simulated ADC counts from data stream
 */
int analogRead(uint8_t) {
    float voltage = g_currentVoltage;
    int counts = (int)((voltage / 3.3f) * 4095.0f);
    if (counts < 0) counts = 0;
    if (counts > 4095) counts = 4095;
    return counts;
}

// Buffer for stdin command input
static std::string g_inputBuffer;

/**
 * @brief Serial.available() - check if complete line ready on stdin
 */
bool SerialClass::available() {
    struct pollfd pfd = { STDIN_FILENO, POLLIN, 0 };
    while (poll(&pfd, 1, 0) > 0) {
        char c;
        if (read(STDIN_FILENO, &c, 1) == 1) {
            g_inputBuffer += c;
        } else {
            break;
        }
    }
    return g_inputBuffer.find('\n') != std::string::npos;
}

/**
 * @brief Serial.readStringUntil() - read command from stdin buffer
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
// Include the ACTUAL firmware source files
// ============================================================================
#include "../src/SampleBuffer.hpp"
#include "../src/SEEs_ADC.hpp"
#include "../src/SEEs_ADC.cpp"

// ============================================================================
// Main - runs the real firmware
// ============================================================================

void printUsage(const char* prog) {
    fprintf(stderr, "SEEs Native Firmware Simulation\n\n");
    fprintf(stderr, "Usage: %s <data_port>\n\n", prog);
    fprintf(stderr, "  data_port: Virtual serial port with ADC data (e.g., /tmp/tty_sees)\n\n");
    fprintf(stderr, "Commands from stdin, output to stdout.\n\n");
    fprintf(stderr, "Example:\n");
    fprintf(stderr, "  python3 virtual_serial_port.py &\n");
    fprintf(stderr, "  %s /tmp/tty_sees\n", prog);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printUsage(argv[0]);
        return 1;
    }

    const char* dataPort = argv[1];

    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);

    // Make stdin non-blocking
    int flags = fcntl(STDIN_FILENO, F_GETFL, 0);
    fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK);

    // Start data reader thread
    std::thread readerThread(dataReaderThread, dataPort);

    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    if (!g_running) {
        fprintf(stderr, "[Native] Failed to start - data port error\n");
        readerThread.join();
        return 1;
    }

    // Run the ACTUAL firmware
    SEEs_ADC sees;
    sees.begin();

    while (g_running) {
        sees.update();
        std::this_thread::sleep_for(std::chrono::microseconds(50));
    }

    fprintf(stderr, "\n[Native] Shutting down...\n");
    readerThread.join();

    return 0;
}
