# Makefile for SEEs Native Linux Build
#
# Builds the firmware for Linux simulation testing.
# The native binary reads ADC data from a virtual serial port.
#
# Cross-compilation for ARM64 (Pi 400):
#   make CXX=aarch64-linux-gnu-g++ TARGET=sees_native_arm64

CXX ?= g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2 -pthread
INCLUDES = -I. -I../src

TARGET ?= sees_native
SOURCES = main_native.cpp

.PHONY: all clean install

all: $(TARGET)

$(TARGET): $(SOURCES) Arduino.h SD.h ../src/*.hpp ../src/*.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $(TARGET) $(SOURCES)

clean:
	rm -f sees_native sees_native_x64 sees_native_arm64

install: $(TARGET)
	mkdir -p $(HOME)/Aeris/bin
	cp $(TARGET) $(HOME)/Aeris/bin/
	@echo "Installed to $(HOME)/Aeris/bin/$(TARGET)"
