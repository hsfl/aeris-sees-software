/**
 * @file Arduino.h
 * @brief Arduino compatibility shim for native Linux builds
 *
 * Provides minimal Arduino API for running SEEs firmware on Linux.
 * Used for simulation testing without Teensy hardware.
 */

#ifndef ARDUINO_H
#define ARDUINO_H

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <chrono>
#include <thread>
#include <new>

// Arduino type aliases
using byte = uint8_t;

// Pin definitions (no-ops on Linux)
#define A0 0
#define BUILTIN_SDCARD 0
#define INPUT 0
#define OUTPUT 1
#define HIGH 1
#define LOW 0

// Timing functions
inline uint32_t millis() {
    static auto start = std::chrono::steady_clock::now();
    auto now = std::chrono::steady_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(now - start).count();
}

inline uint32_t micros() {
    static auto start = std::chrono::steady_clock::now();
    auto now = std::chrono::steady_clock::now();
    return std::chrono::duration_cast<std::chrono::microseconds>(now - start).count();
}

inline void delay(uint32_t ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

inline void delayMicroseconds(uint32_t us) {
    std::this_thread::sleep_for(std::chrono::microseconds(us));
}

// Pin functions (no-ops)
inline void pinMode(uint8_t, uint8_t) {}
inline void digitalWrite(uint8_t, uint8_t) {}
inline int digitalRead(uint8_t) { return 0; }

// ADC functions - these will be overridden by simulation
inline void analogReadResolution(int) {}
inline void analogReadAveraging(int) {}

// Forward declaration - implemented in main_native.cpp
int analogRead(uint8_t pin);

/**
 * @brief Arduino String class compatibility
 */
class String {
public:
    String() : _str() {}
    String(const char* s) : _str(s ? s : "") {}
    String(const String& s) : _str(s._str) {}  // Copy constructor
    String(const std::string& s) : _str(s) {}
    String(int val) : _str(std::to_string(val)) {}
    String(unsigned int val) : _str(std::to_string(val)) {}
    String(long val) : _str(std::to_string(val)) {}
    String(unsigned long val) : _str(std::to_string(val)) {}
    String(float val, int decimals = 2) {
        char buf[32];
        snprintf(buf, sizeof(buf), "%.*f", decimals, val);
        _str = buf;
    }
    String(double val, int decimals = 2) {
        char buf[32];
        snprintf(buf, sizeof(buf), "%.*f", decimals, val);
        _str = buf;
    }

    const char* c_str() const { return _str.c_str(); }
    size_t length() const { return _str.length(); }
    bool isEmpty() const { return _str.empty(); }

    void trim() {
        size_t start = _str.find_first_not_of(" \t\r\n");
        size_t end = _str.find_last_not_of(" \t\r\n");
        if (start == std::string::npos) {
            _str.clear();
        } else {
            _str = _str.substr(start, end - start + 1);
        }
    }

    void toLowerCase() {
        for (auto& c : _str) c = tolower(c);
    }

    String& operator=(const char* s) { _str = s ? s : ""; return *this; }
    String& operator=(const String& s) { _str = s._str; return *this; }
    String operator+(const String& s) const { return String(_str + s._str); }
    String operator+(const char* s) const { return String(_str + (s ? s : "")); }
    bool operator==(const char* s) const { return _str == (s ? s : ""); }
    bool operator==(const String& s) const { return _str == s._str; }
    bool operator!=(const char* s) const { return !(*this == s); }
    char operator[](size_t i) const { return _str[i]; }

private:
    std::string _str;
};

/**
 * @brief Arduino Serial class compatibility
 */
class SerialClass {
public:
    void begin(unsigned long) {}

    void print(const char* s) { printf("%s", s); }
    void print(const String& s) { printf("%s", s.c_str()); }
    void print(int val) { printf("%d", val); }
    void print(unsigned int val) { printf("%u", val); }
    void print(long val) { printf("%ld", val); }
    void print(unsigned long val) { printf("%lu", val); }
    void print(float val, int decimals = 2) { printf("%.*f", decimals, val); }
    void print(double val, int decimals = 2) { printf("%.*f", decimals, val); }
    void print(char c) { printf("%c", c); }

    void println() { printf("\n"); fflush(stdout); }
    void println(const char* s) { printf("%s\n", s); fflush(stdout); }
    void println(const String& s) { printf("%s\n", s.c_str()); fflush(stdout); }
    void println(int val) { printf("%d\n", val); fflush(stdout); }
    void println(unsigned int val) { printf("%u\n", val); fflush(stdout); }
    void println(long val) { printf("%ld\n", val); fflush(stdout); }
    void println(unsigned long val) { printf("%lu\n", val); fflush(stdout); }
    void println(float val, int decimals = 2) { printf("%.*f\n", decimals, val); fflush(stdout); }
    void println(double val, int decimals = 2) { printf("%.*f\n", decimals, val); fflush(stdout); }

    // Input functions - implemented in main_native.cpp
    bool available();
    String readStringUntil(char terminator);
};

extern SerialClass Serial;

#endif // ARDUINO_H
