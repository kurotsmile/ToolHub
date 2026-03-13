@echo off
setlocal
cd /d "%~dp0"

where pyw >nul 2>&1
if %errorlevel%==0 (
    call :set_tk_env_py
    pyw -3 hub.py
    exit /b 0
)

where pythonw >nul 2>&1
if %errorlevel%==0 (
    call :set_tk_env_python
    pythonw hub.py
    exit /b 0
)

where py >nul 2>&1
if %errorlevel%==0 (
    call :set_tk_env_py
    py -3 hub.py
) else (
    call :set_tk_env_python
    python hub.py
)

endlocal
exit /b 0

:set_tk_env_py
for /f "usebackq delims=" %%I in (`py -3 -c "import sys; print(sys.base_prefix)"`) do set "PY_BASE=%%I"
goto :set_tk_env_common

:set_tk_env_python
for /f "usebackq delims=" %%I in (`python -c "import sys; print(sys.base_prefix)"`) do set "PY_BASE=%%I"
goto :set_tk_env_common

:set_tk_env_common
if defined PY_BASE (
    if exist "%PY_BASE%\tcl\tcl8.6\init.tcl" set "TCL_LIBRARY=%PY_BASE%\tcl\tcl8.6"
    if exist "%PY_BASE%\tcl\tk8.6\tk.tcl" set "TK_LIBRARY=%PY_BASE%\tcl\tk8.6"
)
exit /b 0
