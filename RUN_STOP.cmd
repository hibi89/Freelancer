@echo off
setlocal
cd /d "%~dp0"
python -m scripts.queue_control stop
exit /b %errorlevel%
