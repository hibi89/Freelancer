@echo off
setlocal
cd /d "%~dp0"
set "TRIAL=%USERPROFILE%\AXDEV_TRIAL"
if not exist "%TRIAL%\trial-plan.json" (
  if exist "%TRIAL%" (
    echo Refusing an existing unknown trial directory.
    exit /b 2
  )
  call "%~dp0RUN_TRIAL.cmd"
  if errorlevel 1 exit /b 2
)
if not exist "%TRIAL%\trial-repo\.git" (
  echo Expected synthetic Git fixture missing; no model started.
  exit /b 2
)
python -m scripts.verify_trial --phase ready --trial "%TRIAL%"
if errorlevel 1 (
  echo Trial already started or fixture changed. No model called.
  exit /b 2
)
call "%~dp0RUN_MODEL_TRIAL.cmd"
if errorlevel 1 (
  echo Local model trial failed or was held. Review evidence before retrying.
  python -m scripts.first_use_evidence --trial "%TRIAL%"
  exit /b 2
)
python -m scripts.verify_trial --phase completed --trial "%TRIAL%"
if errorlevel 1 (
  echo No independent VERIFIED synthetic commit; success cannot be claimed.
  exit /b 2
)
python -m scripts.first_use_evidence --trial "%TRIAL%"
if errorlevel 1 exit /b 2
echo Independently VERIFIED synthetic task. Model identity and OS sandbox unverified.
exit /b 0
