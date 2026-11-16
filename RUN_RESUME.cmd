@echo off
setlocal
cd /d "%~dp0"
python -m scripts.queue_control resume --confirm
exit /b %errorlevel%
