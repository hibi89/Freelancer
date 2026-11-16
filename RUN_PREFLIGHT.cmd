@echo off
setlocal
cd /d "%~dp0"
if not defined AXDEV_MODEL set "AXDEV_MODEL=ollama/qwen3:4b-instruct"
if exist "%USERPROFILE%\AXDEV_TRIAL\trial-repo\.git" (
    python -m scripts.preflight --model "%AXDEV_MODEL%" --repo "%USERPROFILE%\AXDEV_TRIAL\trial-repo"
) else (
    python -m scripts.preflight --model "%AXDEV_MODEL%"
)
exit /b %errorlevel%
