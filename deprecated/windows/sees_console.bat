@echo off
REM SEEs Console with Basic Logging (Windows)
REM
REM Simple serial monitor with session logging
REM For full features (trigger capture), use SEEs.bat instead
REM
REM Usage: sees_console.bat [port]
REM        Default port: COM3

setlocal enabledelayedexpansion

REM Set default port if not provided
if "%~1"=="" (
    set PORT=COM3
) else (
    set PORT=%~1
)

REM Create session directory
set BASE_DIR=%USERPROFILE%\sees_outputlogs
set SESSION_TIMESTAMP=%DATE:~-4%%DATE:~-10,2%%DATE:~-7,2%.%TIME:~0,2%%TIME:~3,2%
set SESSION_TIMESTAMP=%SESSION_TIMESTAMP: =0%
set SESSION_DIR=%BASE_DIR%\%SESSION_TIMESTAMP%
set LOGFILE=%SESSION_DIR%\SEEs.%SESSION_TIMESTAMP%.log

if not exist "%SESSION_DIR%" mkdir "%SESSION_DIR%"

echo ===================================================
echo   SEEs Console with Automatic Logging
echo ===================================================
echo   Port:         %PORT%
echo   Session dir:  %SESSION_DIR%
echo   Log file:     SEEs.%SESSION_TIMESTAMP%.log
echo ===================================================
echo.
echo WARNING: This is basic logging only
echo          For trigger capture, use: SEEs.bat
echo.
echo Starting Python serial monitor...
echo Press Ctrl+C to exit
echo.

REM Use Python to create a simple serial monitor with logging
python -c "import serial, sys, datetime; ser = serial.Serial('%PORT%', 115200, timeout=0.1); logfile = open(r'%LOGFILE%', 'w', buffering=1); print('Connected to %PORT%'); [print(line.decode('utf-8', errors='ignore'), end='') or logfile.write(line.decode('utf-8', errors='ignore')) or sys.stdout.flush() for line in iter(lambda: ser.readline(), b'')]"

if errorlevel 1 (
    echo.
    echo Error: Connection failed
    echo.
    echo Troubleshooting:
    echo 1. Check that the Teensy is connected
    echo 2. Verify the COM port in Device Manager
    echo 3. Try a different port: sees_console.bat COM4
    echo 4. Install pyserial: pip install pyserial
    echo.
    pause
)

endlocal
