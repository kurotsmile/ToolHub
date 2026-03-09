@echo off
setlocal
cd /d "%~dp0"

where pyw >nul 2>&1
if %errorlevel%==0 (
    pyw -3 hub.py
    exit /b 0
)

where pythonw >nul 2>&1
if %errorlevel%==0 (
    pythonw hub.py
    exit /b 0
)

where py >nul 2>&1
if %errorlevel%==0 (
    py -3 hub.py
) else (
    python hub.py
)

endlocal
