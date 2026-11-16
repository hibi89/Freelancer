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
echo Using local model: %AXDEV_MODEL%
echo This command modifies only a synthetic disposable Git worktree under %TRIAL%.
echo OpenCode tool permissions are not a full OS sandbox. Keep credentials closed.
ollama list
python -m axdev run --repo "%TRIAL%\trial-repo" --plan "%TRIAL%\trial-plan.json" --state "%TRIAL%\state" --model "%AXDEV_MODEL%" --max-tasks 1 --execute
if errorlevel 1 (
 echo AX Dev Factory reported a failure or HOLD. Inspect the JSON status above.
 exit /b 2
)
echo Synthetic local-model trial complete. Verify result status in the JSON above.
exit /b 0
