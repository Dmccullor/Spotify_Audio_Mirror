@echo off
REM Change to the directory where this BAT file is located
cd /d "%~dp0"

:loop
python sound_route.py
echo Script exited with %ERRORLEVEL% at %DATE% %TIME% >> sound_route.log
timeout /t 5
goto loop