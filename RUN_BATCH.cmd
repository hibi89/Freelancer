@echo off
setlocal
cd /d "%~dp0"
if not exist "%LOCALAPPDATA%\AXDevFactory\settings.json" (
  echo No approved local queue configuration.
  echo Run python -m scripts.configure_queue --repo PATH --plan PATH first.
  exit /b 2
)
python -m scripts.run_configured_queue --implementation-batch --execute
exit /b %errorlevel%
