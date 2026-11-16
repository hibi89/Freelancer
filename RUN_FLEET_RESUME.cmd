@echo off
setlocal
cd /d "%~dp0"
python -m scripts.fleet resume --confirm
exit /b %errorlevel%
