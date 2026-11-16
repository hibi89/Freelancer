@echo off
setlocal
cd /d "%~dp0"
if not defined AXDEV_MODEL set "AXDEV_MODEL=ollama/qwen3:4b-instruct"
call "%~dp0RUN_PREFLIGHT.cmd"
if errorlevel 1 (echo Missing model runtime. No inference launched. & exit /b 2)
python -m scripts.benchmark_local --model "%AXDEV_MODEL%" --execute
exit /b %errorlevel%
