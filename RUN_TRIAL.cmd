@echo off
setlocal
cd /d "%~dp0"
set "TRIAL=%USERPROFILE%\AXDEV_TRIAL"
if exist "%TRIAL%" (
  echo Trial directory already exists: %TRIAL%
  echo Refusing overwrite. Use a new directory with scripts\prepare_trial.py.
  exit /b 2
)
python scripts\prepare_trial.py --output "%TRIAL%"
if errorlevel 1 exit /b 1
python -m axdev doctor --plan "%TRIAL%\trial-plan.json"
if errorlevel 1 exit /b 1
python -m axdev run --repo "%TRIAL%\trial-repo" --plan "%TRIAL%\trial-plan.json" --state "%TRIAL%\state"
if errorlevel 1 exit /b 1
echo Synthetic dry-run complete. No model run, no original project changed.
echo See docs\WINDOWS_TRIAL.md for the explicit --execute test.
exit /b 0
