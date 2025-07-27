@echo off
REM Continuously monitor shutdown.txt file and execute shutdown command
REM Author: AI Assistant
REM Created: 2024

echo Starting shutdown monitoring system...
echo.

REM Start shutdown_monitor.py in background
echo Starting shutdown_monitor.py in background...
start /min python shutdown_monitor.py

echo.
echo Starting continuous monitoring of shutdown.txt file...
echo Check interval: 30 seconds
echo Press Ctrl+C to stop monitoring
echo.

:loop
REM Display current time
echo [%date% %time%] Checking for shutdown.txt file...

REM Check if shutdown.txt file exists in current directory
if exist "shutdown.txt" (
    echo.
    echo ========================================
    echo Found shutdown.txt file, preparing to shutdown...
    echo Shutdown time: %date% %time%
    echo ========================================
    
    REM Display shutdown countdown
    echo System will shutdown in 30 seconds...
    echo Press Ctrl+C to cancel shutdown
    
    REM Execute shutdown command, shutdown after 30 seconds
    shutdown /s /t 30 /c "Detected shutdown.txt file, system will shutdown"
    
    REM Delete shutdown.txt file to avoid repeated execution
    del "shutdown.txt"
    echo shutdown.txt file deleted
    echo Shutdown command executed, program exiting
    pause
    exit
) else (
    echo No shutdown.txt file found, continuing to monitor...
)

REM Wait 30 seconds before next check
ping -n 31 127.0.0.1 >nul

REM Jump to loop start
goto loop 