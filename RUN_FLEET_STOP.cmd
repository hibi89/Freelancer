@echo off
setlocal
cd /d "%~dp0"
python -m scripts.fleet stop
exit /b %errorlevel%
