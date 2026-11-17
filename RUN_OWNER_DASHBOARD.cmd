@echo off
setlocal
cd /d "%~dp0"
set "AXDEV_OWNER_SETTINGS=%LOCALAPPDATA%\AXDevFactory\settings.json"
if not exist "%AXDEV_OWNER_SETTINGS%" (
  echo AXDEV_OWNER_DASHBOARD: Private queue settings do not exist.
  echo Configure an approved local queue first. No AI model has been started.
  exit /b 2
)
echo AX Dev Factory Owner Console
 echo Open this URL on this PC: http://127.0.0.1:8765/
 echo Press Ctrl+C to stop the dashboard. This does not stop the AI worker.
python -m scripts.owner_dashboard --settings "%AXDEV_OWNER_SETTINGS%" --port 8765 --confirm-local-dashboard
exit /b %ERRORLEVEL%
