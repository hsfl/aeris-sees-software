@echo off
REM SEEs Unified Console (Windows)
REM
REM Interactive console with automatic session logging and trigger capture
REM All data automatically saved to timestamped session folders
REM
REM Usage: SEEs.bat [port]
REM        Default port: COM3

setlocal

REM Set default port if not provided
if "%~1"=="" (
    set PORT=COM3
) else (
    set PORT=%~1
)

echo Starting SEEs Interactive Console...
echo Port: %PORT%
echo.

REM Run the interactive Python script
python scripts\sees_interactive.py %PORT%

if errorlevel 1 (
    echo.
    echo Error: Failed to start Python script
    echo Make sure Python 3 is installed and pyserial is available
    echo.
    echo Install pyserial with: pip install pyserial
    echo.
    pause
)

endlocal
