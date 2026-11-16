@echo off
setlocal
cd /d "%~dp0"
python -m scripts.fleet status
exit /b %errorlevel%
