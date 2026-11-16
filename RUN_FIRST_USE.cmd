@echo off
setlocal
cd /d "%~dp0"
set "TRIAL=%USERPROFILE%\AXDEV_TRIAL"
if not exist "%TRIAL%\trial-plan.json" (
  if exist "%TRIAL%" (
    echo Refusing to use an existing unknown trial directory: %TRIAL%
    exit /b 2
  )
  call "%~dp0RUN_TRIAL.cmd"
  if errorlevel 1 exit /b 2
)
if not exist "%TRIAL%\trial-repo\.git" (
  echo Expected synthetic Git fixture is missing. No model started.
  exit /b 2
)
call "%~dp0RUN_PREFLIGHT.cmd"
if errorlevel 1 (
  echo Local runtime not ready. No model started. Check the read-only report.
  exit /b 2
)
echo One approved synthetic model-coding task will run now.
echo No real project, GitHub publication, dependency install or model download.
call "%~dp0RUN_MODEL_TRIAL.cmd"
if errorlevel 1 (
  echo Local model trial did not pass. Inspect console output before retry.
  python -m scripts.first_use_evidence --trial "%TRIAL%"
  exit /b 2
)
python -m scripts.first_use_evidence --trial "%TRIAL%"
if errorlevel 1 exit /b 2
echo Synthetic trial completed; actual permission/network isolation not proven.
exit /b 0
