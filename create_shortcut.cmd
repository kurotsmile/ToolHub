@echo off
setlocal
cd /d "%~dp0"

set "BASE=%~dp0"
if "%BASE:~-1%"=="\" set "BASE=%BASE:~0,-1%"

set "TARGET="
set "ARGS="
set "RUN_CMD=%BASE%\run_hub.cmd"
set "ICON=%BASE%\toolhub.ico"

if not exist "%BASE%\hub.py" (
  echo [ERROR] Cannot find file: %BASE%\hub.py
  exit /b 1
)

where pyw >nul 2>&1
if %errorlevel%==0 (
  set "TARGET=pyw"
  set "ARGS=-3 \"%BASE%\hub.py\""
) else (
  where pythonw >nul 2>&1
  if %errorlevel%==0 (
    set "TARGET=pythonw"
    set "ARGS=\"%BASE%\hub.py\""
  ) else (
    if not exist "%RUN_CMD%" (
      echo [ERROR] Cannot find fallback run file: %RUN_CMD%
      exit /b 1
    )
    set "TARGET=%RUN_CMD%"
    set "ARGS="
  )
)

for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP_DIR=%%D"
for /f "usebackq delims=" %%S in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Programs')"`) do set "STARTMENU_DIR=%%S"

if not defined DESKTOP_DIR set "DESKTOP_DIR=%USERPROFILE%\Desktop"
if not defined STARTMENU_DIR set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs"

if not defined DESKTOP_DIR (
  echo [ERROR] Cannot resolve Desktop path.
  exit /b 1
)

if not defined STARTMENU_DIR (
  echo [ERROR] Cannot resolve Start Menu Programs path.
  exit /b 1
)

set "DESKTOP_LNK=%DESKTOP_DIR%\ToolHub.lnk"
set "STARTMENU_LNK=%STARTMENU_DIR%\ToolHub.lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; function New-Link([string]$path){ $s = $ws.CreateShortcut($path); $s.TargetPath = '%TARGET%'; if ('%ARGS%' -ne '') { $s.Arguments = '%ARGS%' }; $s.WorkingDirectory = '%BASE%'; if (Test-Path '%ICON%') { $s.IconLocation = '%ICON%' }; $s.Description = 'ToolHub launcher'; $s.Save() }; New-Link '%DESKTOP_LNK%'; New-Link '%STARTMENU_LNK%'"

if exist "%DESKTOP_LNK%" (
  echo [OK] Desktop shortcut: %DESKTOP_LNK%
) else (
  echo [WARN] Desktop shortcut was not created.
)

if exist "%STARTMENU_LNK%" (
  echo [OK] Start Menu shortcut: %STARTMENU_LNK%
) else (
  echo [WARN] Start Menu shortcut was not created.
)

exit /b 0
