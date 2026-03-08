@echo off
setlocal
cd /d "%~dp0"

set "TARGET=%~dp0run_hub.cmd"
set "ICON=%~dp0toolhub.ico"
set "SHORTCUT=%~dp0ToolHub.lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath='%TARGET%'; $s.WorkingDirectory='%~dp0'; if (Test-Path '%ICON%') { $s.IconLocation='%ICON%' }; $s.Description='ToolHub launcher'; $s.Save()"

if exist "%SHORTCUT%" (
    echo Shortcut created: %SHORTCUT%
) else (
    echo Failed to create shortcut.
)

endlocal
