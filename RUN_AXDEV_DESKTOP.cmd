@echo off
setlocal
cd /d "%~dp0"
rem AX Dev Factory: native Windows app, no HTTP server.
if exist "%~dp0dist\AXDevFactory.exe" (
  start "" "%~dp0dist\AXDevFactory.exe"
  exit /b 0
)
where py >nul 2>&1
if not errorlevel 1 (
  py -3.11 -m scripts.axdev_desktop
  exit /b %ERRORLEVEL%
)
where python >nul 2>&1
if errorlevel 1 (
  echo Python 3.11+ or a locally built AXDevFactory.exe is required.
  exit /b 2
)
python -m scripts.axdev_desktop
exit /b %ERRORLEVEL%
