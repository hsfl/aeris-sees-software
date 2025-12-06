/**
 * @file SD.h
 * @brief SD card compatibility shim for native Linux builds
 *
 * Provides minimal SD card API using Linux filesystem.
 * Files are written to a local directory instead of SD card.
 */

#ifndef SD_H
#define SD_H

#include "Arduino.h"
#include <cstdio>
#include <cerrno>
#include <sys/stat.h>

#define FILE_WRITE 1
#define FILE_READ 0

/**
 * @brief Arduino File class compatibility
 */
class File {
public:
    File() : _fp(nullptr) {}
    File(FILE* fp) : _fp(fp) {}

    explicit operator bool() const { return _fp != nullptr; }

    void print(const char* s) { if (_fp) fprintf(_fp, "%s", s); }
    void print(const String& s) { if (_fp) fprintf(_fp, "%s", s.c_str()); }
    void print(int val) { if (_fp) fprintf(_fp, "%d", val); }
    void print(unsigned int val) { if (_fp) fprintf(_fp, "%u", val); }
    void print(long val) { if (_fp) fprintf(_fp, "%ld", val); }
    void print(unsigned long val) { if (_fp) fprintf(_fp, "%lu", val); }
    void print(float val, int decimals = 2) { if (_fp) fprintf(_fp, "%.*f", decimals, val); }
    void print(double val, int decimals = 2) { if (_fp) fprintf(_fp, "%.*f", decimals, val); }
    void print(char c) { if (_fp) fprintf(_fp, "%c", c); }

    void println() { if (_fp) fprintf(_fp, "\n"); }
    void println(const char* s) { if (_fp) fprintf(_fp, "%s\n", s); }
    void println(const String& s) { if (_fp) fprintf(_fp, "%s\n", s.c_str()); }
    void println(int val) { if (_fp) fprintf(_fp, "%d\n", val); }
    void println(unsigned int val) { if (_fp) fprintf(_fp, "%u\n", val); }
    void println(long val) { if (_fp) fprintf(_fp, "%ld\n", val); }
    void println(unsigned long val) { if (_fp) fprintf(_fp, "%lu\n", val); }
    void println(float val, int decimals = 2) { if (_fp) fprintf(_fp, "%.*f\n", decimals, val); }

    void flush() { if (_fp) fflush(_fp); }
    void close() { if (_fp) { fclose(_fp); _fp = nullptr; } }

    size_t write(uint8_t c) { return _fp ? fwrite(&c, 1, 1, _fp) : 0; }
    size_t write(const uint8_t* buf, size_t size) { return _fp ? fwrite(buf, 1, size, _fp) : 0; }

private:
    FILE* _fp;
};

/**
 * @brief Arduino SD class compatibility
 */
class SDClass {
public:
    bool begin(int = 0) {
        // Create output directory using global mkdir
        ::mkdir("snaps", 0755);
        return true;
    }

    bool exists(const char* path) {
        struct stat st;
        return stat(path, &st) == 0;
    }

    bool mkdir(const char* path) {
        return ::mkdir(path, 0755) == 0 || errno == EEXIST;
    }

    File open(const char* path, int mode = FILE_READ) {
        const char* fmode = (mode == FILE_WRITE) ? "w" : "r";
        FILE* fp = fopen(path, fmode);
        return File(fp);
    }

    bool remove(const char* path) {
        return ::remove(path) == 0;
    }
};

extern SDClass SD;

#endif // SD_H
