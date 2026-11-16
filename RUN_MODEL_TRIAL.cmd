@echo off
setlocal
cd /d "%~dp0"
set "TRIAL=%USERPROFILE%\AXDEV_TRIAL"
if not exist "%TRIAL%\trial-plan.json" (
  echo Synthetic trial fixture not found. Run RUN_TRIAL.cmd first.
  exit /b 2
)
where git >nul 2>&1 || (echo Git is missing. & exit /b 2)
where python >nul 2>&1 || (echo Python is missing. & exit /b 2)
where ollama >nul 2>&1 || (echo Ollama is missing. & exit /b 2)
where opencode >nul 2>&1 || (echo OpenCode V2 is missing. & exit /b 2)
if not defined AXDEV_MODEL set "AXDEV_MODEL=ollama/qwen3:4b-instruct"
python -m scripts.verify_trial --phase ready --trial "%TRIAL%"
if errorlevel 1 (
  echo Synthetic fixture already started, changed, or completed; no model invoked.
  exit /b 2
)
call "%~dp0RUN_PREFLIGHT.cmd"
if errorlevel 1 (echo Local preflight not ready. No model launched. & exit /b 2)
echo Using local model: %AXDEV_MODEL%
echo Only disposable synthetic Git worktree may be modified.
echo OpenCode permissions are not an OS sandbox. No real project secrets.
python -m axdev run --repo "%TRIAL%\trial-repo" --plan "%TRIAL%\trial-plan.json" --state "%TRIAL%\state" --model "%AXDEV_MODEL%" --max-tasks 1 --execute
if errorlevel 1 (
  echo AX Dev Factory reported failure or HOLD. Inspect local checkpoint.
  exit /b 2
)
python -m scripts.verify_trial --phase completed --trial "%TRIAL%"
if errorlevel 1 (
  echo Zero exit status did not establish independent VERIFIED task.
  exit /b 2
)
echo Synthetic file acceptance passed. Model and network isolation remain unverified.
exit /b 0
