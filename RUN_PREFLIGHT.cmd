@echo off
setlocal
cd /d "%~dp0"
if not defined AXDEV_MODEL set "AXDEV_MODEL=ollama/qwen3:4b-instruct"
python -m scripts.preflight --model "%AXDEV_MODEL%"
exit /b %errorlevel%
